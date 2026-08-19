
#
# Created by devanandan : 19-08-2026
#

import struct

# ITCH 5.0 message layouts, standard spec.
# CONFIRM THESE AGAINST Orderbook-cpp's parse_add/parse_delete/parse_execute/
# parse_replace BEFORE trusting them — these are from the public spec, not
# verified against your actual C++ offsets yet.


def build_add_order(
        stock_locate: int,
        tracking_number: int,
        timestamp_ns: int,
        order_ref: int,
        buy_sell: str,       # 'B' or 'S'
        shares: int,
        stock: str,          # e.g. "AAPL"
        price: int,          # price in 1/10000 units, e.g. $150.25 -> 1502500
) -> bytes:
    """
    ITCH 5.0 'Add Order (No MPID)' message, type 'A', 36 bytes total:
      Message Type          1 byte   'A'
      Stock Locate           2 bytes
      Tracking Number        2 bytes
      Timestamp               6 bytes  (48-bit nanoseconds since midnight)
      Order Reference Number  8 bytes
      Buy/Sell Indicator      1 byte   'B' or 'S'
      Shares                  4 bytes
      Stock                   8 bytes  ASCII, space-padded
      Price                   4 bytes  (1/10000 dollar units)
    """
    # struct has no native 48-bit int type, so timestamp is packed as an
    # 8-byte big-endian value and then sliced down to the last 6 bytes.
    ts_full = struct.pack(">Q", timestamp_ns)
    ts_48 = ts_full[2:]  # drop the top 2 bytes, keep the low 6

    stock_bytes = stock.encode("ascii").ljust(8)[:8]
    buy_sell_byte = buy_sell.encode("ascii")

    return (
            b"A"
            + struct.pack(">H", stock_locate)
            + struct.pack(">H", tracking_number)
            + ts_48
            + struct.pack(">Q", order_ref)
            + buy_sell_byte
            + struct.pack(">I", shares)
            + stock_bytes
            + struct.pack(">I", price)
    )


def build_delete_order(
        stock_locate: int,
        tracking_number: int,
        timestamp_ns: int,
        order_ref: int,
) -> bytes:
    """
    ITCH 5.0 'Order Delete' message, type 'D', 19 bytes total:
      Message Type          1 byte   'D'
      Stock Locate           2 bytes
      Tracking Number        2 bytes
      Timestamp               6 bytes
      Order Reference Number  8 bytes
    """
    ts_48 = struct.pack(">Q", timestamp_ns)[2:]
    return (
            b"D"
            + struct.pack(">H", stock_locate)
            + struct.pack(">H", tracking_number)
            + ts_48
            + struct.pack(">Q", order_ref)
    )


def build_order_executed(
        stock_locate: int,
        tracking_number: int,
        timestamp_ns: int,
        order_ref: int,
        executed_shares: int,
        match_number: int,
) -> bytes:
    """
    ITCH 5.0 'Order Executed' message, type 'E', 31 bytes total:
      Message Type          1 byte   'E'
      Stock Locate           2 bytes
      Tracking Number        2 bytes
      Timestamp               6 bytes
      Order Reference Number  8 bytes
      Executed Shares         4 bytes
      Match Number            8 bytes
    """
    ts_48 = struct.pack(">Q", timestamp_ns)[2:]
    return (
            b"E"
            + struct.pack(">H", stock_locate)
            + struct.pack(">H", tracking_number)
            + ts_48
            + struct.pack(">Q", order_ref)
            + struct.pack(">I", executed_shares)
            + struct.pack(">Q", match_number)
    )


def build_order_replace(
        stock_locate: int,
        tracking_number: int,
        timestamp_ns: int,
        original_order_ref: int,
        new_order_ref: int,
        shares: int,
        price: int,
) -> bytes:
    """
    ITCH 5.0 'Order Replace' message, type 'U', 35 bytes total:
      Message Type            1 byte   'U'
      Stock Locate             2 bytes
      Tracking Number          2 bytes
      Timestamp                 6 bytes
      Original Order Ref Number 8 bytes
      New Order Reference Number 8 bytes
      Shares                    4 bytes
      Price                     4 bytes
    """
    ts_48 = struct.pack(">Q", timestamp_ns)[2:]
    return (
            b"U"
            + struct.pack(">H", stock_locate)
            + struct.pack(">H", tracking_number)
            + ts_48
            + struct.pack(">Q", original_order_ref)
            + struct.pack(">Q", new_order_ref)
            + struct.pack(">I", shares)
            + struct.pack(">I", price)
    )