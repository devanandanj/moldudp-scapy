
#
# Created by devanandan : 19-08-2026
#


from scapy.all import Ether, IP, UDP, Raw, sendp


class MoldSequencer:
    """
    Tracks the MoldUDP64 sequence number across multiple sends.
    Sequence numbers are per-session and must increment by the number
    of messages sent in each packet — NOT just by 1 per packet.
    """

    def __init__(self, start_sequence: int = 1):
        self._next_seq = start_sequence

    def next(self, message_count: int) -> int:
        """Returns the sequence number to use for the packet about to be
        sent, then advances the counter by message_count for next time."""
        seq = self._next_seq
        self._next_seq += message_count
        return seq


def send_mold_packet(
        payload: bytes,
        iface: str,
        src_mac: str,
        dst_mac: str,
        src_ip: str,
        dst_ip: str,
        sport: int,
        dport: int,
) -> None:
    """
    Wraps a MoldUDP64 payload (from build_mold_packet) in Ether/IP/UDP
    and sends it out the given interface.

    Requires: Administrator PowerShell, Npcap installed in WinPcap
    API-compatible mode, and a real interface name from interfaces.py.
    """
    pkt = (
            Ether(src=src_mac, dst=dst_mac)
            / IP(src=src_ip, dst=dst_ip)
            / UDP(sport=sport, dport=dport)
            / Raw(load=payload)
    )
    sendp(pkt, iface=iface, verbose=False)