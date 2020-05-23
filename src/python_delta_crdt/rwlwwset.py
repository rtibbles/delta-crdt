from .base import CausalCRDT
from .base import CRDTSetMixin
from .base import Map
from .base import Set
from .base import mutator
from .object_hash import get_object_key


def add_remove(ts, b, val):
    res = Map()
    key = get_object_key(val)
    res[key] = (ts, b, val)

    return res


class RWLWWSet(CausalCRDT, CRDTSetMixin):
    @classmethod
    def initial(cls):
        return Map()

    @classmethod
    def join(cls, s1, s2):
        ret = Map()
        for key in set(s1.keys()).union(set(s2.keys())):
            left = s1.get(key)
            right = s2.get(key)
            if not left:
                ret[key] = right
            elif not right:
                ret[key] = left
            else:

                if left[0] > right[0]:
                    ret[key] = left
                elif right[0] > left[0]:
                    ret[key] = right
                else:
                    ret[key] = (left[0],) + (
                        left[1:] if left[1:] >= right[1:] else right[1:]
                    )

        return ret

    @classmethod
    def value(cls, state):
        res = Set()
        for _, b, value in state.values():
            if not b:
                res.add(value)
        return res

    @mutator
    def add(self, ts, value):
        return add_remove(ts, False, value)

    @mutator
    def remove(self, ts, value):
        return add_remove(ts, True, value)
