from abc import ABCMeta
from abc import abstractmethod

import operator

try:
    from collections.abc import Iterable
    from collections.abc import Mapping
    from collections.abc import MutableMapping
    from collections.abc import MutableSet
except ImportError:
    from collections import Iterable
    from collections import Mapping
    from collections import MutableMapping
    from collections import MutableSet

from six import with_metaclass

from .object_hash import get_object_key


_type_registry = {}


def get_crdt_type(name):
    name = str(name).lower()
    try:
        return _type_registry[name]
    except KeyError:
        raise TypeError("Unknown CRDT type: {}".format(name))


class CRDTMeta(ABCMeta):
    def __new__(cls, name, bases, attrs):
        global _type_registry
        new_class = super(CRDTMeta, cls).__new__(cls, name, bases, attrs)
        if hasattr(new_class, "type_id"):
            name = new_class.type_id
        # For consistency with the JS library, we store all identifiers in lower case.
        type_id = name.lower()
        new_class.type = type_id
        _type_registry[type_id] = new_class
        return new_class


class CRDT(with_metaclass(CRDTMeta)):
    def __init__(self, identifier, state=None):
        self.id = identifier
        self.state = state or self.initial()
        self.state.type = self.type
        self._value_cache = self.value(self.state)
        # Keep track of applied deltas to allow introspection
        # of updates that happen through Python attribute manipulation
        self.deltas = []

    def __repr__(self):
        return repr(self._value_cache)

    def __str__(self):
        return str(self._value_cache)

    def __len__(self):
        return len(self._value_cache)

    def __le__(self, other):
        return self._value_cache <= other

    def __lt__(self, other):
        return self._value_cache < other

    def __eq__(self, other):
        return self._value_cache == other

    def __ne__(self, other):
        return self._value_cache != other

    def __gt__(self, other):
        return self._value_cache > other

    def __ge__(self, other):
        return self._value_cache >= other

    def __and__(self, other):
        return self._value_cache & other

    def __or__(self, other):
        return self._value_cache | other

    def __invert__(self):
        return ~self._value_cache

    def __add__(self, other):
        return self._value_cache + other

    def __sub__(self, other):
        return self._value_cache - other

    def __mul__(self, other):
        return self._value_cache * other

    def __div__(self, other):
        return self._value_cache / other

    def __floordiv__(self, other):
        return self._value_cache // other

    def __mod__(self, other):
        return self._value_cache % other

    def __xor__(self, other):
        return self._value_cache ^ other

    @classmethod
    @abstractmethod
    def initial(self):
        pass

    def apply(self, delta):
        new_state = self.join(self.state, delta)
        new_state.type = self.type
        if hasattr(self, "incremental_value"):
            self._value_cache = self.incremental_value(
                self.state, new_state, delta, self._value_cache
            )
        else:
            self._value_cache = self.value(new_state)
        if getattr(self, "parent", None):
            self.parent.propagate_delta(self, delta)
        self.state = new_state
        self.deltas.append(delta)
        return self.state

    @classmethod
    @abstractmethod
    def join(cls, s1, s2):
        pass

    @classmethod
    @abstractmethod
    def value(cls, state):
        pass


class CRDTSetMixin(MutableSet):
    def __iter__(self):
        return iter(self._value_cache)

    def __contains__(self, item):
        return item in self._value_cache

    def __len__(self):
        return len(self._value_cache)

    def discard(self, item):
        try:
            return self.remove(item)
        except KeyError:
            pass


class CausalCRDT(CRDT):
    parent = None
    key = None


class EmbeddableCRDT(CausalCRDT):
    @abstractmethod
    def propagate_delta(self):
        pass


def mutator(func):
    def wrapper(self, *args, **kwargs):
        delta = func(self, *args, **kwargs)
        setattr(delta, "type", self.type)
        self.apply(delta)
        return delta

    setattr(wrapper, "mutator", True)

    return wrapper


def has_mutator(crdt_type, mutator_name):
    try:
        getattr(getattr(crdt_type, mutator_name), "mutator")
    except AttributeError:
        raise AttributeError(
            "{} has no mutator named {}".format(crdt_type.type, mutator_name)
        )


class StateMeta(ABCMeta):
    def __new__(cls, name, bases, attrs):
        new_class = super(StateMeta, cls).__new__(cls, name, bases, attrs)
        # Set type property here to avoid shadowing Python type global
        new_class.type = None
        return new_class


class StateContainer(with_metaclass(StateMeta)):
    msgpack_code = None

    def __repr__(self):
        return repr(self._state)

    def __str__(self):
        return str(self._state)

    @classmethod
    def factory(cls, init_args):
        if isinstance(init_args, Mapping):
            return cls(**init_args)
        return cls(*init_args)

    def copy(self):
        return self.factory(self.to_init())

    @abstractmethod
    def to_init(self):
        """
        Should return a representation of the state to a format that can be passed
        to the __init__ method of the class, useful for copying and encoding.
        """
        pass


class BaseMap(MutableMapping):
    def __getitem__(self, key):
        return self._state[key]

    def __setitem__(self, key, value):
        self._state[key] = value

    def __delitem__(self, key):
        del self._state[key]

    def __iter__(self):
        return iter(self._state)

    def __len__(self):
        return len(self._state)

    def __contains__(self, item):
        return item in self._state

    def keys(self):
        return self._state.keys()

    def values(self):
        return self._state.values()

    def items(self):
        return self._state.items()

    def update(self, d):
        self._state.update(d)

    def get(self, item, default=None):
        return self._state.get(item, default)


class Map(BaseMap, StateContainer):
    msgpack_code = 64

    def __init__(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise ValueError("Can only pass a single positional argument to Map")
            self._state = dict(args[0])
        else:
            self._state = dict(kwargs)

    @classmethod
    def factory(cls, init_args):
        return cls(init_args)

    def to_init(self):
        return self._state.items()


def check_comparator(other):
    if not isinstance(other, Iterable):
        raise NotImplementedError(
            "Can only compare Set to classes that derive from Python Iterable abstract base class"
        )
    if not isinstance(other, Set):
        other = Set(other)
    return other


class Set(MutableSet, StateContainer):
    msgpack_code = 65

    def __init__(self, iterable=None):
        self._state = {}
        for item in iterable or tuple():
            self.add(item)

    def __repr__(self):
        return repr(self._state.values())

    def __str__(self):
        return str(self._state.values())

    def __iter__(self):
        return iter(self._state.values())

    def __len__(self):
        return len(self._state)

    def __contains__(self, item):
        item_key = get_object_key(item)
        return item_key in self._state

    def __le__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) <= set(other._state.keys())

    def __lt__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) < set(other._state.keys())

    def __eq__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) == set(other._state.keys())

    def __ne__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) != set(other._state.keys())

    def __gt__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) > set(other._state.keys())

    def __ge__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) >= set(other._state.keys())

    def __and__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) & set(other._state.keys())

    def __or__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) | set(other._state.keys())

    def __invert__(self):
        return ~set(self._state.keys())

    def __add__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) + set(other._state.keys())

    def __sub__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) - set(other._state.keys())

    def __mul__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) * set(other._state.keys())

    def __div__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) / set(other._state.keys())

    def __floordiv__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) // set(other._state.keys())

    def __mod__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) % set(other._state.keys())

    def __xor__(self, other):
        other = check_comparator(other)
        return set(self._state.keys()) ^ set(other._state.keys())

    def isdisjoint(self, other):
        other = check_comparator(other)
        return set(self._state.keys()).isdisjoint(set(other._state.keys()))

    def add(self, item):
        item_key = get_object_key(item)
        self._state[item_key] = item

    def remove(self, item):
        item_key = get_object_key(item)
        del self._state[item_key]

    def discard(self, item):
        try:
            return self.remove(item)
        except KeyError:
            pass

    def union(self, other):
        return Set(tuple(self) + tuple(other))

    def difference(self, other):
        return Set((item for item in self if item not in other))

    @classmethod
    def factory(cls, init_args):
        return cls(init_args)

    def to_init(self):
        return tuple(self)


class Tuple(tuple, StateContainer):
    @classmethod
    def factory(cls, init_args):
        return cls(init_args)

    def to_init(self):
        return self
