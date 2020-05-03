from abc import ABCMeta
from abc import abstractmethod

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

from six import with_metaclass


class Base(with_metaclass(ABCMeta)):
    def __init__(self, identifier):
        self.id = identifier
        self.state = self.initial()
        self._value_cache = self.value(self.state)

    @abstractmethod
    def initial(self):
        pass

    def apply(self, delta):
        new_state = self.join(self.state, delta)
        if hasattr(self, "incremental_value"):
            self._value_cache = self.incremental_value(
                self.state, new_state, delta, self._value_cache
            )
        else:
            self._value_cache = self.value(new_state)
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


def mutator(func):
    def wrapper(self, *args, **kwargs):
        delta = func(self, *args, **kwargs)
        self.apply(delta)
        return delta

    return wrapper


class Map(MutableMapping):
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

    def update(self, d):
        self.__store.update(d)

    def copy(self):
        new_map = Map()
        new_map.__store = self.__store.copy()
        return new_map

    def get(self, item, default=None):
        return self.__store.get(item, default)
