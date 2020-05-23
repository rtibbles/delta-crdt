import pytest

from delta_crdt import GCounter
from .helpers import transmit


@pytest.fixture
def gcounter():
    return GCounter("test id 1")


def test_can_create(gcounter):
    pass


def test_starts_with_value_zero(gcounter):
    assert gcounter == 0


def test_can_inc(gcounter):
    gcounter.inc()
    assert gcounter == 1


@pytest.fixture
def replicas():
    replica1 = GCounter("test id 1")
    replica2 = GCounter("test id 2")
    replica1.inc()
    replica1.inc()
    replica2.inc()
    replica2.inc()
    return replica1, replica2


def test_both_converge(replicas):
    replica1, replica2 = replicas
    map(lambda x: replica1.apply(transmit(x)), replica2.deltas)
    map(lambda x: replica2.apply(transmit(x)), replica1.deltas)
    assert replica1 == 4
    assert replica2 == 4
