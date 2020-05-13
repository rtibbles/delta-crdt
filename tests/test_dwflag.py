import pytest

from delta_crdts import DWFlag
from .helpers import transmit


@pytest.fixture
def dwflag():
    return DWFlag("test id 1")


def test_can_create(dwflag):
    pass


def test_starts_as_true(dwflag):
    assert dwflag


def test_can_disable(dwflag):
    dwflag.disable()
    assert not dwflag


@pytest.fixture
def replicas():
    replica1 = DWFlag("test id 1")
    replica2 = DWFlag("test id 2")
    replica1.enable()
    replica1.disable()
    replica2.disable()
    replica2.enable()
    return replica1, replica2


def test_both_converge(replicas):
    replica1, replica2 = replicas
    map(lambda x: replica1.apply(transmit(x)), replica2.deltas)
    map(lambda x: replica2.apply(transmit(x)), replica1.deltas)
    assert not replica1
    assert not replica2
