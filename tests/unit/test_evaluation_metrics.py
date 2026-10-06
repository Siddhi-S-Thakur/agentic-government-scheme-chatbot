import pytest
from app.evaluation.metrics import precision_at_k, recall_at_k, reciprocal_rank

def test_precision_at_k():
    retrieved = ["scheme-1", "scheme-2", "scheme-3", "scheme-4", "scheme-5"]
    relevant = ["scheme-1", "scheme-3"]

    assert precision_at_k(retrieved, relevant, 1) == 1.0  # 1/1
    assert precision_at_k(retrieved, relevant, 2) == 0.5  # 1/2
    assert precision_at_k(retrieved, relevant, 5) == 0.4  # 2/5
    assert precision_at_k([], relevant, 5) == 0.0

def test_recall_at_k():
    retrieved = ["scheme-1", "scheme-2", "scheme-3", "scheme-4", "scheme-5"]
    relevant = ["scheme-1", "scheme-3", "scheme-6"]

    # In top 2, only scheme-1 is retrieved out of 3 relevant
    assert round(recall_at_k(retrieved, relevant, 2), 4) == round(1/3, 4)
    # In top 5, scheme-1 and scheme-3 are retrieved out of 3 relevant
    assert round(recall_at_k(retrieved, relevant, 5), 4) == round(2/3, 4)

def test_reciprocal_rank():
    relevant = ["target-scheme"]

    # First position
    assert reciprocal_rank(["target-scheme", "other-1", "other-2"], relevant) == 1.0
    # Second position
    assert reciprocal_rank(["other-1", "target-scheme", "other-2"], relevant) == 0.5
    # Third position
    assert round(reciprocal_rank(["other-1", "other-2", "target-scheme"], relevant), 4) == round(1/3, 4)
    # Not found
    assert reciprocal_rank(["other-1", "other-2"], relevant) == 0.0
