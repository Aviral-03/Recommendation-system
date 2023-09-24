
from __future__ import annotations
import csv
from typing import Any
import networkx as nx  # Used for visualizing graphs (by convention, referred to as "nx")


class _Vertex:
    """A vertex in a book review graph, used to represent a user or a book.

    Each vertex item is either a user id or book title. Both are represented as strings,
    even though we've kept the type annotation as Any to be consistent with lecture.
    """
    item: Any
    kind: str
    neighbours: set[_Vertex]

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.
        """
        self.item = item
        self.kind = kind
        self.neighbours = set()

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)

    ############################################################################
    # Part 1, Q3
    ############################################################################
    def similarity_score(self, other: _Vertex) -> float:
        """Return the similarity score between this vertex and other.

        See Assignment handout for definition of similarity score.
        """
        if self.degree() == 0 or other.degree() == 0:
            return 0
        else:
            and_set = set.intersection(self.neighbours, other.neighbours)
            or_set = set.union(self.neighbours, other.neighbours)
            return len(and_set) / len(or_set)


class Graph:
    """A graph used to represent a book review network.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.

        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, kind)

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self, kind: str = '') -> set:
        """Return a set of all vertex items in this graph.
        """
        if kind != '':
            return {v.item for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.keys())

    def to_networkx(self, max_vertices: int = 5000) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)

        """
        graph_nx = nx.Graph()
        for v in self._vertices.values():
            graph_nx.add_node(v.item, kind=v.kind)

            for u in v.neighbours:
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(u.item, kind=u.kind)

                if u.item in graph_nx.nodes:
                    graph_nx.add_edge(v.item, u.item)

            if graph_nx.number_of_nodes() >= max_vertices:
                break

        return graph_nx

    def get_similarity_score(self, item1: Any, item2: Any) -> float:
        """Return the similarity score between the two given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        >>> g = Graph()
        >>> for i in range(0, 6):
        ...     g.add_vertex(str(i), kind='user')
        >>> g.add_edge('0', '2')
        >>> g.add_edge('0', '3')
        >>> g.add_edge('0', '4')
        >>> g.add_edge('1', '3')
        >>> g.add_edge('1', '4')
        >>> g.add_edge('1', '5')
        >>> g.get_similarity_score('0', '1')
        0.5
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            return v1.similarity_score(v2)
        else:
            raise ValueError

    def recommend_books(self, book: str, limit: int) -> list[str]:
        """Return a list of up to <limit> recommended books based on similarity to the given book.
        """

        scores_so_far = []
        list_so_far = []
        for vertex in self.get_all_vertices('book'):
            if vertex != book:
                scores_so_far.append(self.get_similarity_score(book, vertex))

        list.sort(scores_so_far, reverse=True)

        for score in scores_so_far:
            for vertex in self.get_all_vertices('book'):
                if vertex != book:
                    if self.get_similarity_score(book, vertex) == score:
                        list_so_far.append(vertex)

        if len(list_so_far) < limit:
            return list_so_far
        else:
            return list_so_far[:limit]


def load_review_graph(reviews_file: str, book_names_file: str) -> Graph:
    """Return a book review graph corresponding to the given datasets.
    """
    g = Graph()
    book_directory = set()
    book_names = {}

    with open(reviews_file) as f:
        reader = csv.reader(f)
        for row in reader:
            g.add_vertex(row[0], 'user')
            book_directory.add(row[1])

    with open(book_names_file) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] in book_directory:
                g.add_vertex(row[1], 'book')
                book_names[row[0]] = row[1]

    with open(reviews_file) as f:
        reader = csv.reader(f)
        for row in reader:
            g.add_edge(row[0], book_names[row[1]])

    return g