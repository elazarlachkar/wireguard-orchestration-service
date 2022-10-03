import ipaddress

from wireguard_orchestration.allocated_resource_pool import AllocatedResourcePool


class OverlayNetwork:
    """
    This class represents an Overlay Network, and is used to allocate IP addresses for clients.
    """
    def __init__(self, virtual_network: ipaddress.IPv4Network):
        """
        :param virtual_network: The IP network which the overlay network is based on. Clients will be given an IP
        address out of this pool of addresses.
        """
        self._virtual_network = virtual_network
        self._address_pool = AllocatedResourcePool(set(virtual_network.hosts()))

    def allocate_ip_address(self) -> ipaddress.IPv4Address:
        """
        Allocates an IP address in the network.
        The returned IP address won't be available again until the `free_ip_address` method is called.

        :raises StopIteration: In case there are no more available IP addresses in the network.
        """
        return self._address_pool.allocate()

    def free_ip_address(self, ip_address: ipaddress.IPv4Address):
        """
        Free a previously allocated IP address for future use.
        If the given IP address was already freed in the past, no error is raised.

        :raises KeyError: In case the given IP address was never a part of the network.
        """
        self._address_pool.free(ip_address)

    def get_virtual_network(self) -> ipaddress.IPv4Network:
        """
        Returns the IP network which the overlay network is based on.
        """
        return self._virtual_network
