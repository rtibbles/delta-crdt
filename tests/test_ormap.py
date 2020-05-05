import pytest

from delta_crdts import ORMap
from .helpers import transmit


@pytest.fixture
def ormap():
    return ORMap("test id 1")


def test_can_create(ormap):
    pass


def test_starts_empty(ormap):
    assert len(ormap) == 0


def test_can_embed_non_causal_crdt(ormap):
    ormap.apply_sub("b", "gset", "add", "B")
    ormap["b"] == set("B")


def test_can_modify_embedded_crdt(ormap):
    ormap.apply_sub("b", "gset", "add", "B")
    embedded = ormap["b"]
    embedded.add("a")
    ormap["b"] == set(["B", "a"])


@pytest.fixture
def replicas():
    replica1 = ORMap("test id 1")
    replica2 = ORMap("test id 2")
    deltas1 = []
    deltas2 = []
    deltas1.append(replica1.apply_sub("a", "gset", "add", "A"))
    deltas1.append(replica1.apply_sub("b", "gset", "add", "B"))
    deltas1.append(replica1.apply_sub("c", "gset", "add", "C"))
    deltas2.append(replica2.apply_sub("a", "gset", "add", "D"))
    deltas2.append(replica2.apply_sub("b", "gset", "add", "E"))
    deltas2.append(replica2.apply_sub("c", "gset", "add", "F"))
    return replica1, replica2, deltas1, deltas2


def test_values_applied(replicas):
    replica1, replica2, deltas1, deltas2 = replicas
    assert replica1["a"] == set("A")
    assert replica1["b"] == set("B")
    assert replica1["c"] == set("C")
    assert replica2["a"] == set("D")
    assert replica2["b"] == set("E")
    assert replica2["c"] == set("F")


def test_values_can_be_joined(replicas):
    replica1, replica2, deltas1, deltas2 = replicas
    state = ORMap.join(replica1.state, replica2.state)
    new = ORMap("new")
    new.apply(state)
    assert new["a"] == set(["A", "D"])
    assert new["b"] == set(["B", "E"])
    assert new["c"] == set(["C", "F"])


def test_can_transmit(replicas):
    replica1, replica2, deltas1, deltas2 = replicas
    map(lambda x: replica1.apply(transmit(x)), deltas2)
    map(lambda x: replica2.apply(transmit(x)), deltas1)
    assert replica1["a"] == set(["A", "D"])
    assert replica1["b"] == set(["B", "E"])
    assert replica1["c"] == set(["C", "F"])
    assert replica2["a"] == set(["A", "D"])
    assert replica2["b"] == set(["B", "E"])
    assert replica2["c"] == set(["C", "F"])
