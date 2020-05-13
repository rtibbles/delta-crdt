from .dot_set import DotSet
from .base import CausalCRDT
from .base import mutator


class CCounter(CausalCRDT):
    @classmethod
    def initial(cls):
        return DotSet()

    @classmethod
    def join(cls, s1, s2):
        return DotSet.join(s1, s2)

    @classmethod
    def value(cls, state):
        return sum(state.values())

    def mutate_for(self):
        r = DotSet()
        base = 0
        for key, value in self.state.items():
            dot = DotSet.dot_for_key(key)
            dot_id = dot[0]
            if self.id == dot_id:
                base = max(base, value)
                r = r.join(r, self.state.remove_dot(dot))

        return r, base

    @mutator
    def inc(self, by=1):
        r, base = self.mutate_for()
        return r.join(r, self.state.add(self.id, base + by))

    @mutator
    def dec(self, by=1):
        r, base = self.mutate_for()
        return r.join(r, self.state.add(self.id, base - by))
