import mock
import pytest

from wireguard_orchestration.allocated_resource_pool import AllocatedResourcePool


def test_sanity():
    resource_mock = mock.Mock()
    pool = AllocatedResourcePool({resource_mock})

    assert pool.allocate() == resource_mock
    with pytest.raises(StopIteration):
        pool.allocate()

    pool.free(resource_mock)
    assert pool.allocate() == resource_mock


def test_free_other_resource():
    resource_mock = mock.Mock()
    pool = AllocatedResourcePool({resource_mock})

    other_resource = mock.Mock()
    with pytest.raises(KeyError):
        pool.free(other_resource)
