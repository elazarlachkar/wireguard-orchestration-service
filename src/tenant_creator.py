import ipaddress
import threading

from allocated_resource_pool import AllocatedResourcePool
from cached_resource_creator import CachedResourceCreator
from overlay_network import OverlayNetwork
from tenant import Tenant


class TenantCreator(CachedResourceCreator):
    """
    This class manages the creation of tenants.

    Each tenant is identified using a unique string, and uses a virtual network pool.
    A tenant is created only if it doesn't already exist in the cache.
    """
    VIRTUAL_NETWORKS = {
        ipaddress.IPv4Network("192.168.1.0/24"),
        ipaddress.IPv4Network("72.16.0.0/16")
    }

    def __init__(self):
        super().__init__()
        self._virtual_network_pool = AllocatedResourcePool(TenantCreator.VIRTUAL_NETWORKS)
        self.cache_lock = threading.Lock()

    def get(self, tenant_id: str) -> Tenant:
        """
        Returns a tenant from the cache. If it doesn't exist yet, creates it.
        """
        return super().get(tenant_id)

    def _create_resource(self) -> Tenant:
        """
        Creates a new tenant instance.
        Each tenant requires a virtual network, which is allocated by the virtual network pool.

        :raises Exception: In case there is no more private networks available to use.
        """
        try:
            virtual_network: ipaddress.IPv4Network = self._virtual_network_pool.allocate()
        except StopIteration:
            raise Exception("Failed to create new tenant, no network available!")

        overlay_network = OverlayNetwork(virtual_network)
        return Tenant(overlay_network)

    def remove(self, tenant_id: str):
        """
        Removes a tenant from the cache, and releasing its virtual network to be used by future tenants.
        The next time a tenant with the same ID will be requested, it will be created again.
        """
        tenant = self.get(tenant_id)
        virtual_network = tenant.get_overlay_network().get_virtual_network()

        super().remove(tenant_id)
        self._virtual_network_pool.free(virtual_network)
