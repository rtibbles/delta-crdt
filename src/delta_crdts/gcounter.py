from .base import CRDT
from .base import Map
from .base import mutator


class GCounter(CRDT):
    @classmethod
    def initial(cls):
        return Map()

    @classmethod
    def value(cls, state):
        return sum(state.values())

    @classmethod
    def join(cls, s1, s2):
        res = Map()
        for key in set(s1.keys()).union(s2.keys()):
            res[key] = max(s1.get(key, 0), s2.get(key, 0))
        return res

    @mutator
    def inc(self):
        return Map([(self.id, self.state.get(self.id, 0) + 1)])
