#
# Created by devanandan : 19-08-2026
#

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mold_udp_scapy.moldudp64 import build_mold_packet
from mold_udp_scapy.itch import build_add_order
from mold_udp_scapy.sender import MoldSequencer, send_mold_packet

seq = MoldSequencer(start_sequence=1)

add_msg = build_add_order(
    stock_locate=1,
    tracking_number=0,
    timestamp_ns=123456789,
    order_ref=1001,
    buy_sell="B",
    shares=100,
    stock="AAPL",
    price=1502500,  # $150.25
)

sequence_number = seq.next(message_count=1)
mold_payload = build_mold_packet(
    session="TESTSESS",
    sequence_number=sequence_number,
    itch_messages=[add_msg],
)

print(f"Built packet, sequence_number={sequence_number}, "
      f"payload len={len(mold_payload)} bytes")
print(mold_payload.hex())

# Uncomment once the FPGA is on the bench and you have a real
# interface name + MAC/IP pair from interfaces.py:
#
# send_mold_packet(
#     payload=mold_payload,
#     iface="YOUR_INTERFACE_NAME_HERE",
#     src_mac="YOUR_LAPTOP_NIC_MAC",
#     dst_mac="FPGA_NIC_MAC",
#     src_ip="10.0.0.1",
#     dst_ip="10.0.0.2",
#     sport=30000,
#     dport=30001,
# )