
#
# Created by devanandan : 19-08-2026
#

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mold_udp_scapy.moldudp64 import build_mold_packet
from scapy.all import Ether, IP, UDP, Raw, wrpcap, hexdump

dummy_itch_msg = b"\x41\x00\x00\x00\x01"

mold_payload = build_mold_packet(session="dummy", sequence_number=1, itch_messages=[dummy_itch_msg])
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