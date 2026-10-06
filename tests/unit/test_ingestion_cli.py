from pathlib import Path
import pytest
from qdrant_client import QdrantClient
from app.rag.ingestion.cli import run_ingestion

def test_run_ingestion_pipeline():
    base_dir = Path(__file__).resolve().parent.parent.parent
    sample_file = base_dir / "data" / "processed" / "sample_schemes.json"

    memory_client = QdrantClient(":memory:")

    summary = run_ingestion(
        data_file=str(sample_file),
        save_to_db=True,
        index_to_qdrant=True,
        qdrant_client=memory_client
    )

    assert summary["schemes_count"] == 4
    assert summary["chunks_count"] == 16
    assert summary["embeddings_count"] == 16
