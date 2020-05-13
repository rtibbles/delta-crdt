from .base import CRDT
from .base import Tuple
from .base import mutator


class LWWReg(CRDT):
    @classmethod
    def initial(cls):
        return Tuple((0, None))

    @classmethod
    def join(cls, s1, s2):
        if s1[0] == s2[0] and s2[1] > s1[1]:
            return Tuple((s2[0], s2[1]))
        return Tuple((s2[0], s2[1])) if s2[0] > s1[0] else Tuple((s1[0], s1[1]))

    @classmethod
    def value(cls, state):
        return state[1]

    @mutator
    def write(self, ts, value):
        return Tuple((ts, value))
