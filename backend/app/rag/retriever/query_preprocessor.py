import re
import unicodedata
from typing import Optional

class QueryPreprocessor:
    """
    Normalizes user queries while strictly preserving critical domain entities:
    - Scheme names and acronyms (e.g., PM-KISAN, PMAY)
    - Indian state names (e.g., Maharashtra, Karnataka)
    - Numerical criteria (age, income figures, percentages)
    - Currency expressions (₹, Rs, Lakh, Crore)
    - Beneficiary and occupation keywords
    - Multilingual scripts (Devanagari for Hindi and Marathi)
    """

    @staticmethod
    def detect_script_language(text: str) -> str:
        """
        Lightweight script detector:
        - If Devanagari characters are present -> 'devanagari' (hi/mr)
        - Otherwise defaults to 'en'
        """
        devanagari_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        if devanagari_chars > 2:
            return "devanagari"
        return "en"

    @classmethod
    def normalize_query(cls, query: str) -> str:
        if not query:
            return ""

        # 1. Unicode NFC normalization (ensures combined Devanagari accents/matras are uniform)
        normalized = unicodedata.normalize("NFKC", query)

        # 2. Standardize Indian currency variants
        normalized = re.sub(r"(?i)\brs\.?\s*", "₹", normalized)
        normalized = re.sub(r"(?i)\brupees\s*", "₹", normalized)

        # 3. Standardize whitespace
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    @classmethod
    def enrich_query_with_profile(cls, query: str, profile_dict: Optional[dict] = None) -> str:
        """
        Optionally augment query text with key profile attributes if not already present in the text,
        improving lexical and semantic recall.
        """
        if not profile_dict:
            return query

        tokens_to_add = []
        state = profile_dict.get("state")
        if state and state.lower() not in query.lower():
            tokens_to_add.append(state)

        occupation = profile_dict.get("occupation")
        if occupation and occupation.lower() not in query.lower():
            tokens_to_add.append(occupation)

        if tokens_to_add:
            return f"{query} {' '.join(tokens_to_add)}"
        return query
