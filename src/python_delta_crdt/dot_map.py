try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

from itertools import chain

from .causal_context import CausalContext
from .base import BaseMap
from .base import Map
from .base import Set
from .base import StateContainer
from .base import get_crdt_type


class DotMap(BaseMap, StateContainer):
    msgpack_code = 66

    def __init__(self, cc=None, state=None, **kwargs):
        if isinstance(cc, CausalContext):
            self.cc = cc
        else:
            self.cc = CausalContext(**(cc or {}))

        self._state = Map(**self._generate_state(state)) if state else Map()
        self.type = kwargs.pop("type", None)

    def _generate_state(self, state):
        if isinstance(state, Mapping):
            state = state.items()
        if state is None:
            state = {}
        output_state = {}
        for key, value in state:
            if isinstance(value, StateContainer):
                output_state[key] = value.copy()
            else:
                type_id = value.get("type")
                if type_id:
                    # Handle badly formed state that may have come
                    # from a non-causal CRDT being embedded in a causal one
                    crdt_type = get_crdt_type(type_id)
                    substate = crdt_type.join(value, crdt_type.initial())
                    substate.type = type_id
                    output_state[key] = substate
        return output_state

    def to_init(self):
        return {
            "cc": {"cc": self.cc.cc, "dc": self.cc.dc} if self.cc else None,
            "state": self._state,
            "type": self.type,
        }

    def dots(self):
        return Set(chain(*map(lambda x: x.dots(), self._state.values())))

    def is_bottom(self):
        return len(self._state) == 0

    def compact(self):
        return DotMap(self.cc.compact(), self._state)

    @classmethod
    def join(cls, dm1, dm2):
        new_causal_context = dm1.cc.join(dm2.cc)
        new_map = {}

        for key in set(dm1.keys()).union(set(dm2.keys())):
            sub1 = dm1.get(key)
            if sub1:
                sub1.cc = dm1.cc

            sub2 = dm2.get(key)
            if sub2:
                sub2.cc = dm2.cc

            new_sub = None
            if sub1 and sub2:
                crdt_type = get_crdt_type(sub1.type or sub2.type)
                new_sub = crdt_type.join(sub1, sub2)
            elif sub1 is not None:
                new_sub = sub1
            elif sub2 is not None:
                new_sub = sub2

            new_sub.cc = None
            new_map[key] = new_sub

        result = DotMap(
            new_causal_context, new_map, type=dm1.type or (dm2 and dm2.type)
        )

        return result
