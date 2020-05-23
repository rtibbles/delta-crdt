import pytest

from delta_crdt.dot_set import DotSet
from delta_crdt import ORMap
from .helpers import transmit


@pytest.fixture
def ormap():
    return ORMap("test id 1")


def test_can_create(ormap):
    pass


def test_starts_empty(ormap):
    assert len(ormap) == 0


def test_cannot_embed_non_causal_crdt(ormap):
    try:
        ormap.apply_sub("b", "gset", "add", "B")
        assert False
    except TypeError:
        assert True


def test_can_modify_embedded_crdt(ormap):
    ormap.apply_sub("b", "ccounter", "inc")
    embedded = ormap["b"]
    embedded.inc()
    embedded == 2


@pytest.fixture
def replicas():
    replica1 = ORMap("test id 1")
    replica2 = ORMap("test id 2")
    replica1.apply_sub("a", "mvreg", "write", "A")
    replica1.apply_sub("b", "mvreg", "write", "B")
    replica1.apply_sub("c", "mvreg", "write", "C")
    replica2.apply_sub("a", "mvreg", "write", "a")
    replica2.apply_sub("b", "mvreg", "write", "b")
    replica2.apply_sub("c", "mvreg", "write", "c")
    return replica1, replica2


def test_values_applied(replicas):
    replica1, replica2 = replicas
    assert replica1["a"] == set("A")
    assert replica1["b"] == set("B")
    assert replica1["c"] == set("C")
    assert replica2["a"] == set("a")
    assert replica2["b"] == set("b")
    assert replica2["c"] == set("c")


def test_values_can_be_joined(replicas):
    replica1, replica2 = replicas
    state = ORMap.join(replica1.state, replica2.state)
    new = ORMap("new")
    new.apply(state)
    assert new["a"] == set(["A", "a"])
    assert new["b"] == set(["B", "b"])
    assert new["c"] == set(["C", "c"])


def test_can_transmit(replicas):
    replica1, replica2 = replicas
    for delta in replica2.deltas:
        replica1.apply(transmit(delta))
    for delta in replica1.deltas:
        replica2.apply(transmit(delta))
    assert replica1["a"] == set(["A", "a"])
    assert replica1["b"] == set(["B", "b"])
    assert replica1["c"] == set(["C", "c"])
    assert replica2["a"] == set(["A", "a"])
    assert replica2["b"] == set(["B", "b"])
    assert replica2["c"] == set(["C", "c"])


def test_causality_is_preserved(replicas):
    replica1, replica2 = replicas
    delta = replica1.apply_sub("a", "mvreg", "write", "AA")
    assert replica1["a"] == ["AA"]

    replica2.apply(delta)
    assert replica2["a"] == ["AA"]


def test_add_wins(replicas):
    replica1, replica2 = replicas
    delta1 = replica1.remove("b")
    assert "b" not in replica1
    delta2 = replica2.apply_sub("b", "mvreg", "write", "BB")
    assert replica2["b"] == ["BB"]
    replica1.apply(transmit(delta2))
    replica2.apply(transmit(delta1))
    assert replica2["b"] == ["BB"]
    assert replica1["b"] == ["BB"]
    assert isinstance(replica1.state.get("b"), DotSet)


def test_removals_stored_in_state(replicas):
    replica1, replica2 = replicas
    replica1.remove("b")
    assert "b" not in replica1
    replica2.apply(replica1.state)
    assert "b" not in replica2
