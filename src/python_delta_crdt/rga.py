try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence

from .base import CRDT
from .base import Map
from .base import Set
from .base import Tuple
from .base import mutator
from .codec import decode
from .codec import encode

ADDED_VERTICES = 0
REMOVED_VERTICES = 1
EDGES = 2
UNMERGED_EDGES = 3


def create_unique_id(state, node_id, index=0):
    edges = state[EDGES]
    position = len(edges) + index
    return encode((position, node_id)).encode("base64")


def compare_ids(id1, id2):
    pos1, node_id1 = decode(id1.decode("base64"))
    pos2, node_id2 = decode(id2.decode("base64"))

    if pos1 < pos2:
        return -1
    if pos1 > pos2:
        return 1
    if node_id1 < node_id2:
        return -1
    if node_id1 > node_id2:
        return 1
    return 0


class RGA(CRDT, MutableSequence):
    def __iter__(self):
        return iter(self._value_cache)

    def __contains__(self, item):
        return item in self._value_cache

    def __len__(self):
        return len(self._value_cache)

    @classmethod
    def initial(cls):
        return Tuple((Map([(None, None)]), Set(), Map([(None, None)]), Set(),))

    @classmethod
    def join(cls, s1, s2):
        added = s1[ADDED_VERTICES].copy()
        added.update(s2[ADDED_VERTICES])
        removed = s1[REMOVED_VERTICES].union(s2[REMOVED_VERTICES])

        s1_edges = s1[EDGES]
        s2_edges = s2[EDGES]
        result_edges = s1_edges.copy()

        def insert_edge(left_edge, new_key):
            right = result_edges.get(left_edge, None)

            if not new_key or right == new_key:
                return

            while right and (compare_ids(right, new_key) > 0):
                left_edge = right
                right = result_edges.get(right, None)

            result_edges[left_edge] = new_key
            result_edges[new_key] = right

        unmerged_edges = (s1[UNMERGED_EDGES] or Set()).union(
            s2[UNMERGED_EDGES] or Set()
        )

        edges_to_add = s2_edges.copy()

        if not result_edges:
            result_edges[None] = None

        for key, new_value in edges_to_add.items():
            if new_value in result_edges:
                continue
            elif key in result_edges:
                if new_value not in added:
                    unmerged_edges.add((key, new_value))
                else:
                    insert_edge(key, new_value)
            else:
                unmerged_edges.add((key, new_value))

        if unmerged_edges:
            progress = True
            while progress:
                edges_inserted = Set()
                for edge in unmerged_edges:
                    key, new_value = edge
                    if new_value in result_edges:
                        edges_inserted.add(edge)
                    elif key in result_edges and key in added:
                        insert_edge(key, new_value)
                        edges_inserted.add(edge)

                progress = bool(edges_inserted)
                unmerged_edges = unmerged_edges.difference(edges_inserted)

        return Tuple((added, removed, result_edges, unmerged_edges,))

    @classmethod
    def _gen_value(cls, state):
        added_vertices, removed_vertices, edges, _ = state
        next_id = edges.get(None)
        while next_id:
            if next_id not in removed_vertices:
                yield added_vertices.get(next_id)
            next_id = edges.get(next_id)

    @classmethod
    def value(cls, state):
        return list(cls._gen_value(state))

    def __getitem__(self, index):
        return self._value_cache[index]

    def _remove_vertex_delta(self, vertex):
        return Tuple((Map(), Set([vertex]), Map(), Set()))

    def _remove_index_delta(self, index):
        removed = self.state[REMOVED_VERTICES]
        edges = self.state[EDGES]
        i = -1
        element_id = None
        while i < index:
            if element_id in edges:
                element_id = edges.get(element_id)
            else:
                raise ValueError("Nothing at index {}".format(index))
            if element_id not in removed:
                i += 1
        return self._remove_vertex_delta(element_id)

    def _insert_values_at_index_delta(self, index, values):
        removed = self.state[REMOVED_VERTICES]
        edges = self.state[EDGES]
        i = 0
        left = None
        while i < index and left in edges:
            if left not in removed:
                i += 1
            if left in edges:
                left = edges.get(left)
            while left in removed:
                left = edges.get(left)
        new_added = Map()
        new_removed = Set()
        if left in removed:
            new_removed.add(left)
        new_edges = Map()
        for i, value in enumerate(values):
            new_id = create_unique_id(self.state, self.id, i)
            new_added[new_id] = value
            new_edges[left] = new_id
            left = new_id

        return Tuple((new_added, new_removed, new_edges, Set()))

    @mutator
    def __delitem__(self, index):
        return self._remove_index_delta(index)

    @mutator
    def __setitem__(self, index, value):
        return self.join(
            self._insert_values_at_index_delta(index, [value]),
            self._remove_index_delta(index),
        )

    @mutator
    def add_right(self, before_vertex, value):
        elem_id = create_unique_id(self.state, self.id)
        edges = self.state[EDGES]
        r = edges.get(before_vertex)
        new_edges = Map()
        new_edges[before_vertex] = elem_id
        new_edges[elem_id] = r

        return Tuple((Map([(elem_id, value)]), Set(), new_edges, Set()))

    @mutator
    def insert(self, index, *values):
        return self._insert_values_at_index_delta(index, values)

    @mutator
    def append(self, value):
        edges = self.state[EDGES]
        last = None
        while last in edges and edges.get(last):
            last = edges.get(last)

        elem_id = create_unique_id(self.state, self.id)

        new_added = Map([(elem_id, value)])
        new_edges = Map([(last, elem_id)])

        return Tuple((new_added, Set(), new_edges, Set()))

    @mutator
    def remove(self, value):
        index = self._value_cache.index(value)
        return self._remove_index_delta(index)

    @mutator
    def remove_at(self, index):
        return self._remove_index_delta(index)

    @mutator
    def extend(self, values):
        index = len(self)
        return self._insert_values_at_index_delta(index, values)
