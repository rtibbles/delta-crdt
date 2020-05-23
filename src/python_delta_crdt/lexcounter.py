from .base import CRDT
from .base import Map
from .base import mutator


class LexCounter(CRDT):
    @classmethod
    def initial(cls):
        return Map()

    @classmethod
    def join(cls, s1, s2):
        res = Map()

        for key in set(s1.keys()).union(set(s2.keys())):

            left = s1.get(key)
            right = s2.get(key)
            if not left:
                res[key] = right
            elif not right:
                res[key] = left
            else:
                if left[0] > right[0]:
                    res[key] = left
                elif right[0] > left[0]:
                    res[key] = right
                else:
                    res[key] = (left[0], max(left[1], right[1]))

        return res

    @classmethod
    def value(cls, state):
        return sum((value[1] for value in state.values()))

    @mutator
    def inc(self):
        existing = self.state.get(self.id, (0, 0))
        return Map(**{self.id: (existing[0], existing[1] + 1)})

    @mutator
    def dec(self):
        existing = self.state.get(self.id, (0, 0))
        return Map(**{self.id: (existing[0] + 1, existing[1] - 1)})
