#
# Created by devanandan : 19-08-2026
#

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mold_udp_scapy.moldudp64 import build_mold_packet
from scapy.all import Ether, IP, UDP, Raw, wrpcap, hexdump

from mold_udp_scapy.moldudp64 import build_mold_packet
from mold_udp_scapy.itch import build_add_order

add_msg = build_add_order(
    stock_locate=1,
    tracking_number=0,
    timestamp_ns=123456789,
    order_ref=1001,
    buy_sell="B",
    shares=100,
    stock="AAPL",
    price=1502500,
)

mold_payload = build_mold_packet(session="TESTSESS", sequence_number=1, itch_messages=[add_msg])

pkt = (
        Ether(src="00:11:22:33:44:55", dst="66:77:88:99:aa:bb")
        / IP(src="10.0.0.1", dst="10.0.0.2")
        / UDP(sport=30000, dport=30001)
        / Raw(load=mold_payload)
)

pkt.show()
hexdump(pkt)

wrpcap("mold_test.pcap", [pkt])
print("\nWrote mold_test.pcap — open it in Wireshark to inspect visually.")