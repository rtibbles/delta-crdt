from .base import CausalCRDT
from .base import CRDTSetMixin
from .base import Set
from .base import mutator
from .dot_set import DotSet


class AWORSet(CausalCRDT, CRDTSetMixin):
    @classmethod
    def initial(cls):
        return DotSet()

    @classmethod
    def join(cls, s1, s2):
        return DotSet.join(s1, s2)

    @classmethod
    def value(cls, state):
        return Set(state.values())

    @mutator
    def add(self, value):
        return DotSet.join(
            self.state.remove_value(value), self.state.add(self.id, value)
        )

    @mutator
    def remove(self, value):
        return self.state.remove_value(value)
