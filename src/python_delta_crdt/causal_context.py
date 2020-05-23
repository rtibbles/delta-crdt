from .base import Map
from .base import Set


class CausalContext(object):
    def __init__(self, cc=None, dc=None):
        # compact causal context
        self.cc = Map(cc) if cc else Map()
        # dot cloud
        self.dc = Set(dc) if dc else Set()

    def __contains__(self, dot):
        return self.dot_in(dot)

    def __repr__(self):
        return repr({"cc": self.cc, "dc": self.dc})

    def __str__(self):
        return str({"cc": self.cc, "dc": self.dc})

    def dot_in(self, dot):
        if not isinstance(dot, tuple):
            raise TypeError("Dot must be a tuple")
        key, value = dot
        count = self.cc.get(key)
        return value <= count or dot in self.dc

    def compact(self):
        # compact DC to CC if possible
        for dot in self.dc:
            key, value = dot
            existing = self.cc.get(key)
            if existing is None or existing < value:
                self.cc[key] = value
        self.dc = Set()
        return self

    def next(self, key):
        value = self.cc.get(key, 0) + 1
        return (key, value)

    def make_dot(self, key):
        dot = self.next(key)
        self.cc[dot[0]] = dot[1]
        return dot

    def insert_dot(self, key, value=None, compact_now=False):
        self.dc.add((key, value))
        if compact_now:
            self.compact()

    def join(self, other):
        other.compact()
        self.compact()
        result = Map()

        for key in set(self.cc.keys()).union(set(other.cc.keys())):
            result[key] = max(self.cc.get(key, 0), other.cc.get(key, 0))

        return CausalContext(result)
