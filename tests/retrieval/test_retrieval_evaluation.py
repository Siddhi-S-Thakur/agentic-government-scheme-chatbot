import json
from pathlib import Path
import pytest
from app.schemas.scheme_schema import SchemeRecord
from app.rag.embeddings.base import DeterministicMultilingualEmbeddingService
from app.rag.vector_store.base import InMemoryVectorStore
from app.rag.bm25.base import BM25Index
from app.rag.reranker.base import DeterministicCrossEncoderReranker
from app.rag.retriever.hybrid_retriever import HybridRetriever
from app.rag.ingestion.indexer import SchemeKnowledgeIndexer
from app.evaluation.evaluate_retrieval import EvaluationQuery, evaluate_retriever

def test_full_retrieval_evaluation():
    base_dir = Path(__file__).resolve().parent.parent.parent

    # 1. Load schemes
    schemes_file = base_dir / "data" / "processed" / "sample_schemes.json"
    with open(schemes_file, "r", encoding="utf-8") as f:
        schemes = [SchemeRecord(**item) for item in json.load(f)]

    # 2. Setup retriever
    embedding_service = DeterministicMultilingualEmbeddingService()
    vector_store = InMemoryVectorStore()
    bm25_index = BM25Index()
    reranker = DeterministicCrossEncoderReranker()

    indexer = SchemeKnowledgeIndexer(embedding_service, vector_store, bm25_index)
    indexer.index_schemes(schemes)

    retriever = HybridRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        bm25_index=bm25_index,
        reranker=reranker
    )

    # 3. Load evaluation queries
    eval_file = base_dir / "data" / "evaluation" / "sample_evaluation.json"
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
        eval_queries = [EvaluationQuery(**item) for item in eval_data]

    # 4. Run evaluation
    report = evaluate_retriever(retriever, eval_queries)
    report.print_summary()

    # 5. Assert evaluation quality targets
    assert report.total_queries == len(eval_queries)
    assert report.mrr >= 0.70, f"Expected MRR >= 0.70, got {report.mrr}"
    assert report.mean_recall_at_5 >= 0.70, f"Expected Recall@5 >= 0.70, got {report.mean_recall_at_5}"
