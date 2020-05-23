import pytest

from delta_crdt import CCounter
from .helpers import transmit


@pytest.fixture
def ccounter():
    return CCounter("test id 1")


def test_can_create(ccounter):
    pass


def test_starts_with_value_zero(ccounter):
    assert ccounter == 0


def test_can_inc(ccounter):
    ccounter.inc()
    assert ccounter == 1


def test_can_dec(ccounter):
    ccounter.dec()
    assert ccounter == -1


@pytest.fixture
def replicas():
    replica1 = CCounter("test id 1")
    replica2 = CCounter("test id 2")
    replica1.inc(2)
    replica1.dec()
    replica1.inc(2)
    replica2.inc()
    replica2.dec()
    replica2.inc()
    return replica1, replica2


def test_changes_can_be_raw_joined(replicas):
    replica1, replica2 = replicas
    state = CCounter.join(transmit(replica1.state), transmit(replica2.state))
    replica = CCounter("replica")
    replica.apply(state)
    assert replica == 4


def test_both_converge(replicas):
    replica1, replica2 = replicas
    map(lambda x: replica1.apply(transmit(x)), replica2.deltas)
    map(lambda x: replica2.apply(transmit(x)), replica1.deltas)
    assert replica1 == 4
    assert replica2 == 4
