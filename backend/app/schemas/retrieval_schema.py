from typing import Optional, Literal, Any
from pydantic import BaseModel, Field

class RetrievedEvidence(BaseModel):
    """
    Structured evidence returned by the retrieval pipeline.
    Preserves granular scoring at each stage (vector, BM25, RRF, reranker)
    for transparency, explainability, and debugging.
    """
    scheme_id: str = Field(..., description="Unique identifier of the matching scheme")
    scheme_name: str = Field(..., description="Name of the scheme")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    content: str = Field(..., description="Retrieved textual excerpt or chunk")
    section: Optional[str] = Field(default=None, description="Section of the scheme chunk")
    retrieval_source: Literal["vector", "bm25", "hybrid"] = Field(..., description="Origin retriever")
    vector_score: Optional[float] = Field(default=None, description="Cosine similarity score from vector search")
    bm25_score: Optional[float] = Field(default=None, description="Lexical relevance score from BM25")
    fusion_score: Optional[float] = Field(default=None, description="Reciprocal Rank Fusion (RRF) score")
    reranker_score: Optional[float] = Field(default=None, description="Cross-encoder / BGE reranker relevance score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata tags associated with chunk")
    official_url: Optional[str] = Field(default=None, description="Official government source link")

class RetrievalDebugInfo(BaseModel):
    """
    Full observability data exposing the retrieval pipeline's internal decisions.
    Answers: 'Why did this scheme get retrieved?'
    """
    original_query: str = Field(..., description="Raw user query as submitted")
    normalized_query: str = Field(..., description="Preprocessed query preserving domain entities")
    detected_language: Optional[str] = Field(default=None, description="Detected language code (e.g. en, hi, mr)")
    profile_context: Optional[dict[str, Any]] = Field(default=None, description="User profile attributes used to enrich retrieval")
    metadata_filters: Optional[dict[str, Any]] = Field(default=None, description="Structured filters applied to search")
    vector_results: list[RetrievedEvidence] = Field(default_factory=list, description="Top candidates from vector search")
    bm25_results: list[RetrievedEvidence] = Field(default_factory=list, description="Top candidates from BM25 search")
    fusion_results: list[RetrievedEvidence] = Field(default_factory=list, description="Results after RRF fusion before reranking")
    reranker_results: list[RetrievedEvidence] = Field(default_factory=list, description="Results after reranking")
    final_top_k: list[RetrievedEvidence] = Field(default_factory=list, description="Final output evidence list")
    source_urls: list[str] = Field(default_factory=list, description="All unique official source URLs")

class RetrievalRequest(BaseModel):
    """
    Request model for the retrieval interface.
    """
    query: str = Field(..., description="User query in English, Hindi, or Marathi")
    profile: Optional[dict[str, Any]] = Field(default=None, description="Optional profile dictionary")
    filters: Optional[dict[str, Any]] = Field(default=None, description="Optional explicit metadata filters")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of final evidence chunks to return")
    debug: bool = Field(default=False, description="Whether to include full observability debug info")

class RetrievalResponse(BaseModel):
    """
    Response model returned by the retriever.
    """
    query: str = Field(..., description="Processed query")
    results: list[RetrievedEvidence] = Field(..., description="Top-K evidence items")
    total_candidates_found: int = Field(default=0, description="Total candidates identified before final cut")
    debug_info: Optional[RetrievalDebugInfo] = Field(default=None, description="Observability details when debug=True")
