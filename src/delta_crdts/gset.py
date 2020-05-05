try:
    from collections.abc import MutableSet
except ImportError:
    from collections import MutableSet

from .base import CRDT
from .base import Set
from .base import mutator


class GSet(CRDT, MutableSet):
    @classmethod
    def initial(self):
        return Set()

    @classmethod
    def join(cls, s1, s2):
        return s1.union(s2)

    @classmethod
    def value(cls, state):
        return set(state)

    def __eq__(self, other):
        return not self.state.difference(other)

    def __iter__(self):
        for item in self._value_cache:
            yield item

    def __contains__(self, item):
        return item in self._value_cache

    def __len__(self):
        return len(self._value_cache)

    @mutator
    def add(self, value):
        return Set([value])

    def discard(self, value):
        raise NotImplementedError("Growth only set does not support removing elements")
