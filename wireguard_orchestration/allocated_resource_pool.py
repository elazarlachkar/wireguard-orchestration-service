import typing


class AllocatedResourcePool:
    """
    This class represents a pool of allocated resources.
    This means that the pool receives a predefined set of resources, each of them can be used only once at a time.

    The class manages its resources by allocating each resource once, and then blocking further usage of the resource
    until a matching free is called.
    """
    def __init__(self, resources: typing.Set[typing.Any]):
        self._resources = resources
        self._used_resources = set()

    def allocate(self) -> typing.Any:
        """
        Allocates a resource out of the pool's available resources and returns it.
        This resource will be blocked to any other usage, until the free method is called.

        :raises StopIteration: In case there are no more available resources.
        """
        available_resources = self._resources - self._used_resources
        try:
            allocated_resource = available_resources.pop()
            self._used_resources.add(allocated_resource)
            return allocated_resource
        except KeyError:
            raise StopIteration("No available resources! Free an allocated resource in order to refill the pool")

    def free(self, resource: typing.Any):
        """
        Free a resource that has been allocated in the past, allowing its usage by the next user.
        If the resource was already freed, no error is raised.

        :raises KeyError: In case the given resource was never a part of the pool.
        """
        try:
            self._used_resources.remove(resource)

        # The resource isn't a part of the used resources, meaning it was already freed, or was never a part of the pool
        except KeyError:
            if resource not in self._resources:
                raise KeyError("The given resource was never a part of this pool!")
