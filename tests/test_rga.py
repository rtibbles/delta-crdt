import pytest

from delta_crdts.rga import RGA

from .helpers import transmit


@pytest.fixture
def rga():
    return RGA("test id")


def test_rga_can_be_created(rga):
    pass


def test_rga_starts_empty(rga):
    assert len(rga) == 0


def test_add_right(rga):
    rga.add_right(None, "a")
    assert rga == ["a"]


def test_append(rga):
    rga.append("a")
    assert rga[0] == "a"


def test_append_twice(rga):
    rga.append("a")
    assert rga[0] == "a"
    rga.append("b")
    assert rga[1] == "b"


def test_length(rga):
    rga.append("a")
    assert len(rga) == 1


def test_contains(rga):
    rga.append("a")
    assert "a" in rga


def test_contains_after_deleted_sequence(rga):
    rga.append("a")
    rga.append("b")
    rga.remove("a")
    assert "a" not in rga
    assert "b" in rga


def test_insert_after_deleted_sequence(rga):
    rga.append("a")
    rga.append("b")
    rga.append("c")
    assert rga == ["a", "b", "c"]
    rga.append("d")
    assert rga == ["a", "b", "c", "d"]
    del rga[1]
    assert rga == ["a", "c", "d"]
    del rga[1]
    assert rga == ["a", "d"]
    rga.insert(2, "e")
    assert rga == ["a", "d", "e"]


def test_insert_after_updated_sequence(rga):
    rga.append("a")
    rga.append("b")
    rga.append("c")
    assert rga == ["a", "b", "c"]
    rga.append("d")
    assert rga == ["a", "b", "c", "d"]
    rga[1] = "g"
    assert rga == ["a", "g", "c", "d"]
    rga.insert(2, "e")
    assert rga == ["a", "g", "e", "c", "d"]


def test_extend(rga):
    rga.extend(["a", "b"])
    assert rga == ["a", "b"]


@pytest.fixture
def replicas():
    replica1 = RGA("test id 1")
    replica2 = RGA("test id 2")
    deltas1 = []
    deltas1.append(replica1.append("a"))
    deltas1.append(replica1.append("b"))
    deltas2 = []
    deltas2.append(replica2.append("c"))
    deltas2.append(replica2.append("d"))
    return replica1, replica2, deltas1, deltas2


def test_replica_can_handle_diffs_from_another(replicas):
    replica1, replica2, deltas1, deltas2 = replicas
    replica1.apply(transmit(deltas2[0]))
    assert replica1 == ["c", "a", "b"]
    replica1.apply(transmit(deltas2[1]))
    assert replica1 == ["c", "d", "a", "b"]


def test_replica_can_handle_repeated_diffs(replicas):
    replica1, replica2, deltas1, deltas2 = replicas
    replica1.apply(transmit(deltas2[0]))
    assert replica1 == ["c", "a", "b"]
    replica1.apply(transmit(deltas2[1]))
    assert replica1 == ["c", "d", "a", "b"]
    replica1.apply(transmit(deltas2[0]))
    assert replica1 == ["c", "d", "a", "b"]
    replica1.apply(transmit(deltas2[1]))
    assert replica1 == ["c", "d", "a", "b"]


def test_can_reapply_own_diffs(rga):
    delta = rga.extend(["a", "b"])
    assert rga == ["a", "b"]
    rga.apply(delta)
    assert rga == ["a", "b"]


def test_both_replicas_converge(replicas):
    replica1, replica2, deltas1, deltas2 = replicas
    replica1.apply(transmit(deltas2[0]))
    replica1.apply(transmit(deltas2[1]))
    replica2.apply(transmit(deltas1[0]))
    replica2.apply(transmit(deltas1[1]))
    assert replica1 == replica2
    assert replica2 == ["c", "d", "a", "b"]


@pytest.fixture
def deletion(replicas):
    replica1, replica2, deltas1, deltas2 = replicas
    replica1.apply(transmit(deltas2[0]))
    replica1.apply(transmit(deltas2[1]))
    replica2.apply(transmit(deltas1[0]))
    replica2.apply(transmit(deltas1[1]))
    deltas1 = [replica1.remove_at(1)]
    deltas2 = [replica2.remove_at(2)]
    return replica1, replica2, deltas1, deltas2


def test_can_delete_concurrently(deletion):
    replica1, replica2, deltas1, deltas2 = deletion
    assert replica1 == ["c", "a", "b"]
    assert replica2 == ["c", "d", "b"]


def test_deletion_converges(deletion):
    replica1, replica2, deltas1, deltas2 = deletion
    replica1.apply(transmit(deltas2[0]))
    replica2.apply(transmit(deltas1[0]))
    assert replica1 == ["c", "b"]
    assert replica2 == ["c", "b"]


@pytest.fixture
def further(deletion):
    replica1, replica2, deltas1, deltas2 = deletion
    replica1.apply(transmit(deltas2[0]))
    replica2.apply(transmit(deltas1[0]))
    deltas1 = []
    deltas2 = []
    deltas1.append(replica1.append("e"))
    deltas1.append(replica1.append("f"))
    deltas2.append(replica2.append("g"))
    deltas2.append(replica2.append("h"))
    replica1.apply(transmit(deltas2[0]))
    replica1.apply(transmit(deltas2[1]))
    replica2.apply(transmit(deltas1[0]))
    replica2.apply(transmit(deltas1[1]))
    return replica1, replica2, deltas1, deltas2


def test_can_add_further_after_deletion(further):
    replica1, replica2, deltas1, deltas2 = further
    assert replica1 == replica2
    assert replica2 == ["c", "b", "g", "h", "e", "f"]


def test_can_join_two_deltas(further):
    replica1, replica2, deltas1, deltas2 = further
    deltaBuffer1 = [replica1.append("k"), replica1.append("l")]
    deltaBuffer2 = [replica2.append("m"), replica2.append("n")]
    delta1 = replica1.join(deltaBuffer1[0], deltaBuffer1[1])
    delta2 = replica2.join(deltaBuffer2[0], deltaBuffer2[1])
    replica1.apply(transmit(delta2))
    replica2.apply(transmit(delta1))
    assert replica1 == ["c", "b", "g", "h", "e", "f", "m", "n", "k", "l"]
    assert replica1 == replica2


def test_can_reapply_entire_state(further):
    replica1, replica2, deltas1, deltas2 = further
    replica1.apply(transmit(replica1.state))
    replica2.apply(transmit(replica2.state))
    assert replica1 == replica2
    assert replica2 == ["c", "b", "g", "h", "e", "f"]


def test_can_insert_multiple(further):
    replica1, replica2, deltas1, deltas2 = further
    replica1.insert(1, "X", "Y", "Z")
    assert replica1 == ["c", "X", "Y", "Z", "b", "g", "h", "e", "f"]


def test_ids_give_consistent_order():
    replica1 = RGA("a")
    replica2 = RGA("b")
    delta_a = replica1.append("a")
    replica2.append("b")
    replica2.apply(delta_a)
    assert replica2 == ["b", "a"]
    replica3 = RGA("d")
    replica4 = RGA("c")
    replica3.append("d")
    delta_d = replica4.append("c")
    replica3.apply(delta_d)
    assert replica3 == ["d", "c"]


@pytest.fixture
def missing_state():
    replica1 = RGA("id1")
    replica1.append("a")
    replica1.append("b")
    replica1.append("c")
    state1 = replica1.state
    replica2 = RGA("id2")
    replica2.append("d")
    replica2.append("e")
    replica2.append("f")
    state2 = replica2.state
    replica3 = RGA("id3")
    replica3.apply(state1)
    replica3.apply(state2)
    delta3 = replica3.insert(3, "X")
    delta4 = replica3.append("Y")
    return state1, state2, delta3, delta4


def test_states_and_deltas_applied_in_order(missing_state):
    state1, state2, delta3, delta4 = missing_state
    replica = RGA("id")
    replica.apply(state1)
    replica.apply(state2)
    replica.apply(delta3)
    replica.apply(delta4)
    assert replica == ["d", "e", "f", "X", "a", "b", "c", "Y"]


def test_states_and_deltas_applied_in_modified_order(missing_state):
    state1, state2, delta3, delta4 = missing_state
    replica = RGA("id")
    replica.apply(state2)
    replica.apply(state1)
    replica.apply(delta4)
    replica.apply(delta3)
    assert replica == ["d", "e", "f", "X", "a", "b", "c", "Y"]


def test_states_and_deltas_applied_deltas_early(missing_state):
    state1, state2, delta3, delta4 = missing_state
    replica = RGA("id")
    replica.apply(state2)
    replica.apply(delta3)
    replica.apply(state1)
    replica.apply(delta4)
    assert replica == ["d", "e", "f", "X", "a", "b", "c", "Y"]
