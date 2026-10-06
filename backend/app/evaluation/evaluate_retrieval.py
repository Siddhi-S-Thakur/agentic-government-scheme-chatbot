import json
import os
from typing import Optional, Any
from pydantic import BaseModel, Field
from app.schemas.profile_schema import UserProfile
from app.rag.retriever.hybrid_retriever import HybridRetriever
from app.evaluation.metrics import precision_at_k, recall_at_k, reciprocal_rank

class EvaluationQuery(BaseModel):
    query: str
    expected_scheme_ids: list[str]
    expected_chunks: Optional[list[str]] = None
    language: str = Field(default="en", description="Language: 'en', 'hi', 'mr'")
    profile: Optional[dict[str, Any]] = None
    metadata_filters: Optional[dict[str, Any]] = None

class QueryEvaluationResult(BaseModel):
    query: str
    language: str
    expected_scheme_ids: list[str]
    retrieved_scheme_ids: list[str]
    precision_at_1: float
    precision_at_3: float
    precision_at_5: float
    recall_at_5: float
    reciprocal_rank: float
    hit: bool

class RetrievalEvaluationReport(BaseModel):
    total_queries: int
    mean_precision_at_1: float
    mean_precision_at_3: float
    mean_precision_at_5: float
    mean_recall_at_5: float
    mrr: float
    query_results: list[QueryEvaluationResult]

    def print_summary(self) -> None:
        import sys
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

        print("\n" + "=" * 60)
        print(" RETRIEVAL EVALUATION REPORT")
        print("=" * 60)
        print(f"Total Queries Evaluated: {self.total_queries}")
        print(f"Mean Precision@1:        {self.mean_precision_at_1:.4f}")
        print(f"Mean Precision@3:        {self.mean_precision_at_3:.4f}")
        print(f"Mean Precision@5:        {self.mean_precision_at_5:.4f}")
        print(f"Mean Recall@5:           {self.mean_recall_at_5:.4f}")
        print(f"Mean Reciprocal Rank:    {self.mrr:.4f}")
        print("-" * 60)
        print("Per-Query Performance:")
        for res in self.query_results:
            status = "HIT " if res.hit else "MISS"
            line = f"[{status}] [{res.language.upper()}] P@5: {res.precision_at_5:.2f} | MRR: {res.reciprocal_rank:.2f} | Query: {res.query}"
            try:
                print(line)
            except UnicodeEncodeError:
                safe_line = line.encode(sys.stdout.encoding or "ascii", errors="replace").decode(sys.stdout.encoding or "ascii")
                print(safe_line)
        print("=" * 60 + "\n")


def evaluate_retriever(
    retriever: HybridRetriever,
    dataset: list[EvaluationQuery]
) -> RetrievalEvaluationReport:
    """
    Evaluates the retriever over a dataset of test queries across English, Hindi, and Marathi.
    """
    results: list[QueryEvaluationResult] = []

    for item in dataset:
        profile_obj = UserProfile(**item.profile) if item.profile else None
        response = retriever.retrieve(
            query=item.query,
            profile=profile_obj,
            filters=item.metadata_filters,
            top_k=5,
            debug=False
        )

        retrieved_scheme_ids = [cand.scheme_id for cand in response.results]
        # Deduplicate while preserving order
        unique_retrieved: list[str] = []
        for sid in retrieved_scheme_ids:
            if sid not in unique_retrieved:
                unique_retrieved.append(sid)

        p1 = precision_at_k(unique_retrieved, item.expected_scheme_ids, 1)
        p3 = precision_at_k(unique_retrieved, item.expected_scheme_ids, 3)
        p5 = precision_at_k(unique_retrieved, item.expected_scheme_ids, 5)
        r5 = recall_at_k(unique_retrieved, item.expected_scheme_ids, 5)
        rr = reciprocal_rank(unique_retrieved, item.expected_scheme_ids)

        results.append(
            QueryEvaluationResult(
                query=item.query,
                language=item.language,
                expected_scheme_ids=item.expected_scheme_ids,
                retrieved_scheme_ids=unique_retrieved,
                precision_at_1=round(p1, 4),
                precision_at_3=round(p3, 4),
                precision_at_5=round(p5, 4),
                recall_at_5=round(r5, 4),
                reciprocal_rank=round(rr, 4),
                hit=(rr > 0.0)
            )
        )

    n = max(len(results), 1)
    mean_p1 = sum(r.precision_at_1 for r in results) / n
    mean_p3 = sum(r.precision_at_3 for r in results) / n
    mean_p5 = sum(r.precision_at_5 for r in results) / n
    mean_r5 = sum(r.recall_at_5 for r in results) / n
    mrr = sum(r.reciprocal_rank for r in results) / n

    return RetrievalEvaluationReport(
        total_queries=len(results),
        mean_precision_at_1=round(mean_p1, 4),
        mean_precision_at_3=round(mean_p3, 4),
        mean_precision_at_5=round(mean_p5, 4),
        mean_recall_at_5=round(mean_r5, 4),
        mrr=round(mrr, 4),
        query_results=results
    )

if __name__ == "__main__":
    from pathlib import Path
    from app.schemas.scheme_schema import SchemeRecord
    from app.rag.embeddings.base import DeterministicMultilingualEmbeddingService
    from app.rag.vector_store.base import InMemoryVectorStore
    from app.rag.bm25.base import BM25Index
    from app.rag.reranker.base import DeterministicCrossEncoderReranker
    from app.rag.ingestion.indexer import SchemeKnowledgeIndexer

    # Locate project root
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    schemes_file = base_dir / "data" / "processed" / "sample_schemes.json"
    eval_file = base_dir / "data" / "evaluation" / "sample_evaluation.json"

    print("Setting up Hybrid RAG Pipeline for Retrieval Evaluation...")
    with open(schemes_file, "r", encoding="utf-8") as f:
        schemes = [SchemeRecord(**item) for item in json.load(f)]

    embedding_service = DeterministicMultilingualEmbeddingService()
    vector_store = InMemoryVectorStore()
    bm25_index = BM25Index()
    reranker = DeterministicCrossEncoderReranker()

    indexer = SchemeKnowledgeIndexer(embedding_service, vector_store, bm25_index)
    chunks = indexer.index_schemes(schemes)
    print(f"Indexed {len(schemes)} schemes into {len(chunks)} chunks.")

    retriever = HybridRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        bm25_index=bm25_index,
        reranker=reranker
    )

    with open(eval_file, "r", encoding="utf-8") as f:
        eval_queries = [EvaluationQuery(**item) for item in json.load(f)]

    print(f"Running evaluation on {len(eval_queries)} queries...")
    report = evaluate_retriever(retriever, eval_queries)
    report.print_summary()

