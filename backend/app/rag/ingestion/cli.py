import argparse
import json
import os
import sys
from pathlib import Path
from app.core.database import init_db
from app.models.repositories import SchemeRepository
from app.schemas.scheme_schema import SchemeRecord, SchemeChunk
from app.rag.chunking.scheme_chunker import SchemeChunker
from app.rag.embeddings.base import DeterministicMultilingualEmbeddingService
from app.rag.vector_store.qdrant_store import QdrantVectorStore
from app.rag.bm25.base import BM25Index

def run_ingestion(
    data_file: str,
    save_to_db: bool = True,
    index_to_qdrant: bool = False,
    qdrant_client = None
) -> dict:
    """
    Ingests official government schemes from a JSON data file,
    persisting records to the database and vector indexes.
    """
    path = Path(data_file)
    if not path.exists():
        raise FileNotFoundError(f"Scheme data file not found: {data_file}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    schemes = [SchemeRecord(**item) for item in data]
    print(f"Loaded and validated {len(schemes)} scheme records from {data_file}")

    # 1. Save to relational database
    if save_to_db:
        init_db()
        SchemeRepository.save_batch(schemes)
        print(f"Successfully saved {len(schemes)} schemes to relational database.")

    # 2. Chunk schemes
    all_chunks: list[SchemeChunk] = []
    for s in schemes:
        chunks = SchemeChunker.chunk_scheme(s)
        all_chunks.extend(chunks)
    print(f"Generated {len(all_chunks)} semantic section chunks.")

    # 3. Generate embeddings
    embedder = DeterministicMultilingualEmbeddingService()
    chunk_texts = [c.content for c in all_chunks]
    embeddings = embedder.embed_batch(chunk_texts)
    print(f"Generated {len(embeddings)} dense embeddings (dim={embedder.dimension}).")

    # 4. Optional Qdrant indexing
    if index_to_qdrant:
        try:
            qdrant_store = QdrantVectorStore(client=qdrant_client, dimension=embedder.dimension)
            qdrant_store.add_chunks(all_chunks, embeddings)
            print(f"Successfully upserted {len(all_chunks)} chunks to Qdrant collection '{qdrant_store.collection_name}'.")
        except Exception as e:
            print(f"Warning: Qdrant indexing encountered an issue ({e}). Skipping live Qdrant upsert.")

    # 5. BM25 indexing
    bm25 = BM25Index()
    bm25.build_index(all_chunks)
    print(f"BM25 index built with {len(all_chunks)} chunks.")

    return {
        "schemes_count": len(schemes),
        "chunks_count": len(all_chunks),
        "embeddings_count": len(embeddings)
    }

def main():
    parser = argparse.ArgumentParser(description="Government Scheme Knowledge Base Ingestion CLI")
    parser.add_argument(
        "--data-file",
        default="data/processed/sample_schemes.json",
        help="Path to JSON file containing scheme records"
    )
    parser.add_argument("--db", action="store_true", default=True, help="Save to relational database")
    parser.add_argument("--qdrant", action="store_true", default=False, help="Index into Qdrant vector store")

    args = parser.parse_args()

    print("=" * 60)
    print(" GOVERNMENT SCHEME INGESTION PIPELINE")
    print("=" * 60)
    summary = run_ingestion(
        data_file=args.data_file,
        save_to_db=args.db,
        index_to_qdrant=args.qdrant
    )
    print("-" * 60)
    print(f"Ingestion Complete: {summary['schemes_count']} schemes, {summary['chunks_count']} chunks indexed.")
    print("=" * 60)

if __name__ == "__main__":
    main()
