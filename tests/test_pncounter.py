import pytest

from delta_crdts import PNCounter
from .helpers import transmit


@pytest.fixture
def pncounter():
    return PNCounter("test id 1")


def test_can_create(pncounter):
    pass


def test_starts_with_value_zero(pncounter):
    assert pncounter == 0


def test_can_inc(pncounter):
    pncounter.inc()
    assert pncounter == 1


def test_can_dec(pncounter):
    pncounter.dec()
    assert pncounter == -1


@pytest.fixture
def replicas():
    replica1 = PNCounter("test id 1")
    replica2 = PNCounter("test id 2")
    replica1.inc()
    replica1.inc()
    replica1.dec()
    replica2.inc()
    replica2.inc()
    replica2.dec()
    return replica1, replica2


def test_both_converge(replicas):
    replica1, replica2 = replicas
    map(lambda x: replica1.apply(transmit(x)), replica2.deltas)
    map(lambda x: replica2.apply(transmit(x)), replica1.deltas)
    assert replica1 == 2
    assert replica2 == 2
