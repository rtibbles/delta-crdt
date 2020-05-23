import pytest

from delta_crdt import AWORSet

from .helpers import transmit


@pytest.fixture
def aworset():
    return AWORSet("test id 1")


def test_can_be_instantiated(aworset):
    pass


def test_starts_empty(aworset):
    assert len(aworset) == 0


def test_can_add_element(aworset):
    aworset.add("a")
    assert aworset == ["a"]


def test_can_remove_element(aworset):
    aworset.add("a")
    aworset.remove("a")
    assert len(aworset) == 0


def test_deduplicates_element_add(aworset):
    aworset.add({"value": "AAA"})
    aworset.add({"value": "AAA"})
    assert len(aworset) == 1
    assert aworset == [{"value": "AAA"}]


@pytest.fixture
def replicas():
    replica1 = AWORSet("test id 1")
    replica2 = AWORSet("test id 2")
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
    result = ["a", "b", "c", "d", "e"]
    assert replica1 == result
    assert replica2 == result


def test_test_test():
    replica1 = AWORSet("test id 1")
    replica1.add("a")
    replica1.add("b")
