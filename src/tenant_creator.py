import ipaddress

from allocated_resource_pool import AllocatedResourcePool
from cached_resource_creator import CachedResourceCreator
from overlay_network import OverlayNetwork
from tenant import Tenant


class TenantCreator(CachedResourceCreator):
    VIRTUAL_NETWORKS = {
        ipaddress.IPv4Network("192.168.1.0/24"),
        ipaddress.IPv4Network("72.16.0.0/16")
    }

    def __init__(self):
        super().__init__()
        self._virtual_network_pool = AllocatedResourcePool(TenantCreator.VIRTUAL_NETWORKS)

    def get(self, tenant_id: str) -> Tenant:
        return super().get(tenant_id)

    def _create_resource(self) -> Tenant:
        try:
            virtual_network: ipaddress.IPv4Network = self._virtual_network_pool.allocate()
        except StopIteration:
            raise Exception("Failed to create new tenant, no network available!")

        overlay_network = OverlayNetwork(virtual_network)
        return Tenant(overlay_network)

    def remove(self, tenant_id: str):
        tenant = self.get(tenant_id)
        virtual_network = tenant.get_overlay_network().get_virtual_network()

        super().remove(tenant_id)
        self._virtual_network_pool.free(virtual_network)
