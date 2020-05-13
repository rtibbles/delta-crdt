from .base import CausalCRDT
from .base import mutator
from .dot_set import DotSet


class EWFlag(CausalCRDT):
    # Define both __bool__ and __nonzero__ for Py2/3 compatibility
    def __bool__(self):
        return self._value_cache

    def __nonzero__(self):
        return self._value_cache

    @classmethod
    def initial(cls):
        return DotSet()

    @classmethod
    def join(cls, s1, s2):
        return DotSet.join(s1, s2)

    @classmethod
    def value(cls, state):
        return bool(state)

    @mutator
    def enable(self):
        return self.state.join(
            self.state.remove_value(True), self.state.add(self.id, True)
        )

    @mutator
    def disable(self):
        return self.state.remove_value(True)
