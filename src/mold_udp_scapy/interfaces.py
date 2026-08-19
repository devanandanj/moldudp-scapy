
#
# Created by devanandan : 19-08-2026
#

from scapy.arch.windows import get_windows_if_list


def list_interfaces() -> list[dict]:
    """Returns raw interface dicts from Scapy's Windows backend."""
    return get_windows_if_list()


def find_interface_by_name(name: str) -> dict | None:
    """Exact-match lookup by the 'name' field, e.g. from list_ifaces.py output."""
    for iface in list_interfaces():
        if iface["name"] == name:
            return iface
    return None


def print_interfaces() -> None:
    """Same output as scripts/list_ifaces.py — kept here so it's reusable,
    not just a one-off script."""
    for iface in list_interfaces():
        print(f"name: {iface['name']}")
        print(f"  guid: {iface['guid']}")
        print(f"  mac:  {iface['mac']}")
        print(f"  ips:  {iface['ips']}")
        print()