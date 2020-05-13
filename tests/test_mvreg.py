import pytest

from delta_crdts import MVReg
from .helpers import transmit


@pytest.fixture
def mvreg():
    return MVReg("test id")


def test_can_create(mvreg):
    pass


def test_starts_empty(mvreg):
    assert len(mvreg) == 0


def test_can_write_values(mvreg):
    mvreg.write("a")
    assert mvreg == set("a")
    mvreg.write("b")
    assert mvreg == set("b")


@pytest.fixture
def replicas():
    replica1 = MVReg("id1")
    replica2 = MVReg("id2")
    deltas1 = []
    deltas2 = []
    deltas1.append(replica1.write("hello"))
    deltas1.append(replica1.write("world"))
    deltas2.append(replica2.write("world"))
    deltas2.append(replica2.write("hello"))

    return replica1, replica2, deltas1, deltas2


def test_concurrent_writes(replicas):
    replica1, replica2, deltas1, deltas2 = replicas
    assert replica1 == set(["world"])
    assert replica2 == set(["hello"])


def test_changes_converge(replicas):
    replica1, replica2, deltas1, deltas2 = replicas
    map(lambda x: replica1.apply(transmit(x)), deltas2)
    map(lambda x: replica2.apply(transmit(x)), deltas1)
    assert replica1 == set(["hello", "world"])
    assert replica2 == set(["hello", "world"])


def test_sequential_writes_converge():
    replica_a = MVReg("idA")
    delta_a = replica_a.write("a")
    replica_b = MVReg("idB")
    replica_b.apply(delta_a)
    delta_b = replica_b.write("b")
    replica_a.apply(delta_b)
    assert replica_a == set(["b"])
