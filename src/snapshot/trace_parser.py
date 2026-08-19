#
# Created by devanandan : 19-08-2026
#

"""
Parses Orderbook-cpp's WriteTraceEntry output format:

    MSG,<msgIndex>,<msgType>,<orderId>,<OK|REJECTED>,<reason>
    BID,<orderId>,<price>,<qty>      (zero or more, sorted by orderId asc)
    ASK,<orderId>,<price>,<qty>      (zero or more, sorted by orderId asc)
    END
    <blank line>

into a list of structured TraceEntry records, one per message, for
diffing against FPGA-captured snapshots.
"""

from dataclasses import dataclass, field


@dataclass
class OrderLevel:
    order_id: int
    price: int
    quantity: int


@dataclass
class TraceEntry:
    msg_index: int
    msg_type: str
    order_id: int
    accepted: bool
    reason: str
    bids: list[OrderLevel] = field(default_factory=list)
    asks: list[OrderLevel] = field(default_factory=list)


def parse_golden_trace(path: str) -> list[TraceEntry]:
    entries: list[TraceEntry] = []
    current: TraceEntry | None = None

    with open(path, "r") as f:
        for line_num, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue  # blank line between entries, ignore

            parts = line.split(",")
            tag = parts[0]

            if tag == "MSG":
                if current is not None:
                    raise ValueError(
                        f"line {line_num}: new MSG before previous entry's END"
                    )
                if len(parts) < 6:
                    raise ValueError(f"line {line_num}: malformed MSG line: {line}")
                msg_index = int(parts[1])
                msg_type = parts[2]
                order_id = int(parts[3])
                accepted = parts[4] == "OK"
                reason = parts[5]
                current = TraceEntry(
                    msg_index=msg_index,
                    msg_type=msg_type,
                    order_id=order_id,
                    accepted=accepted,
                    reason=reason,
                )

            elif tag in ("BID", "ASK"):
                if current is None:
                    raise ValueError(f"line {line_num}: {tag} line before MSG: {line}")
                if len(parts) != 4:
                    raise ValueError(f"line {line_num}: malformed {tag} line: {line}")
                level = OrderLevel(
                    order_id=int(parts[1]),
                    price=int(parts[2]),
                    quantity=int(parts[3]),
                )
                (current.bids if tag == "BID" else current.asks).append(level)

            elif tag == "END":
                if current is None:
                    raise ValueError(f"line {line_num}: END with no open MSG")
                entries.append(current)
                current = None

            else:
                raise ValueError(f"line {line_num}: unrecognized tag: {tag}")

    if current is not None:
        raise ValueError("file ended with an open MSG entry (missing END)")

    return entries