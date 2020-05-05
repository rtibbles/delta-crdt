import pytest

from delta_crdts.causal_context import CausalContext


@pytest.fixture
def context():
    return CausalContext()


def test_can_create(context):
    pass


def test_empty_when_initialized(context):
    assert ("a", 1) not in context


def test_can_make_dot(context):
    context.make_dot("a")
    assert ("a", 1) in context


def test_can_make_dot_and_higher_dot_not_in(context):
    context.make_dot("a")
    assert ("a", 2) not in context


def test_can_make_dot_and_insert_higher_dot(context):
    context.make_dot("a")
    context.insert_dot("a", 2)
    assert ("a", 1) in context
    assert ("a", 2) in context
    assert ("a", 3) not in context


def test_can_compact_compact_preserves(context):
    context.make_dot("a")
    context.insert_dot("a", 2)
    context.compact()
    assert ("a", 1) in context
    assert ("a", 2) in context
    assert ("a", 3) not in context


def test_can_join_two_contexts(context):
    other_context = CausalContext()
    other_context.insert_dot("a", 1)
    other_context.insert_dot("b", 2)
    context.make_dot("a")
    context.insert_dot("a", 2)
    result = context.join(other_context)
    assert ("a", 1) in result
    assert ("a", 2) in result
    assert ("a", 3) not in result
    assert ("b", 1) in result
    assert ("b", 2) in result
    assert ("b", 3) not in result
