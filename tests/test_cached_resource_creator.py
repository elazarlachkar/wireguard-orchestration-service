import mock

from src.cached_resource_creator import CachedResourceCreator

RESOURCE_ID = "randomID"


class CachedMockCreator(CachedResourceCreator):
    def _create_resource(self) -> mock.Mock:
        return mock.Mock()


def test_cached_get():
    creator = CachedMockCreator()
    resource = creator.get(RESOURCE_ID)

    assert resource is creator.get(RESOURCE_ID)


def test_remove():
    creator = CachedMockCreator()
    resource = creator.get(RESOURCE_ID)
    creator.remove(RESOURCE_ID)

    assert resource is not creator.get(RESOURCE_ID)


def test_duplicate_remove():
    creator = CachedMockCreator()
    _ = creator.get(RESOURCE_ID)
    creator.remove(RESOURCE_ID)

    # Make sure no error is raised
    creator.remove(RESOURCE_ID)
