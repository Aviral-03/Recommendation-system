from __future__ import annotations
import csv
from typing import Any, Union

from Graph_ADT import Graph


class _WeightedVertex:
    """A vertex in a weighted book review graph, used to represent a user or a book.
    """
    item: Any
    kind: str
    neighbours: dict[_WeightedVertex, Union[int, float]]

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.
        """
        self.item = item
        self.kind = kind
        self.neighbours = {}

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)


    def similarity_score_unweighted(self, other: _WeightedVertex) -> float:
        """Return the unweighted similarity score between this vertex and other.
        """
        if self.degree() == 0 or other.degree() == 0:
            return 0
        else:
            and_set = set.intersection(set(self.neighbours.keys()), set(other.neighbours.keys()))
            or_set = set.union(set(self.neighbours.keys()), set(other.neighbours.keys()))
            return len(and_set) / len(or_set)

    def similarity_score_strict(self, other: _WeightedVertex) -> float:
        """Return the strict weighted similarity score between this vertex and other.
        """
        if self.degree() == 0 or other.degree() == 0:
            return 0.0
        else:
            and_set = {x for x in self.neighbours
                       if x in other.neighbours and self.neighbours[x] == other.neighbours[x]}
            or_set = set.union(set(self.neighbours.keys()), set(other.neighbours.keys()))
            return len(and_set) / len(or_set)


class WeightedGraph(Graph):
    """A weighted graph used to represent a book review network that keeps track of review scores.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _WeightedVertex object.
    _vertices: dict[Any, _WeightedVertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

        # This call isn't necessary, except to satisfy PythonTA.
        Graph.__init__(self)

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph.
        """
        if item not in self._vertices:
            self._vertices[item] = _WeightedVertex(item, kind)

    def add_edge(self, item1: Any, item2: Any, weight: Union[int, float] = 1) -> None:
        """Add an edge between the two vertices with the given items in this graph,
        with the given weight.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            # Add the new edge
            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight
        else:
            # We didn't find an existing vertex for both items.
            raise ValueError

    def get_weight(self, item1: Any, item2: Any) -> Union[int, float]:
        """Return the weight of the edge between the given items.
        """
        v1 = self._vertices[item1]
        v2 = self._vertices[item2]
        return v1.neighbours.get(v2, 0)

    def average_weight(self, item: Any) -> float:
        """Return the average weight of the edges adjacent to the vertex corresponding to item.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return sum(v.neighbours.values()) / len(v.neighbours)
        else:
            raise ValueError

    def get_similarity_score(self, item1: Any, item2: Any,
                             score_type: str = 'unweighted') -> float:
        """Return the similarity score between the two given items in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            if score_type == 'unweighted':
                return v1.similarity_score_unweighted(v2)
            else:
                return v1.similarity_score_strict(v2)
        else:
            raise ValueError

    def recommend_books(self, book: str, limit: int,
                        score_type: str = 'unweighted') -> list[str]:
        """Return a list of up to <limit> recommended books based on similarity to the given book.
        """
        scores_so_far = []
        list_so_far = []
        for vertex in self.get_all_vertices('book'):
            if vertex != book:
                scores_so_far.append(self.get_similarity_score(book, vertex, score_type))

        list.sort(scores_so_far, reverse=True)

        for score in scores_so_far:
            for vertex in self.get_all_vertices('book'):
                if vertex != book:
                    if self.get_similarity_score(book, vertex, score_type) == score:
                        list_so_far.append(vertex)

        if len(list_so_far) < limit:
            return list_so_far
        else:
            return list_so_far[:limit]


def load_weighted_review_graph(reviews_file: str, book_names_file: str) -> WeightedGraph:
    """Return a book review WEIGHTED graph corresponding to the given datasets.
    """
    g = WeightedGraph()
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
            g.add_edge(row[0], book_names[row[1]], int(row[2]))

    return g