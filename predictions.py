from __future__ import annotations
import csv
from typing import Union

import recommendation


class ReviewScorePredictor:
    graph: recommendation.WeightedGraph

    def __init__(self, graph: recommendation.WeightedGraph) -> None:
        """Initialize a new ReviewScorePredictor."""
        self.graph = graph

    def predict_review_score(self, user: str, book: str) -> int:
        """Predict the score (1-5) that the given user would give the given book.

        If there is already an edge between the given user and book in the graph,
        return that score. Otherwise, return a predicted score.
        """
        raise NotImplementedError


class FiveStarPredictor(ReviewScorePredictor):
    """A book review predictor that always predicts a five-star review,
    ignoring the actual book and user.
    """
    def predict_review_score(self, user: str, book: str) -> int:
        """Predict the score that the given user would give the given book.
        """
        if self.graph.adjacent(user, book):
            return self.graph.get_weight(user, book)
        else:
            return 5


class BookAverageScorePredictor(ReviewScorePredictor):
    """A book review predictor that always predicts based on the book's average score,
    ignoring any user preferences.
    """
    def predict_review_score(self, user: str, book: str) -> int:
        """Predict the score that the given user would give the given book.
        """
        if self.graph.adjacent(user, book):
            return self.graph.get_weight(user, book)
        else:
            return round(self.graph.average_weight(book))


class SimilarUserPredictor(ReviewScorePredictor):
    """A book review predictor that makes a prediction based on how similar users rated the book.
    """
    # Private Instance Attributes:
    #   - _score_type: the type of similarity score to use when computing similarity score
    _score_type: str

    def __init__(self, graph: recommendation.WeightedGraph,
                 score_type: str = 'unweighted') -> None:
        """Initialize a new SimilarUserPredictor.
        """
        self._score_type = score_type
        ReviewScorePredictor.__init__(self, graph)

    def predict_review_score(self, user: str, book: str) -> int:
        """Predict the score that the given user would give the given book.
        """
        if self.graph.adjacent(user, book):
            return self.graph.get_weight(user, book)
        else:
            score_predictor = []
            total_weighted_score = 0
            for other_user in self.graph.get_all_vertices('user'):
                if self.graph.get_weight(other_user, book) > 0:
                    weight_similarity_score = self.graph.get_similarity_score(user, other_user,
                                                                              'strict')
                    review_score = self.graph.get_weight(other_user, book)
                    score_predictor.append((weight_similarity_score * review_score))
                    total_weighted_score += weight_similarity_score

            if sum(score_predictor) == 0:
                return round(self.graph.average_weight(book))
            else:
                return round(sum(score_predictor) / total_weighted_score)


def evaluate_predictor(predictor: ReviewScorePredictor,
                       test_file: str, book_names_file: str) -> dict[str, Union[int, float]]:
    """Evaluate the given ReviewScorePredictor on the given test file.
    """
    with open(book_names_file) as d:
        reader = csv.reader(d)

        book_names = {}
        for row in reader:
            book_names[row[0]] = row[1]

    with open(test_file) as f:
        reader = csv.reader(f)
        total_reviews = 0
        total_correct = 0
        error_so_far = []
        for row in reader:
            predicted_score = predictor.predict_review_score(row[0], book_names[row[1]])
            if predicted_score == int(row[2]):
                total_correct += 1
            total_reviews += 1
            error_so_far.append(abs(predicted_score - int(row[2])))
        average_error = sum(error_so_far) / total_reviews

    return {
        'num_reviews': total_reviews,
        'num_correct': total_correct,
        'average_error': average_error,
    }