import re
from typing import Optional, Any
from rank_bm25 import BM25Okapi
from app.schemas.scheme_schema import SchemeChunk
from app.schemas.retrieval_schema import RetrievedEvidence

class BM25Index:
    """
    Lexical retrieval index utilizing BM25Okapi.
    Specialized for matching exact government terminology, scheme names,
    eligibility keywords, document names, and numbers across English, Hindi, and Marathi.
    """
    def __init__(self):
        self.chunks: list[SchemeChunk] = []
        self.tokenized_corpus: list[list[str]] = []
        self.bm25: Optional[BM25Okapi] = None

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """
        Multilingual tokenizer that supports Devanagari, English alphanumeric strings,
        currency figures, and hyphenated terms.
        """
        if not text:
            return []
        # Lowercase Latin text while preserving Devanagari characters
        lowered = text.lower()
        # Match words including Unicode alphanumeric characters (e.g. Devanagari range \u0900-\u097F)
        tokens = re.findall(r"[\w\u0900-\u097F]+(?:-[\w\u0900-\u097F]+)*", lowered, flags=re.UNICODE)
        return tokens

    def build_index(self, chunks: list[SchemeChunk]) -> None:
        """Index a collection of scheme chunks."""
        self.chunks = list(chunks)
        self.tokenized_corpus = [self.tokenize(c.content + " " + c.scheme_name) for c in self.chunks]
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)
        else:
            self.bm25 = None

    def _matches_filters(self, chunk: SchemeChunk, filters: Optional[dict[str, Any]]) -> bool:
        if not filters:
            return True
        for key, val in filters.items():
            if val is None:
                continue
            meta = chunk.metadata
            if key == "state":
                chunk_state = meta.get("state")
                level = meta.get("level", "central")
                if level == "central":
                    continue
                if chunk_state and chunk_state.lower() != str(val).lower():
                    return False
            elif key == "beneficiary_categories":
                categories = [c.lower() for c in meta.get("beneficiary_categories", [])]
                if isinstance(val, list):
                    if not any(v.lower() in categories for v in val):
                        return False
                elif isinstance(val, str):
                    if val.lower() not in categories and categories:
                        return False
            elif key in meta and meta[key] != val:
                return False
        return True

    def search(
        self,
        query: str,
        filters: Optional[dict[str, Any]] = None,
        top_k: int = 10
    ) -> list[RetrievedEvidence]:
        """
        Perform BM25 search over indexed chunks with optional metadata filtering.
        """
        if not self.bm25 or not self.chunks:
            return []

        tokens = self.tokenize(query)
        if not tokens:
            return []

        raw_scores = self.bm25.get_scores(tokens)

        scored_candidates: list[tuple[float, SchemeChunk]] = []
        for idx, score in enumerate(raw_scores):
            chunk = self.chunks[idx]
            if score <= 0.0:
                continue
            if not self._matches_filters(chunk, filters):
                continue
            scored_candidates.append((float(score), chunk))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        top_candidates = scored_candidates[:top_k]

        evidence_list: list[RetrievedEvidence] = []
        for score, chunk in top_candidates:
            evidence_list.append(
                RetrievedEvidence(
                    scheme_id=chunk.scheme_id,
                    scheme_name=chunk.scheme_name,
                    chunk_id=chunk.chunk_id,
                    content=chunk.content,
                    section=chunk.section,
                    retrieval_source="bm25",
                    bm25_score=round(score, 4),
                    metadata=chunk.metadata,
                    official_url=chunk.metadata.get("official_url")
                )
            )
        return evidence_list
