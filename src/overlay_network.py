import ipaddress

from allocated_resource_pool import AllocatedResourcePool


class OverlayNetwork:
    def __init__(self, virtual_network: ipaddress.IPv4Network):
        self._virtual_network = virtual_network
        self._address_pool = AllocatedResourcePool(list(virtual_network.hosts()))

    def allocate_ip_address(self) -> ipaddress.IPv4Address:
        return self._address_pool.allocate()

    def free_ip_address(self, ip_address: ipaddress.IPv4Address):
        self._address_pool.free(ip_address)

    def get_virtual_network(self) -> ipaddress.IPv4Network:
        return self._virtual_network
