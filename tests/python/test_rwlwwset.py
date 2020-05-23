import pytest

from delta_crdt import RWLWWSet

from .helpers import transmit


@pytest.fixture
def rwlwwset():
    return RWLWWSet("test id 1")


def test_can_be_instantiated(rwlwwset):
    pass


def test_starts_empty(rwlwwset):
    assert len(rwlwwset) == 0


def test_can_add_element(rwlwwset):
    rwlwwset.add(1, "a")
    assert rwlwwset == ["a"]


def test_can_remove_element(rwlwwset):
    rwlwwset.add(1, "a")
    rwlwwset.remove(2, "a")
    assert len(rwlwwset) == 0


def test_deduplicates_element_add(rwlwwset):
    rwlwwset.add(1, {"value": "AAA"})
    rwlwwset.add(2, {"value": "AAA"})
    assert len(rwlwwset) == 1
    assert rwlwwset == [{"value": "AAA"}]


@pytest.fixture
def replicas():
    replica1 = RWLWWSet("test id 1")
    replica2 = RWLWWSet("test id 2")
    replica1.add(1, "a")
    replica1.add(2, "b")
    replica1.remove(3, "b")
    replica1.add(4, "c")
    replica2.add(1, "a")
    replica2.remove(2, "a")
    replica2.add(3, "b")
    replica2.add(5, "d")
    replica2.add(6, "e")
    return replica1, replica2


def test_changes_made(replicas):
    replica1, replica2 = replicas
    assert replica1 == ["a", "c"]
    assert replica2 == ["b", "d", "e"]


def test_changes_converge(replicas):
    replica1, replica2 = replicas
    for delta in replica1.deltas:
        replica2.apply(transmit(delta))
    for delta in replica2.deltas:
        replica1.apply(transmit(delta))
    result = ["b", "c", "d", "e"]
    assert replica1 == result
    assert replica2 == result
