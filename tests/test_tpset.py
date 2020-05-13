import pytest

from delta_crdts import TPSet

from .helpers import transmit


@pytest.fixture
def tpset():
    return TPSet("test id 1")


def test_can_be_instantiated(tpset):
    pass


def test_starts_empty(tpset):
    assert len(tpset) == 0


def test_can_add_element(tpset):
    tpset.add("a")
    assert tpset == set("a")


def test_can_remove_element(tpset):
    tpset.add("a")
    tpset.remove("a")
    assert len(tpset) == 0


@pytest.fixture
def replicas():
    replica1 = TPSet("test id 1")
    replica2 = TPSet("test id 2")
    replica1.add("a")
    replica1.add("b")
    replica1.add("c")
    replica2.remove("a")
    replica2.add("b")
    replica2.add("d")
    replica2.add("e")
    return replica1, replica2


def test_changes_converge(replicas):
    replica1, replica2 = replicas
    for delta in replica1.deltas:
        replica2.apply(transmit(delta))
    for delta in replica2.deltas:
        replica1.apply(transmit(delta))
    result = set(["b", "c", "d", "e"])
    assert replica1 == result
    assert replica2 == result
