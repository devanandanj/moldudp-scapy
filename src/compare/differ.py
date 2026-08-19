#
# Created by devanandan : 19-08-2026
#

"""
Diffs golden model output (Orderbook-cpp trace) against FPGA snapshot
captures.

Correlation is by index: entries[i] <-> snapshots[i]

"""

from dataclasses import dataclass

from src.snapshot.trace_parser import TraceEntry, OrderLevel
from src.snapshot.struct_unpacker import SnapshotEntry


@dataclass
class Mismatch:
    entry_index: int
    msg_index: int
    kind: str          # "count" | "sequence" | "level"
    side: str | None    # "bid" | "ask" | None
    level_index: int | None
    expected: object
    actual: object

    def __str__(self) -> str:
        loc = f"entry[{self.entry_index}] msg_index={self.msg_index}"
        if self.kind == "sequence":
            return f"{loc}: sequence mismatch: expected {self.expected}, got {self.actual}"
        if self.kind == "count":
            return f"{loc} side={self.side}: count mismatch: expected {self.expected}, got {self.actual}"
        return (f"{loc} side={self.side} level={self.level_index}: "
                f"expected {self.expected}, got {self.actual}")


def _diff_side(entry_idx: int, msg_index: int, side: str,
               golden: list[OrderLevel], actual: list[OrderLevel]) -> list[Mismatch]:
    mismatches = []

    if len(golden) != len(actual):
        mismatches.append(Mismatch(
            entry_index=entry_idx, msg_index=msg_index, kind="count",
            side=side, level_index=None,
            expected=len(golden), actual=len(actual),
        ))
        # still compare the overlapping prefix so you get level-level detail too
    for i, (g, a) in enumerate(zip(golden, actual)):
        if (g.order_id, g.price, g.quantity) != (a.order_id, a.price, a.quantity):
            mismatches.append(Mismatch(
                entry_index=entry_idx, msg_index=msg_index, kind="level",
                side=side, level_index=i,
                expected=g, actual=a,
            ))

    return mismatches


def diff_trace(golden_entries: list[TraceEntry],
               snapshots: list[SnapshotEntry],
               stop_on_first: bool = True) -> list[Mismatch]:
    if len(golden_entries) != len(snapshots):
        raise ValueError(
            f"entry count mismatch: golden has {len(golden_entries)} entries, "
            f"snapshots has {len(snapshots)} -- capture is incomplete or extra "
            f"packets were captured"
        )

    all_mismatches: list[Mismatch] = []

    for i, (entry, snap) in enumerate(zip(golden_entries, snapshots)):
        if snap.sequence != entry.msg_index:
            mm = Mismatch(
                entry_index=i, msg_index=entry.msg_index, kind="sequence",
                side=None, level_index=None,
                expected=entry.msg_index, actual=snap.sequence,
            )
            all_mismatches.append(mm)
            if stop_on_first:
                return all_mismatches
            continue  # don't bother diffing book state if sequence is already off

        bid_mm = _diff_side(i, entry.msg_index, "bid", entry.bids, snap.bids)
        ask_mm = _diff_side(i, entry.msg_index, "ask", entry.asks, snap.asks)
        mismatches = bid_mm + ask_mm

        if mismatches:
            all_mismatches.extend(mismatches)
            if stop_on_first:
                return all_mismatches

    return all_mismatches


def report(mismatches: list[Mismatch]) -> str:
    if not mismatches:
        return "MATCH: all entries verified, no mismatches."
    lines = [f"MISMATCH: {len(mismatches)} issue(s) found (showing in order):"]
    lines.extend(f"  {m}" for m in mismatches)
    return "\n".join(lines)