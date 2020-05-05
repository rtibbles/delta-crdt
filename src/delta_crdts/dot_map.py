try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

from itertools import chain

from .causal_context import CausalContext
from .base import Map
from .base import Set
from .base import StateContainer
from .base import get_crdt_type


def dot_map_from_raw(base):
    cc = None
    if hasattr(base, "cc") and hasattr(base.cc, "dc"):
        cc = CausalContext(base.cc.cc, base.cc.dc)
    state_from_raw = Map()
    for key in base.state.keys():
        value = base.state.get(key)
        crdt_type = get_crdt_type(value.type_id)
        state_from_raw[key] = crdt_type.join(value, crdt_type.initial())
        state_from_raw[key].type_id = value.type_id
    dot_map = DotMap(cc, state_from_raw)
    dot_map.type_id = base.type_id
    return dot_map


def sub_join(sub1, sub2):
    if sub1 is None:
        return sub2
    if sub2 is None:
        return sub1
    crdt_type = get_crdt_type(sub1.type_id or sub2.type_id)
    result = crdt_type.join(sub1, sub2)
    result.type_id = crdt_type.type_id
    return result


class DotMap(MutableMapping, StateContainer):
    def __init__(self, cc=None, state=None):
        self.cc = cc or CausalContext()
        self.__state = state or Map()

    def dots(self):
        return Set(chain(*map(lambda x: x.dots(), self.__state.values())))

    def is_bottom(self):
        return len(self.__state) == 0

    def compact(self):
        return DotMap(self.cc.compact(), self.__state)

    @classmethod
    def join(cls, dm1, dm2):
        if not isinstance(dm1, DotMap):
            dm1 = dot_map_from_raw(dm1)

        if not isinstance(dm2, DotMap):
            dm2 = dot_map_from_raw(dm2)

        new_causal_context = dm1.cc.join(dm2.cc)
        new_map = Map()

        for key in set(dm1.keys()).union(set(dm2.keys())):
            sub1 = dm1.get(key)
            if sub1:
                sub1.cc = dm1.cc

            sub2 = dm2.get(key)
            if sub2:
                sub2.cc = dm2.cc

            new_sub = sub_join(sub1, sub2)

            new_sub.cc = None
            new_map[key] = new_sub

        result = DotMap(new_causal_context, new_map)
        result.type_id = dm1.type_id or (dm2 and dm2.type_id)

        return result

    def __getitem__(self, key):
        return self.__state[key]

    def __setitem__(self, key, value):
        self.__state[key] = value

    def __delitem__(self, key):
        del self.__state[key]

    def __iter__(self):
        return iter(self.__state)

    def __len__(self):
        return len(self.__state)

    def __contains__(self, item):
        return item in self.__state

    def update(self, d):
        self.__state.update(d)

    def copy(self):
        new_map = Map()
        new_map.__state = self.__state.copy()
        return new_map

    def get(self, item, default=None):
        return self.__state.get(item, default)

    def items(self):
        return self.__state.items()

    def keys(self):
        return self.__state.keys()
