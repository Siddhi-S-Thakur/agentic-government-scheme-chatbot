import uuid
from typing import Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny
)
from app.rag.vector_store.base import BaseVectorStore
from app.schemas.scheme_schema import SchemeChunk
from app.schemas.retrieval_schema import RetrievedEvidence
from app.core.config import settings

class QdrantVectorStore(BaseVectorStore):
    """
    Production vector database connector utilizing Qdrant.
    Supports live remote instances, local embedded instances, or in-memory testing.
    """
    def __init__(
        self,
        client: Optional[QdrantClient] = None,
        collection_name: Optional[str] = None,
        dimension: int = 384
    ):
        self.collection_name = collection_name or settings.qdrant_collection
        self.dimension = dimension

        if client:
            self.client = client
        else:
            # Check if live host is configured
            if settings.qdrant_api_key:
                self.client = QdrantClient(
                    host=settings.qdrant_host,
                    port=settings.qdrant_port,
                    api_key=settings.qdrant_api_key
                )
            else:
                self.client = QdrantClient(
                    host=settings.qdrant_host,
                    port=settings.qdrant_port
                )

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create Qdrant collection if it does not already exist."""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE)
                )
        except Exception:
            # If server connection fails at startup, collection creation can be deferred
            pass

    def add_chunks(self, chunks: list[SchemeChunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) count mismatch")

        self._ensure_collection()

        points = []
        for chunk, emb in zip(chunks, embeddings):
            # Generate deterministic UUID from chunk_id
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
            payload = {
                "chunk_id": chunk.chunk_id,
                "scheme_id": chunk.scheme_id,
                "scheme_name": chunk.scheme_name,
                "section": chunk.section,
                "content": chunk.content,
                "state": chunk.metadata.get("state"),
                "level": chunk.metadata.get("level", "central"),
                "beneficiary_categories": chunk.metadata.get("beneficiary_categories", []),
                "scheme_category": chunk.metadata.get("scheme_category"),
                "official_url": chunk.metadata.get("official_url"),
                "metadata": chunk.metadata
            }
            points.append(PointStruct(id=point_id, vector=emb, payload=payload))

        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)

    def _build_filter(self, filters: Optional[dict[str, Any]]) -> Optional[Filter]:
        if not filters:
            return None

        must_conditions = []
        for key, val in filters.items():
            if val is None:
                continue
            if key == "state":
                # Match schemes that are central OR state == val
                must_conditions.append(
                    Filter(
                        should=[
                            FieldCondition(key="level", match=MatchValue(value="central")),
                            FieldCondition(key="state", match=MatchValue(value=str(val)))
                        ]
                    )
                )
            elif key == "beneficiary_categories":
                if isinstance(val, list):
                    must_conditions.append(
                        FieldCondition(key="beneficiary_categories", match=MatchAny(any=val))
                    )
                elif isinstance(val, str):
                    must_conditions.append(
                        FieldCondition(key="beneficiary_categories", match=MatchValue(value=val))
                    )
            elif key in ("scheme_category", "level"):
                must_conditions.append(FieldCondition(key=key, match=MatchValue(value=str(val))))

        if must_conditions:
            return Filter(must=must_conditions)
        return None

    def search(
        self,
        query_vector: list[float],
        filters: Optional[dict[str, Any]] = None,
        top_k: int = 10
    ) -> list[RetrievedEvidence]:
        qdrant_filter = self._build_filter(filters)

        try:
            if hasattr(self.client, "query_points"):
                res = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    query_filter=qdrant_filter,
                    limit=top_k
                )
                hits = res.points
            else:
                hits = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    query_filter=qdrant_filter,
                    limit=top_k
                )
        except Exception:
            return []

        evidence_list: list[RetrievedEvidence] = []
        for hit in hits:
            payload = hit.payload or {}
            evidence_list.append(
                RetrievedEvidence(
                    scheme_id=payload.get("scheme_id", ""),
                    scheme_name=payload.get("scheme_name", ""),
                    chunk_id=payload.get("chunk_id", str(hit.id)),
                    content=payload.get("content", ""),
                    section=payload.get("section"),
                    retrieval_source="vector",
                    vector_score=round(float(hit.score), 4),
                    metadata=payload.get("metadata", {}),
                    official_url=payload.get("official_url")
                )
            )
        return evidence_list
