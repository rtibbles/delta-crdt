import pytest

from delta_crdt import LexCounter
from .helpers import transmit


@pytest.fixture
def lexcounter():
    return LexCounter("test id 1")


def test_can_create(lexcounter):
    pass


def test_starts_with_value_zero(lexcounter):
    assert lexcounter == 0


def test_can_inc(lexcounter):
    lexcounter.inc()
    assert lexcounter == 1


def test_can_dec(lexcounter):
    lexcounter.dec()
    assert lexcounter == -1


@pytest.fixture
def replicas():
    replica1 = LexCounter("test id 1")
    replica2 = LexCounter("test id 2")
    replica1.inc()
    replica1.inc()
    replica1.dec()
    replica2.inc()
    replica2.inc()
    replica2.dec()
    return replica1, replica2


def test_both_converge(replicas):
    replica1, replica2 = replicas

    assert replica1 == 1
    assert replica2 == 1

    map(lambda x: replica1.apply(transmit(x)), replica2.deltas)
    map(lambda x: replica2.apply(transmit(x)), replica1.deltas)
    assert replica1 == 2
    assert replica2 == 2
