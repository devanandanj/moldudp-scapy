#
# Created by devanandan : 19-08-2026
#

"""
Synthetic tests for compare/differ.py — no RTL/hardware needed.
Hand-built SnapshotEntry lists exercise: exact match, sequence
mismatch, count mismatch, level mismatch, multi-mismatch with
stop_on_first=False, and empty-book edge cases.
"""

from src.snapshot.trace_parser import TraceEntry, OrderLevel
from src.snapshot.struct_unpacker import SnapshotEntry
from src.compare.differ import diff_trace, report


def _mk_entry(msg_index, bids=None, asks=None):
    return TraceEntry(
        msg_index=msg_index, msg_type="A", order_id=0,
        accepted=True, reason="",
        bids=bids or [], asks=asks or [],
    )


def _mk_snap(sequence, bids=None, asks=None):
    return SnapshotEntry(sequence=sequence, bids=bids or [], asks=asks or [])


def _lvl(order_id, price, qty):
    return OrderLevel(order_id=order_id, price=price, quantity=qty)


# ---------------------------------------------------------------------
# 1. Exact match — should report clean MATCH
# ---------------------------------------------------------------------
def test_exact_match():
    golden = [
        _mk_entry(0, bids=[_lvl(1, 1000, 10)]),
        _mk_entry(1, bids=[_lvl(1, 1000, 10), _lvl(2, 999, 5)]),
    ]
    snaps = [
        _mk_snap(0, bids=[_lvl(1, 1000, 10)]),
        _mk_snap(1, bids=[_lvl(1, 1000, 10), _lvl(2, 999, 5)]),
    ]
    mismatches = diff_trace(golden, snaps)
    assert mismatches == [], f"expected clean match, got: {report(mismatches)}"
    print("test_exact_match: PASS")


# ---------------------------------------------------------------------
# 2. Sequence mismatch — snapshot.sequence != golden.msg_index
# ---------------------------------------------------------------------
def test_sequence_mismatch():
    golden = [_mk_entry(0, bids=[_lvl(1, 1000, 10)])]
    snaps = [_mk_snap(99, bids=[_lvl(1, 1000, 10)])]  # wrong sequence

    mismatches = diff_trace(golden, snaps)
    assert len(mismatches) == 1
    assert mismatches[0].kind == "sequence"
    assert mismatches[0].expected == 0
    assert mismatches[0].actual == 99
    print("test_sequence_mismatch: PASS")
    print(report(mismatches))


# ---------------------------------------------------------------------
# 3. Count mismatch — FPGA book has fewer/more levels than golden
# ---------------------------------------------------------------------
def test_count_mismatch():
    golden = [_mk_entry(0, bids=[_lvl(1, 1000, 10), _lvl(2, 999, 5)])]
    snaps = [_mk_snap(0, bids=[_lvl(1, 1000, 10)])]  # missing one bid level

    mismatches = diff_trace(golden, snaps)
    assert len(mismatches) == 1
    assert mismatches[0].kind == "count"
    assert mismatches[0].side == "bid"
    assert mismatches[0].expected == 2
    assert mismatches[0].actual == 1
    print("test_count_mismatch: PASS")
    print(report(mismatches))


# ---------------------------------------------------------------------
# 4. Level mismatch — same count, wrong price/qty/orderId at a level
# ---------------------------------------------------------------------
def test_level_mismatch_price():
    golden = [_mk_entry(0, bids=[_lvl(1, 1000, 10)])]
    snaps = [_mk_snap(0, bids=[_lvl(1, 1234, 10)])]  # wrong price

    mismatches = diff_trace(golden, snaps)
    assert len(mismatches) == 1
    assert mismatches[0].kind == "level"
    assert mismatches[0].side == "bid"
    assert mismatches[0].level_index == 0
    assert mismatches[0].expected.price == 1000
    assert mismatches[0].actual.price == 1234
    print("test_level_mismatch_price: PASS")
    print(report(mismatches))


def test_level_mismatch_order_id():
    golden = [_mk_entry(0, bids=[_lvl(1, 1000, 10)])]
    snaps = [_mk_snap(0, bids=[_lvl(2, 1000, 10)])]  # wrong orderId, same price/qty

    mismatches = diff_trace(golden, snaps)
    assert len(mismatches) == 1
    assert mismatches[0].kind == "level"
    assert mismatches[0].expected.order_id == 1
    assert mismatches[0].actual.order_id == 2
    print("test_level_mismatch_order_id: PASS")


# ---------------------------------------------------------------------
# 5. Ask-side mismatch — confirm side="ask" path works, not just bid
# ---------------------------------------------------------------------
def test_ask_side_mismatch():
    golden = [_mk_entry(0, asks=[_lvl(5, 2000, 3)])]
    snaps = [_mk_snap(0, asks=[_lvl(5, 2001, 3)])]  # wrong price on ask side

    mismatches = diff_trace(golden, snaps)
    assert len(mismatches) == 1
    assert mismatches[0].side == "ask"
    print("test_ask_side_mismatch: PASS")


# ---------------------------------------------------------------------
# 6. Both sides populated, mismatch only on one side
# ---------------------------------------------------------------------
def test_bid_ok_ask_wrong():
    golden = [_mk_entry(0, bids=[_lvl(1, 1000, 10)], asks=[_lvl(2, 2000, 5)])]
    snaps = [_mk_snap(0, bids=[_lvl(1, 1000, 10)], asks=[_lvl(2, 2005, 5)])]

    mismatches = diff_trace(golden, snaps)
    assert len(mismatches) == 1
    assert mismatches[0].side == "ask"
    print("test_bid_ok_ask_wrong: PASS")


# ---------------------------------------------------------------------
# 7. Empty book on both sides — REJECTED-before-any-orders edge case
# ---------------------------------------------------------------------
def test_empty_book_match():
    golden = [_mk_entry(0, bids=[], asks=[])]
    snaps = [_mk_snap(0, bids=[], asks=[])]

    mismatches = diff_trace(golden, snaps)
    assert mismatches == []
    print("test_empty_book_match: PASS")


# ---------------------------------------------------------------------
# 8. stop_on_first=True (default) halts at first bad entry, doesn't
#    scan later entries even if they'd also mismatch
# ---------------------------------------------------------------------
def test_stop_on_first_true():
    golden = [
        _mk_entry(0, bids=[_lvl(1, 1000, 10)]),
        _mk_entry(1, bids=[_lvl(2, 2000, 10)]),
    ]
    snaps = [
        _mk_snap(0, bids=[_lvl(1, 9999, 10)]),  # entry 0 wrong
        _mk_snap(1, bids=[_lvl(2, 8888, 10)]),  # entry 1 also wrong
    ]

    mismatches = diff_trace(golden, snaps, stop_on_first=True)
    assert len(mismatches) == 1
    assert mismatches[0].entry_index == 0
    print("test_stop_on_first_true: PASS")


# ---------------------------------------------------------------------
# 9. stop_on_first=False collects mismatches across multiple entries
# ---------------------------------------------------------------------
def test_stop_on_first_false():
    golden = [
        _mk_entry(0, bids=[_lvl(1, 1000, 10)]),
        _mk_entry(1, bids=[_lvl(2, 2000, 10)]),
    ]
    snaps = [
        _mk_snap(0, bids=[_lvl(1, 9999, 10)]),  # entry 0 wrong
        _mk_snap(1, bids=[_lvl(2, 8888, 10)]),  # entry 1 also wrong
    ]

    mismatches = diff_trace(golden, snaps, stop_on_first=False)
    assert len(mismatches) == 2
    assert {m.entry_index for m in mismatches} == {0, 1}
    print("test_stop_on_first_false: PASS")


# ---------------------------------------------------------------------
# 10. Entry-count mismatch — capture short/long vs golden -> raises
# ---------------------------------------------------------------------
def test_entry_count_mismatch_raises():
    golden = [_mk_entry(0), _mk_entry(1)]
    snaps = [_mk_snap(0)]  # missing entry 1 entirely (dropped packet)

    try:
        diff_trace(golden, snaps)
        assert False, "expected ValueError for entry count mismatch"
    except ValueError as e:
        assert "count mismatch" in str(e)
        print(f"test_entry_count_mismatch_raises: PASS ({e})")


# ---------------------------------------------------------------------
# 11. Sequence mismatch stops before book-state diff even runs
#     (sequence check happens first; a wrong sequence shouldn't also
#     spam level mismatches for a pair that's already misaligned)
# ---------------------------------------------------------------------
def test_sequence_mismatch_skips_level_diff():
    golden = [_mk_entry(0, bids=[_lvl(1, 1000, 10)])]
    snaps = [_mk_snap(99, bids=[_lvl(999, 1, 1)])]  # both sequence AND levels wrong

    mismatches = diff_trace(golden, snaps, stop_on_first=False)
    assert len(mismatches) == 1
    assert mismatches[0].kind == "sequence"
    print("test_sequence_mismatch_skips_level_diff: PASS")


if __name__ == "__main__":
    tests = [
        test_exact_match,
        test_sequence_mismatch,
        test_count_mismatch,
        test_level_mismatch_price,
        test_level_mismatch_order_id,
        test_ask_side_mismatch,
        test_bid_ok_ask_wrong,
        test_empty_book_match,
        test_stop_on_first_true,
        test_stop_on_first_false,
        test_entry_count_mismatch_raises,
        test_sequence_mismatch_skips_level_diff,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failed += 1
            print(f"{t.__name__}: FAIL — {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")