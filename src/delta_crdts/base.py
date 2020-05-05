from abc import ABCMeta
from abc import abstractmethod

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

from six import with_metaclass


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
        # For consistency with the JS library, we store all identifiers in lower case.
        type_id = name.lower()
        new_class.type_id = type_id
        _type_registry[type_id] = new_class
        return new_class


class CRDT(with_metaclass(CRDTMeta)):
    def __init__(self, identifier, state=None):
        self.id = identifier
        self.state = state or self.initial()
        self.state.type_id = self.type_id
        self._value_cache = self.value(self.state)

    @classmethod
    @abstractmethod
    def initial(self):
        pass

    def apply(self, delta):
        new_state = self.join(self.state, delta)
        new_state.type_id = self.type_id
        if hasattr(self, "incremental_value"):
            self._value_cache = self.incremental_value(
                self.state, new_state, delta, self._value_cache
            )
        else:
            self._value_cache = self.value(new_state)
        if getattr(self, "parent", None):
            self.parent.propagate_delta(self, delta)
        self.state = new_state
        return self.state

    @classmethod
    @abstractmethod
    def join(cls, s1, s2):
        pass

    @classmethod
    @abstractmethod
    def value(cls, state):
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
        setattr(delta, "type_id", self.type_id)
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


class StateContainer(object):
    type_id = None
    cc = None


class Map(MutableMapping, StateContainer):
    def __init__(self, *args, **kwargs):
        self.__store = dict(*args, **kwargs)

    def __getitem__(self, key):
        return self.__store[key]

    def __setitem__(self, key, value):
        self.__store[key] = value

    def __delitem__(self, key):
        del self.__store[key]

    def __iter__(self):
        return iter(self.__store)

    def __len__(self):
        return len(self.__store)

    def __contains__(self, item):
        return item in self.__store

    def keys(self):
        return self.__store.keys()

    def update(self, d):
        self.__store.update(d)

    def copy(self):
        new_map = Map()
        new_map.__store = self.__store.copy()
        return new_map

    def get(self, item, default=None):
        return self.__store.get(item, default)


class Set(set, StateContainer):
    pass


class Tuple(tuple, StateContainer):
    pass
