import abc
import typing


class CachedResourceCreator(abc.ABC):
    """
    Some resources are expensive to create, or meant to be shared by multiple users by design.
    This class manages those type of resources.

    Each user access the resource it needs by the `get` method.
        If the resource doesn't exist - it is created, saved in the cache and returned.
        If the resource already exist - it is returned from the cache.

    The `remove` method allows the user to remove an existing resource from the cache. Next time the resource is
    requested, it will be recreated.
    """
    def __init__(self):
        self._resources: dict[str, typing.Any] = {}

    @abc.abstractmethod
    def _create_resource(self) -> typing.Any:
        """
        Subclasses should implement here the resource creation.
        A resource will be created only if a user requested it and it doesn't exist in the cache.
        """
        pass

    def get(self, resource_id: str) -> typing.Any:
        """
        Returns the resource with the matching ID.
        If the resource doesn't exist - it is created, saved in the cache and returned.
        If the resource already exist - it is returned from the cache.
        """
        if resource_id not in self._resources.keys():
            resource = self._create_resource()
            self._resources[resource_id] = resource

        return self._resources.get(resource_id)

    def remove(self, resource_id):
        """
        Removes a resource from the cache. Next time the resource is requested, it will be recreated.
        """
        try:
            self._resources.pop(resource_id)
        except KeyError:  # If the resource was already removed, do not raise an error
            pass
