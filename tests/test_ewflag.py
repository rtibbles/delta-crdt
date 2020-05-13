import pytest

from delta_crdts import EWFlag
from .helpers import transmit


@pytest.fixture
def ewflag():
    return EWFlag("test id 1")


def test_can_create(ewflag):
    pass


def test_starts_as_false(ewflag):
    assert not ewflag


def test_can_enable(ewflag):
    ewflag.enable()
    assert ewflag


@pytest.fixture
def replicas():
    replica1 = EWFlag("test id 1")
    replica2 = EWFlag("test id 2")
    replica1.enable()
    replica1.disable()
    replica2.disable()
    replica2.enable()
    return replica1, replica2


def test_both_converge(replicas):
    replica1, replica2 = replicas
    map(lambda x: replica1.apply(transmit(x)), replica2.deltas)
    map(lambda x: replica2.apply(transmit(x)), replica1.deltas)
    assert replica1
    assert replica2
