import pytest

from delta_crdts import LWWReg
from .helpers import transmit


@pytest.fixture
def lwwreg():
    return LWWReg("test id")


def test_can_create(lwwreg):
    pass


def test_starts_empty(lwwreg):
    assert lwwreg == None  # noqa


def test_can_write_values(lwwreg):
    lwwreg.write(1, "a")
    assert lwwreg == "a"
    lwwreg.write(2, "b")
    assert lwwreg == "b"


@pytest.fixture
def replicas():
    replica1 = LWWReg("id1")
    replica2 = LWWReg("id2")
    replica1.write(0, "a")
    replica1.write(1, "b")
    replica2.write(0, "c")
    replica2.write(1, "d")

    return replica1, replica2


def test_concurrent_writes(replicas):
    replica1, replica2 = replicas
    assert replica1 == "b"
    assert replica2 == "d"


def test_changes_converge(replicas):
    replica1, replica2 = replicas
    map(lambda x: replica1.apply(transmit(x)), replica2.deltas)
    map(lambda x: replica2.apply(transmit(x)), replica1.deltas)
    assert replica1 == "d"
    assert replica2 == "d"
