#
# Created by devanandan : 19-08-2026
#

"""
Unpacks raw FPGA UDP book-snapshot packets into the same TraceEntry/OrderLevel
shape produced by golden_trace_parser.py, using field widths from
config/snapshot_format.yaml.

"""

import struct
import yaml
from dataclasses import dataclass, field
from pathlib import Path

from src.snapshot.trace_parser import OrderLevel


@dataclass
class SnapshotEntry:
    sequence: int
    bids: list[OrderLevel] = field(default_factory=list)
    asks: list[OrderLevel] = field(default_factory=list)


def _load_format(config_path: str = "config/snapshot_format.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


class StructUnpacker:
    def __init__(self, config_path: str = "config/snapshot_format.yaml"):
        cfg = _load_format(config_path)

        if cfg["byte_order"] != "big":
            raise NotImplementedError("only big-endian wire format is supported")

        self._max_orders = cfg["max_orders_per_side"]

        # header: bid_count(1) + ask_count(1) + sequence(2) = 4 bytes, BE
        self._header_struct = struct.Struct(">BBH")

        # order record: price(4) + quantity(4) + orderId(8) = 16 bytes, BE
        fields = cfg["order_record"]["fields"]
        self._record_fields = [f["name"] for f in fields]
        self._record_struct = struct.Struct(">" + "".join(
            {1: "B", 2: "H", 4: "I", 8: "Q"}[f["width"]] for f in fields
        ))
        self._record_size = self._record_struct.size

    def unpack(self, raw: bytes) -> SnapshotEntry:
        header_size = self._header_struct.size
        if len(raw) < header_size:
            raise ValueError(
                f"packet too short for header: got {len(raw)} bytes, need {header_size}"
            )

        bid_count, ask_count, sequence = self._header_struct.unpack_from(raw, 0)

        if bid_count > self._max_orders or ask_count > self._max_orders:
            raise ValueError(
                f"sequence {sequence}: bid_count={bid_count} ask_count={ask_count} "
                f"exceeds max_orders_per_side={self._max_orders}"
            )

        expected_len = header_size + (bid_count + ask_count) * self._record_size
        if len(raw) != expected_len:
            raise ValueError(
                f"sequence {sequence}: packet length {len(raw)} != expected "
                f"{expected_len} (header={header_size}, "
                f"{bid_count}+{ask_count} records * {self._record_size}B)"
            )

        offset = header_size
        bids = []
        for _ in range(bid_count):
            price, quantity, order_id = self._record_struct.unpack_from(raw, offset)
            bids.append(OrderLevel(order_id=order_id, price=price, quantity=quantity))
            offset += self._record_size

        asks = []
        for _ in range(ask_count):
            price, quantity, order_id = self._record_struct.unpack_from(raw, offset)
            asks.append(OrderLevel(order_id=order_id, price=price, quantity=quantity))
            offset += self._record_size

        return SnapshotEntry(sequence=sequence, bids=bids, asks=asks)