# packages/utilities/vector_matching/vector_matcher.py

# This file would contain functions to perform vector similarity matching
# using libraries like scikit-learn or faiss.

from typing import List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class VectorMatcher:
    """Performs similarity matching between vectors."""

    def __init__(self):
        print("Initializing VectorMatcher...")

    def find_most_similar(
        self, query_vector: List[float], candidate_vectors: List[List[float]]
    ) -> List[Tuple[int, float]]:
        """Finds the most similar candidate vectors to a query vector using cosine similarity.

        Returns a list of tuples (index, similarity_score) sorted by similarity.
        """
        if not candidate_vectors:
            return []

        query_np = np.array(query_vector).reshape(1, -1)
        candidates_np = np.array(candidate_vectors)

        similarities = cosine_similarity(query_np, candidates_np)[0]

        # Pair similarities with their original indices and sort
        indexed_similarities = sorted(
            enumerate(similarities), key=lambda x: x[1], reverse=True
        )

        return indexed_similarities

    def calculate_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculates the cosine similarity between two vectors."""
        vec1_np = np.array(vector1).reshape(1, -1)
        vec2_np = np.array(vector2).reshape(1, -1)
        return cosine_similarity(vec1_np, vec2_np)[0][0]
