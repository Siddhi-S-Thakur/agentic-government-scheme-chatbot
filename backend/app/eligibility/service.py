from typing import Optional
from app.schemas.profile_schema import UserProfile
from app.schemas.scheme_schema import SchemeRecord
from app.schemas.retrieval_schema import RetrievedEvidence
from app.eligibility.models import EligibilityEvaluation, EligibilityStatus
from app.eligibility.engine import EligibilityEngine

class SchemeRecommendation(EligibilityEvaluation):
    """
    Combines deterministic eligibility evaluation with retrieved evidence excerpts.
    """
    retrieved_sections: list[str] = []
    top_evidence_snippet: Optional[str] = None
    retrieval_score: Optional[float] = None

class EligibilityService:
    """
    Service coordinating between retrieved RAG evidence and deterministic rule checking.
    """

    @classmethod
    def evaluate_retrieved_schemes(
        cls,
        profile: UserProfile,
        evidence: list[RetrievedEvidence],
        schemes_catalog: dict[str, SchemeRecord]
    ) -> list[SchemeRecommendation]:
        """
        Takes retrieved evidence from Hybrid RAG, resolves parent schemes,
        evaluates eligibility, and pairs each with its evidence snippets.
        """
        # Group evidence by scheme_id while preserving rank order
        scheme_evidence_map: dict[str, list[RetrievedEvidence]] = {}
        for ev in evidence:
            if ev.scheme_id not in scheme_evidence_map:
                scheme_evidence_map[ev.scheme_id] = []
            scheme_evidence_map[ev.scheme_id].append(ev)

        recommendations: list[SchemeRecommendation] = []

        for sid, ev_list in scheme_evidence_map.items():
            scheme = schemes_catalog.get(sid)
            if not scheme:
                continue

            # Deterministic rule evaluation
            eval_result = EligibilityEngine.evaluate(profile, scheme)

            top_snippet = ev_list[0].content if ev_list else None
            top_score = ev_list[0].reranker_score or ev_list[0].fusion_score
            sections = list({e.section for e in ev_list if e.section})

            rec = SchemeRecommendation(
                scheme_id=eval_result.scheme_id,
                scheme_name=eval_result.scheme_name,
                status=eval_result.status,
                matched_conditions=eval_result.matched_conditions,
                failed_conditions=eval_result.failed_conditions,
                missing_fields=eval_result.missing_fields,
                summary=eval_result.summary,
                official_url=eval_result.official_url,
                retrieved_sections=sections,
                top_evidence_snippet=top_snippet,
                retrieval_score=top_score
            )
            recommendations.append(rec)

        # Sort recommendations: ELIGIBLE first, then INFORMATION_MISSING, then NOT_ELIGIBLE
        priority_order = {
            EligibilityStatus.ELIGIBLE: 0,
            EligibilityStatus.INFORMATION_MISSING: 1,
            EligibilityStatus.NOT_ELIGIBLE: 2
        }
        recommendations.sort(key=lambda r: priority_order.get(r.status, 3))

        return recommendations
