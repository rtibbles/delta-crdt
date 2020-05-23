from .base import CRDT
from .base import CRDTSetMixin
from .base import Set
from .base import mutator


class GSet(CRDT, CRDTSetMixin):
    @classmethod
    def initial(self):
        return Set()

    @classmethod
    def join(cls, s1, s2):
        return s1.union(s2)

    @classmethod
    def value(cls, state):
        return Set(state)

    @mutator
    def add(self, value):
        return Set([value])

    def remove(self, value):
        raise NotImplementedError("Growth only set does not support removing elements")
