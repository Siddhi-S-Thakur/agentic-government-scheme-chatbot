from app.schemas.scheme_schema import SchemeRecord, SchemeChunk

class SchemeChunker:
    """
    Decomposes a SchemeRecord into semantically coherent, section-based SchemeChunks.
    Attaches structured metadata to each chunk to enable metadata pre-filtering during retrieval.
    """

    @classmethod
    def chunk_scheme(cls, scheme: SchemeRecord) -> list[SchemeChunk]:
        chunks: list[SchemeChunk] = []

        # Common metadata attached to every chunk of this scheme
        common_metadata = {
            "scheme_id": scheme.scheme_id,
            "scheme_name": scheme.scheme_name,
            "level": scheme.level,
            "state": scheme.state,
            "beneficiary_categories": scheme.beneficiary_categories,
            "scheme_category": scheme.scheme_category,
            "official_url": scheme.official_url,
            "source_department": scheme.source_department,
            "min_age": scheme.eligibility_criteria.min_age,
            "max_age": scheme.eligibility_criteria.max_age,
            "max_income": scheme.eligibility_criteria.max_income,
            "tags": scheme.tags,
        }

        # 1. Overview Section Chunk
        names_str = f"{scheme.scheme_name}"
        if scheme.scheme_name_hi:
            names_str += f" | {scheme.scheme_name_hi}"
        if scheme.scheme_name_mr:
            names_str += f" | {scheme.scheme_name_mr}"

        overview_content = (
            f"Scheme: {names_str}\n"
            f"Department: {scheme.department}\n"
            f"Classification: {scheme.level.upper()}"
            + (f" ({scheme.state})" if scheme.state else "")
            + f"\nCategory: {scheme.scheme_category}\n"
            f"Target Beneficiaries: {', '.join(scheme.beneficiary_categories)}\n"
            f"Overview: {scheme.description}"
        )
        chunks.append(
            SchemeChunk(
                chunk_id=f"{scheme.scheme_id}-overview",
                scheme_id=scheme.scheme_id,
                scheme_name=scheme.scheme_name,
                section="overview",
                content=overview_content,
                metadata={**common_metadata, "section": "overview"}
            )
        )

        # 2. Benefits Section Chunk
        benefits_content = (
            f"Scheme: {scheme.scheme_name}\n"
            f"Benefits & Financial Assistance:\n{scheme.benefits}"
        )
        chunks.append(
            SchemeChunk(
                chunk_id=f"{scheme.scheme_id}-benefits",
                scheme_id=scheme.scheme_id,
                scheme_name=scheme.scheme_name,
                section="benefits",
                content=benefits_content,
                metadata={**common_metadata, "section": "benefits"}
            )
        )

        # 3. Eligibility Section Chunk
        crit = scheme.eligibility_criteria
        elig_parts = [f"Scheme: {scheme.scheme_name}", "Eligibility Criteria:"]
        if crit.min_age is not None or crit.max_age is not None:
            elig_parts.append(f"- Age: {crit.min_age or 0} to {crit.max_age or 'no limit'} years")
        if crit.max_income is not None:
            elig_parts.append(f"- Maximum Income Limit: ₹{crit.max_income:,.0f} per annum")
        if crit.occupations:
            elig_parts.append(f"- Occupations: {', '.join(crit.occupations)}")
        if crit.education_qualifications:
            elig_parts.append(f"- Education: {', '.join(crit.education_qualifications)}")
        if crit.caste_categories:
            elig_parts.append(f"- Categories: {', '.join(crit.caste_categories)}")
        if crit.residence_state:
            elig_parts.append(f"- Resident of: {crit.residence_state}")
        for cond in crit.additional_conditions:
            elig_parts.append(f"- {cond}")

        eligibility_content = "\n".join(elig_parts)
        chunks.append(
            SchemeChunk(
                chunk_id=f"{scheme.scheme_id}-eligibility",
                scheme_id=scheme.scheme_id,
                scheme_name=scheme.scheme_name,
                section="eligibility",
                content=eligibility_content,
                metadata={**common_metadata, "section": "eligibility"}
            )
        )

        # 4. Application & Documents Section Chunk
        docs_str = ", ".join(scheme.documents_required) if scheme.documents_required else "None specified"
        app_content = (
            f"Scheme: {scheme.scheme_name}\n"
            f"Required Documents: {docs_str}\n"
            f"Application Procedure:\n{scheme.application_procedure}\n"
            f"Official Portal: {scheme.official_url}"
        )
        chunks.append(
            SchemeChunk(
                chunk_id=f"{scheme.scheme_id}-application",
                scheme_id=scheme.scheme_id,
                scheme_name=scheme.scheme_name,
                section="application",
                content=app_content,
                metadata={**common_metadata, "section": "application"}
            )
        )

        return chunks
