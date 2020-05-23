import json

from .base import BaseMap
from .base import Map
from .base import Set
from .base import StateContainer
from .causal_context import CausalContext
from .object_hash import get_object_key


class DotSet(BaseMap, StateContainer):
    msgpack_code = 67

    def __init__(self, ds=None, cc=None, **kwargs):
        if isinstance(cc, CausalContext):
            self.cc = cc
        else:
            self.cc = CausalContext(**(cc or {}))
        if isinstance(ds, Map):
            self._state = ds
        else:
            self._state = Map(*(ds or []))
        self.type = kwargs.pop("type", None)

    def to_init(self):
        return {
            "cc": {"cc": self.cc.cc, "dc": self.cc.dc} if self.cc else None,
            "ds": self._state,
            "type": self.type,
        }

    def dots(self):
        return Set(map(self.dot_for_key, self._state.keys()))

    def is_bottom(self):
        return len(self._state) == 0

    @classmethod
    def key_for_dot(cls, dot):
        return json.dumps(dot)

    @classmethod
    def dot_for_key(cls, key):
        return tuple(json.loads(key))

    def add(self, identifier, value):
        dot, dot_key = self.dot_add(identifier, value)

        res_ds = Map()
        res_ds[dot_key] = value
        res_cc = CausalContext()
        res_cc.insert_dot(dot[0], dot[1])

        return DotSet(res_ds, res_cc)

    def dot_add(self, identifier, value):
        dot = self.cc.next(identifier)
        dot_key = self.key_for_dot(dot)
        return dot, dot_key

    def remove_value(self, value):
        res = DotSet()
        value_key = get_object_key(value)
        for dot_key, value in self.items():
            current_value_key = get_object_key(value)
            if current_value_key == value_key:
                res.cc.insert_dot(self.dot_for_key(dot_key))
        res.cc.compact()
        return res

    def remove_dot(self, dot):
        dot_key = self.key_for_dot(dot)
        value = self._state.get(dot_key)
        res = DotSet()
        if value:
            res.cc.insert_dot(dot[0], dot[1])
        res.cc.compact()
        return res

    def remove_all(self):
        res = DotSet()
        for key in self._state:
            dot = self.dot_for_key(key)
            res.cc.insert_dot(dot[0], dot[1])
        # clear payload, but retain context
        self._state = Map()

        res.cc.compact()
        return res

    @classmethod
    def join(cls, s1, s2, *args):
        keys = Set(s1.keys()).union(Set(s2.keys()))

        # clone map so that we return something immutable
        ds = s1._state.copy()
        cc = s1.cc.join(s2.cc)

        for key in keys:
            dot = cls.dot_for_key(key)
            if key not in s2:
                if key in s1 and s2.cc.dot_in(dot):
                    del ds[key]
            elif key not in s1:
                # we don't have it
                if not s1.cc.dot_in(dot):
                    ds[key] = s2.get(key)
            else:
                # in both
                ds[key] = ds.get(key) or s2.get(key)

        result = DotSet(ds, cc, type=s1.type or s2.type)

        if args:
            return cls.join(result, args[0], *args[1:])

        return result
