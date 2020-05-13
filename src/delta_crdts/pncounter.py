from .base import CRDT
from .base import Map
from .base import mutator
from .base import Tuple
from .gcounter import GCounter


class PNCounter(CRDT):
    @classmethod
    def initial(cls):
        return Tuple((GCounter.initial(), GCounter.initial()))

    @classmethod
    def value(cls, state):
        return GCounter.value(state[0]) - GCounter.value(state[1])

    @classmethod
    def join(cls, s1, s2):
        return Tuple((GCounter.join(s1[0], s2[0]), GCounter.join(s1[1], s2[1])))

    @mutator
    def inc(self):
        return Tuple(
            (Map([(self.id, self.state[0].get(self.id, 0) + 1)]), self.state[1])
        )

    @mutator
    def dec(self):
        return Tuple(
            (self.state[0], Map([(self.id, self.state[1].get(self.id, 0) + 1)]))
        )
