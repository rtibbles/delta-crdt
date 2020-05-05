import pytest

from delta_crdts import GSet
from .helpers import transmit


@pytest.fixture
def gset():
    return GSet("test id 1")


def test_can_create(gset):
    pass


def test_starts_empty(gset):
    assert len(gset) == 0


def test_can_add_element(gset):
    gset.add("a")
    assert gset == set("a")


@pytest.fixture
def replicas():
    replica1 = GSet("test id 1")
    replica2 = GSet("test id 2")
    deltas1 = []
    deltas2 = []
    deltas1.append(replica1.add("a"))
    deltas1.append(replica1.add("b"))
    deltas1.append(replica1.add("c"))
    deltas2.append(replica2.add("a"))
    deltas2.append(replica2.add("d"))
    deltas2.append(replica2.add("e"))
    return replica1, replica2, deltas1, deltas2


def test_can_add_to_replicas(replicas):
    replica1, replica2, deltas1, deltas2 = replicas
    assert replica1 == set(["a", "b", "c"])
    assert replica2 == set(["a", "d", "e"])


def test_can_transmit(replicas):
    replica1, replica2, deltas1, deltas2 = replicas
    map(lambda x: replica1.apply(transmit(x)), deltas2)
    map(lambda x: replica2.apply(transmit(x)), deltas1)
    assert replica1 == set(["a", "b", "c", "d", "e"])
    assert replica2 == set(["a", "b", "c", "d", "e"])
