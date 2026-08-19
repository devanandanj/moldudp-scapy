from src.snapshot.trace_parser import parse_golden_trace

entries = parse_golden_trace("test/stress_test_trace.txt")

print(f"parsed {len(entries)} entries")
print(f"first: msg={entries[0].msg_index} type={entries[0].msg_type} "
      f"accepted={entries[0].accepted} bids={len(entries[0].bids)} asks={len(entries[0].asks)}")
print(f"last:  msg={entries[-1].msg_index} type={entries[-1].msg_type} "
      f"accepted={entries[-1].accepted} bids={len(entries[-1].bids)} asks={len(entries[-1].asks)}")

# spot-check against known expected states from test.cpp's comments:
# after msg77: bids=32 asks=31
msg77 = next((e for e in entries if e.msg_index == 77), None)
if msg77:
    print(f"msg77: bids={len(msg77.bids)} asks={len(msg77.asks)} (expect 32, 31)")

# final entry: bids=1 asks=1
print(f"final: bids={len(entries[-1].bids)} asks={len(entries[-1].asks)} (expect 1, 1)")