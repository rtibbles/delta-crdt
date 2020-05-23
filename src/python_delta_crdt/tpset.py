from .base import CRDT
from .base import CRDTSetMixin
from .base import Set
from .base import Tuple
from .base import mutator


class TPSet(CRDT, CRDTSetMixin):
    # Can't name the class this, so explicitly set the type_id
    type_id = "2pset"

    @classmethod
    def initial(cls):
        return Tuple((Set(), Set()))

    @classmethod
    def value(cls, state):
        return Set(state[0])

    @classmethod
    def join(cls, s1, s2):
        removed = s1[1].union(s2[1])
        added = s1[0].union(s2[0]).difference(removed)

        return Tuple((added, removed))

    @mutator
    def add(self, value):
        if value not in self.state[0]:
            return Tuple((Set([value]), Set()))
        return self.initial()

    @mutator
    def remove(self, value):
        return Tuple((Set(), Set([value])))
