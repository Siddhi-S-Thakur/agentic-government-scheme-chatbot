from app.schemas.scheme_schema import SchemeRecord, SchemeChunk
from app.rag.chunking.scheme_chunker import SchemeChunker
from app.rag.embeddings.base import BaseEmbeddingService
from app.rag.vector_store.base import BaseVectorStore
from app.rag.bm25.base import BM25Index

class SchemeKnowledgeIndexer:
    """
    Coordinates chunking of SchemeRecords, embedding generation,
    vector store indexing, and BM25 index building.
    """
    def __init__(
        self,
        embedding_service: BaseEmbeddingService,
        vector_store: BaseVectorStore,
        bm25_index: BM25Index
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.bm25_index = bm25_index

    def index_schemes(self, schemes: list[SchemeRecord]) -> list[SchemeChunk]:
        """
        Chunks all scheme records and populates both vector store and BM25 index.
        """
        all_chunks: list[SchemeChunk] = []
        for scheme in schemes:
            chunks = SchemeChunker.chunk_scheme(scheme)
            all_chunks.extend(chunks)

        if not all_chunks:
            return []

        # 1. Generate dense embeddings for all chunk texts
        texts = [c.content for c in all_chunks]
        embeddings = self.embedding_service.embed_batch(texts)

        # 2. Add chunks and embeddings to vector store
        self.vector_store.add_chunks(all_chunks, embeddings)

        # 3. Build BM25 index
        self.bm25_index.build_index(all_chunks)

        return all_chunks
