from .base import CausalCRDT
from .base import CRDTSetMixin
from .base import Set
from .base import mutator
from .dot_set import DotSet


class RWORSet(CausalCRDT, CRDTSetMixin):
    @classmethod
    def initial(cls):
        return DotSet()

    @classmethod
    def join(cls, s1, s2):
        return DotSet.join(s1, s2)

    @classmethod
    def value(cls, state):
        ret = Set()
        for value, keep in state.values():
            if keep:
                ret.add(value)
            else:
                ret.discard(value)

        return ret

    @mutator
    def add(self, value):
        return DotSet.join(
            self.state.remove_value((value, True)),
            self.state.remove_value((value, False)),
            self.state.add(self.id, (value, True)),
        )

    @mutator
    def remove(self, value):
        return DotSet.join(
            self.state.remove_value((value, True)),
            self.state.remove_value((value, False)),
            self.state.add(self.id, (value, False)),
        )
