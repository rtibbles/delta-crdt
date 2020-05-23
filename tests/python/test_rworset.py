import pytest

from delta_crdt import RWORSet

from .helpers import transmit


@pytest.fixture
def rworset():
    return RWORSet("test id 1")


def test_can_be_instantiated(rworset):
    pass


def test_starts_empty(rworset):
    assert len(rworset) == 0


def test_can_add_element(rworset):
    rworset.add("a")
    assert rworset == ["a"]


def test_can_remove_element(rworset):
    rworset.add("a")
    rworset.remove("a")
    assert len(rworset) == 0


def test_deduplicates_element_add(rworset):
    rworset.add({"value": "AAA"})
    rworset.add({"value": "AAA"})
    assert len(rworset) == 1
    assert rworset == [{"value": "AAA"}]


@pytest.fixture
def replicas():
    replica1 = RWORSet("test id 1")
    replica2 = RWORSet("test id 2")
    replica1.add("a")
    replica1.add("b")
    replica1.remove("b")
    replica1.add("c")
    replica2.add("a")
    replica2.remove("a")
    replica2.add("b")
    replica2.add("d")
    replica2.add("e")
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
    result = ["c", "d", "e"]
    assert replica1 == result
    assert replica2 == result
