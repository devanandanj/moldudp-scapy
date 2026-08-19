#
# Created by devanandan : 19-08-2026
#

"""
Receives raw book-snapshot UDP packets from the FPGA and hands them to
StructUnpacker. Blocking, single-socket receive loop — this is a test/
verification tool, not a production service, so no async/threading here.

Usage:
    listener = UdpListener(port=5005)
    snapshots = listener.capture(expected_count=143)
"""

import socket

from snapshot.struct_unpacker import StructUnpacker, SnapshotEntry


class UdpListener:
    def __init__(self, port: int, host: str = "0.0.0.0",
                 config_path: str = "config/snapshot_format.yaml",
                 recv_bufsize: int = 4096):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((host, port))
        self._unpacker = StructUnpacker(config_path)
        self._recv_bufsize = recv_bufsize

    def capture(self, expected_count: int, timeout_s: float = 5.0) -> list[SnapshotEntry]:
        """
        Blocks until expected_count packets are received or timeout_s elapses
        with no packet arriving. Returns whatever was captured (may be short
        if it timed out) -- differ.py's entry-count check will catch that
        rather than this silently padding or looping forever.
        """
        self._sock.settimeout(timeout_s)
        snapshots: list[SnapshotEntry] = []

        for i in range(expected_count):
            try:
                raw, addr = self._sock.recvfrom(self._recv_bufsize)
            except socket.timeout:
                print(f"timeout after {len(snapshots)}/{expected_count} packets "
                      f"({timeout_s}s with no packet)")
                break

            try:
                entry = self._unpacker.unpack(raw)
            except ValueError as e:
                print(f"packet {i} from {addr}: unpack failed: {e}")
                raise

            snapshots.append(entry)

        return snapshots

    def close(self):
        self._sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()