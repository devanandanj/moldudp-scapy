
#
# Created by devanandan : 19-08-2026
#

from scapy.arch.windows import get_windows_if_list

for iface in get_windows_if_list():
    print(f"name: {iface['name']}")
    print(f"  guid: {iface['guid']}")
    print(f"  mac:  {iface['mac']}")
    print(f"  ips:  {iface['ips']}")
    print()