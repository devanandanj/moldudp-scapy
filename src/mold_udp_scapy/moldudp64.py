#
# Created by devanandan : 19-08-2026
#

import struct

SESSION_LEN = 10

def build_mold_header(session: str, sequence_number: int, message_count: int) -> bytes:
    """
    MoldUDP64 packet header, 20 bytes total, big-endian:
      Session         10 bytes, ASCII, space-padded
      SequenceNumber   8 bytes, unsigned
      MessageCount     2 bytes, unsigned (0x0000 = heartbeat, 0xFFFF = end of session)
    """

    session_bytes = session.encode("ascii").ljust(SESSION_LEN)[:SESSION_LEN]
    return struct.pack(">10sQH", session_bytes, sequence_number, message_count)

def build_message_block(itch_payload: bytes) -> bytes:
    """
    One MoldUDP64 message block = 2-byte big-endian length prefix, then the
    raw ITCH message bytes. Length excludes the 2-byte prefix itself.
    """
    return struct.pack(">H", len(itch_payload)) + itch_payload

def build_mold_packet(session: str, sequence_number: int, itch_messages: list[bytes]) -> bytes:
    """
    Full MoldUDP64 UDP payload: header + N message blocks, back to back.
    itch_messages: list of raw ITCH message byte strings, NOT yet length-prefixed.
    """
    header = build_mold_header(session, sequence_number, len(itch_messages))
    blocks = b"".join(build_message_block(m) for m in itch_messages)
    return header + blocks