#
# Created by devanandan : 19-08-2026
#


from scapy.all import sniff, UDP, Raw

def handle_packet(pkt):
    # Called once per matched packet. Right now this just prints —
    # later you'll swap this for your trace-record parser once
    # you've defined the on-wire format for the FPGA->host trace.
    if UDP in pkt and Raw in pkt:
        payload = bytes(pkt[Raw].load)
        print(f"[{len(payload)} bytes] {payload.hex()}")

def start_sniffing(iface: str, udp_port: int):
    """
    Blocks and listens until closed.
    """
    bpf_filter = f"udp port {udp_port}"
    print(f"Listening on {iface}, filter: '{bpf_filter}'")
    sniff(iface=iface, filter=bpf_filter, prn=handle_packet, store=False)