try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

from .base import CRDT
from .base import EmbeddableCRDT
from .base import Map
from .base import get_crdt_type
from .base import has_mutator
from .base import mutator
from .causal_context import CausalContext
from .dot_map import DotMap


class ORMap(EmbeddableCRDT, MutableMapping):
    @classmethod
    def initial(cls):
        return DotMap()

    @classmethod
    def join(cls, s1, s2):
        return DotMap.join(s1, s2)

    @classmethod
    def value(cls, state):
        result = {}
        for key, sub_state in state.items():
            if hasattr(sub_state, "is_bottom") and sub_state.is_bottom():
                continue
            crdt_type = get_crdt_type(sub_state.type_id)
            result[key] = crdt_type.value(sub_state)

        return result

    @classmethod
    def _create_delta_from_child(cls, key, delta):
        cc = getattr(delta, "cc", CausalContext())
        delta = DotMap(cc, Map([(key, delta)]))
        delta.type_id = cls.type_id
        return delta

    def propagate_delta(self, sub_item, delta):
        delta = self._create_delta_from_child(sub_item.key, delta)
        self.apply(delta)

    @mutator
    def apply_sub(self, key, type_name, mutator_name, *args):
        crdt_type = get_crdt_type(type_name)
        if not issubclass(crdt_type, CRDT):
            raise TypeError("ORMap can only embed CRDT types")
        has_mutator(crdt_type, mutator_name)
        sub_item = crdt_type(self.id, state=self.state.get(key))
        sub_item.cc = self.state.cc
        delta = getattr(sub_item, mutator_name)(*args)
        return self._create_delta_from_child(key, delta)

    def _remove_by_key(self, key):
        sub_state = self.state[key]
        try:
            dots = sub_state.dots()
        except AttributeError:
            dots = None
        new_cc = CausalContext(dots)

        crdt_type = get_crdt_type(sub_state.type_id)

        return DotMap(new_cc, Map([(key, crdt_type.initial())]))

    @mutator
    def remove(self, key):
        return self._remove_by_key

    def __iter__(self):
        for key in self._value_cache:
            yield key

    def __contains__(self, key):
        return key in self._value_cache

    def __len__(self):
        return len(self._value_cache)

    def __getitem__(self, key):
        sub_state = self.state[key]
        crdt_type = get_crdt_type(sub_state.type_id)
        sub_item = crdt_type(self.id, state=sub_state)
        sub_item.cc = self.state.cc
        sub_item.parent = self
        sub_item.key = key
        return sub_item

    @mutator
    def __delitem__(self, key):
        return self._remove_by_key

    @mutator
    def __setitem__(self, key, value):
        if not isinstance(value, CRDT):
            raise TypeError("ORMap can only embed CRDT types")
        sub_state = self.state.get(key)
        try:
            dots = sub_state.dots()
        except AttributeError:
            dots = None
        new_cc = CausalContext(dots)

        return DotMap(new_cc, Map([(key, value.state)]))
