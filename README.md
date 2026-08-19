# moldudp-scapy

Python/Scapy toolkit for building and sending MoldUDP64-framed NASDAQ ITCH
5.0 messages to an FPGA order-book parser over Ethernet.

Companion tool to [Orderbook-cpp](https://github.com/devanandanj/Orderbook-cpp) —
the host-side transmitter that drives the FPGA capstone's parser with live
and adversarial ITCH 5.0 / MoldUDP64 traffic.

## Status

**Host-side packet construction is complete and offline-verified.** Live
send/receive against the FPGA is not yet tested — the target board is not
in hand yet. Everything up to and including raw-frame construction has been
built and hex-verified; `sender.py`'s actual `sendp()` path is written but
unexercised against real hardware.

This is intentionally staged: build and validate the packet layer first,
wire it to a physical link once the board arrives.

## Why this exists

The FPGA capstone needs a host-side tool to drive ITCH 5.0 / MoldUDP64
traffic at the board — both realistic session replay and adversarial edge
cases (malformed headers, truncated messages, out-of-order sequence
numbers). Scapy's interactive, mutate-and-resend workflow made it the
right fit for this over a from-scratch compiled sender.

Message field offsets are cross-checked byte-for-byte against `Orderbook-cpp`'s
`parse_add`, `parse_delete`, `parse_execute`, and `parse_replace` — this tool
and the golden model are guaranteed to agree on wire format, not just built
to a spec independently.

## Project structure

```
mold-udp-scapy/
├── src/
│   └── mold_udp_scapy/
│       ├── moldudp64.py    # MoldUDP64 header + message-block framing
│       ├── itch.py         # ITCH 5.0 message builders (Add/Delete/Execute/Replace)
│       ├── interfaces.py   # Windows NIC discovery
│       ├── sender.py       # raw Ethernet send (Scapy sendp), sequence tracking
│       └── sniffer.py      # UDP trace-in listener, parked pending UART-vs-UDP decision
├── scripts/
│   ├── list_ifaces.py       # print available NICs
│   ├── build_and_inspect.py # build a packet, hexdump it, write to pcap — no hardware needed
│   └── send_test.py         # build + optionally send a real Add Order message
└── requirements.txt
```

## Setup

Requires Windows + [Npcap](https://npcap.com/#download) installed with
**"Install Npcap in WinPcap API-compatible Mode"** checked. Raw frame
sends require an Administrator terminal.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Quickstart — no hardware required

Build a MoldUDP64/ITCH packet and inspect it without touching a NIC:

```powershell
python scripts\build_and_inspect.py
```

This writes `mold_test.pcap`, openable in Wireshark, plus a terminal
hexdump and layer-by-layer breakdown.

Build a real Add Order message and print its hex:

```powershell
python scripts\send_test.py
```

The actual `send_mold_packet(...)` call in `send_test.py` is commented out
by default — uncomment once a real interface name and MAC/IP pair are
available (via `scripts\list_ifaces.py`) and the board is on the bench.

## Verified so far

- MoldUDP64 header (session/sequence/message count) — byte-verified via
  manual hexdump walkthrough
- Add Order (`'A'`) message layout — offsets confirmed against
  `Orderbook-cpp`'s `parse_add`
- Delete, Execute, Replace layouts — offsets confirmed against their
  respective C++ parsers

## Not yet done

- No live send/receive test against the FPGA (blocked on hardware)
- No automated tests (correctness currently verified by manual hexdump
  inspection)
- No CLI entry point — scripts are edited directly per test case
- Sequence rollover / heartbeat (`message_count = 0`) handling undecided