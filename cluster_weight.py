
import random

from recommendation import WeightedGraph


def create_book_graph(review_graph: WeightedGraph,
                      threshold: float = 0.05,
                      score_type: str = 'unweighted') -> WeightedGraph:
    """Return a book graph based on the given review_graph.
    """
    g = WeightedGraph()
    for vertex in review_graph.get_all_vertices('book'):
        g.add_vertex(vertex, 'book')
    for b1 in g.get_all_vertices('book'):
        for b2 in g.get_all_vertices('book'):
            if b2 != b1:
                score = review_graph.get_similarity_score(b1, b2, score_type)
                if score > threshold:
                    g.add_edge(b1, b2, score)
    return g


def cross_cluster_weight(book_graph: WeightedGraph, cluster1: set, cluster2: set) -> float:
    """Return the cross-cluster weight between cluster1 and cluster2.
    """
    weights = 0
    for u in cluster1:
        for v in cluster2:
            weights += book_graph.get_weight(u, v)
    denominator = len(cluster1) * len(cluster2)
    return weights / denominator


def find_clusters_random(graph: WeightedGraph, num_clusters: int) -> list[set]:
    """Return a list of <num_clusters> vertex clusters for the given graph.
    """
    # Each book starts in its own cluster
    clusters = [{book} for book in graph.get_all_vertices()]

    for _ in range(0, len(clusters) - num_clusters):
        print(f'{len(clusters)} clusters')

        c1 = random.choice(clusters)
        # Pick the best cluster to merge c1 into.
        best = -1
        best_c2 = None

        for c2 in clusters:
            if c1 is not c2:
                score = cross_cluster_weight(graph, c1, c2)
                if score > best:
                    best = score
                    best_c2 = c2

        best_c2.update(c1)
        clusters.remove(c1)

    return clusters


def find_clusters_greedy(graph: WeightedGraph, num_clusters: int) -> list[set]:
    """Return a list of <num_clusters> vertex clusters for the given graph.
    """
    # Each book starts in its own cluster
    clusters = [{book} for book in graph.get_all_vertices()]

    for _ in range(0, len(clusters) - num_clusters):
        print(f'{len(clusters)} clusters')

        # Merge the two communities with the most links
        best = -1
        best_c1, best_c2 = None, None

        for i1 in range(0, len(clusters)):
            for i2 in range(i1 + 1, len(clusters)):
                c1, c2 = clusters[i1], clusters[i2]
                score = cross_cluster_weight(graph, c1, c2)
                if score > best:
                    best, best_c1, best_c2 = score, c1, c2

        best_c2.update(best_c1)
        clusters.remove(best_c1)

    return clusters