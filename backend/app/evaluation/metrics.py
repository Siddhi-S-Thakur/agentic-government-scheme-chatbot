from typing import Sequence

def precision_at_k(retrieved: Sequence[str], relevant: Sequence[str], k: int) -> float:
    """
    Calculate Precision@K:
    Proportion of top-K retrieved items that are relevant.
    """
    if k <= 0:
        return 0.0
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    relevant_set = set(relevant)
    hits = sum(1 for item in top_k if item in relevant_set)
    return hits / float(k)


def recall_at_k(retrieved: Sequence[str], relevant: Sequence[str], k: int) -> float:
    """
    Calculate Recall@K:
    Proportion of all relevant items that are retrieved in the top-K.
    """
    if not relevant:
        return 1.0  # Vacuously true if no items expected
    top_k = retrieved[:k]
    relevant_set = set(relevant)
    hits = sum(1 for item in top_k if item in relevant_set)
    return hits / float(len(relevant_set))


def reciprocal_rank(retrieved: Sequence[str], relevant: Sequence[str]) -> float:
    """
    Calculate Reciprocal Rank (RR):
    1 / rank of the first relevant item in the retrieved list (1-indexed).
    Returns 0.0 if no relevant items are found.
    """
    relevant_set = set(relevant)
    for rank_idx, item in enumerate(retrieved):
        if item in relevant_set:
            return 1.0 / float(rank_idx + 1)
    return 0.0
