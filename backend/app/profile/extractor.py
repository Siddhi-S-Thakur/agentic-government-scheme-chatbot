import re
import unicodedata
from typing import Optional, Literal
from app.schemas.profile_schema import UserProfile

class ProfileExtractor:
    """
    Progressively extracts citizen profile attributes from conversational turns
    across English, Hindi, and Marathi, mapping them to language-neutral canonical values.
    """

    # Multilingual occupation dictionary -> canonical English value
    OCCUPATION_MAP = {
        # Farmers / Agriculture
        "farmer": "farmer",
        "farmers": "farmer",
        "farming": "farmer",
        "agriculture": "farmer",
        "agriculturist": "farmer",
        "किसान": "farmer",
        "कृषक": "farmer",
        "खेती": "farmer",
        "शेतकरी": "farmer",
        "शेती": "farmer",
        # Students
        "student": "student",
        "students": "student",
        "studying": "student",
        "विद्यार्थी": "student",
        "छात्र": "student",
        "छात्रा": "student",
        "कॉलेज": "student",
        "शाळा": "student",
        # Unemployed / Destitute
        "unemployed": "unemployed",
        "jobless": "unemployed",
        "बेरोजगार": "unemployed",
        "बेरोज़गार": "unemployed",
        "destitute": "destitute",
        "निराधार": "destitute",
    }

    # Indian States dictionary -> canonical title-cased name
    STATE_MAP = {
        "maharashtra": "Maharashtra",
        "महाराष्ट्र": "Maharashtra",
        "karnataka": "Karnataka",
        "कर्नाटक": "Karnataka",
        "gujarat": "Gujarat",
        "गुजरात": "Gujarat",
        "delhi": "Delhi",
        "दिल्ली": "Delhi",
        "uttar pradesh": "Uttar Pradesh",
        "उत्तर प्रदेश": "Uttar Pradesh",
        "madhya pradesh": "Madhya Pradesh",
        "मध्य प्रदेश": "Madhya Pradesh",
        "rajasthan": "Rajasthan",
        "राजस्थान": "Rajasthan",
    }

    # Social/Caste Categories
    CATEGORY_MAP = {
        "sc": "SC",
        "scheduled caste": "SC",
        "अनुसूचित जाति": "SC",
        "अनुसूचित जाती": "SC",
        "st": "ST",
        "scheduled tribe": "ST",
        "अनुसूचित जनजाति": "ST",
        "अनुसूचित जमाती": "ST",
        "obc": "OBC",
        "other backward class": "OBC",
        "इतर मागास वर्ग": "OBC",
        "अन्य पिछड़ा वर्ग": "OBC",
        "general": "General",
        "open": "General",
        "सामान्य": "General",
        "खुला": "General",
        "ews": "EWS",
    }

    # Gender
    GENDER_MAP = {
        "female": "female",
        "woman": "female",
        "women": "female",
        "महिला": "female",
        "स्त्री": "female",
        "मुलगी": "female",
        "लड़की": "female",
        "aurat": "female",
        "male": "male",
        "man": "male",
        "men": "male",
        "पुरुष": "male",
        "मुलगा": "male",
        "लड़का": "male",
    }

    @classmethod
    def extract_from_text(cls, text: str, existing_profile: Optional[UserProfile] = None) -> UserProfile:
        """
        Incrementally updates and returns a UserProfile by extracting any recognizable
        entities from the user's latest text input.
        """
        profile = existing_profile.model_copy() if existing_profile else UserProfile()
        if not text:
            return profile

        normalized = unicodedata.normalize("NFKC", text)
        lowered = normalized.lower()

        # 1. Detect Interaction Mode preference
        if any(term in lowered for term in ["mcq mode", "use mcq", "mcq", "पर्याय", "बहुविकल्पीय"]):
            profile.interaction_mode = "mcq"
        elif any(term in lowered for term in ["text mode", "normal mode", "type"]):
            profile.interaction_mode = "text"

        # 2. Detect Language preference
        MARATHI_INDICATORS = ["आहे", "आहेत", "नाही", "मध्ये", "कसे", "काय", "शेतकरी", "वर्षे", "कोणती", "लागतात", "होते", "करावे", "मिळेल", "उत्पन्न", "मुलगी", "मुलगा", "मी"]
        HINDI_INDICATORS = ["है", "हैं", "नहीं", "में", "कैसे", "क्या", "किसान", "साल", "कौनसी", "होता", "मिलेगा", "लड़की", "लड़का", "हूँ", "हूं", "आय"]

        if any(term in lowered for term in ["in marathi", "मराठीत", "मराठी मध्ये", "मराठी"]):
            profile.preferred_language = "mr"
        elif any(term in lowered for term in ["in hindi", "हिंदी में", "हिन्दी में", "हिंदी"]):
            profile.preferred_language = "hi"
        elif any(term in lowered for term in ["in english", "english"]):
            profile.preferred_language = "en"
        elif sum(1 for c in text if '\u0900' <= c <= '\u097F') > 3:
            mr_count = sum(1 for word in MARATHI_INDICATORS if word in lowered)
            hi_count = sum(1 for word in HINDI_INDICATORS if word in lowered)
            if mr_count > hi_count:
                profile.preferred_language = "mr"
            else:
                profile.preferred_language = "hi"

        # 3. Extract Age
        # Patterns like: "25 years old", "age 30", "वय 25", "25 साल", "25 वर्ष", "वय २५"
        # Convert Devanagari numerals to ASCII if present
        devanagari_digits = str.maketrans("०१२३४५६७८९", "0123456789")
        ascii_text = lowered.translate(devanagari_digits)

        age_match = re.search(
            r"(?:age\s*(?:is|:)?\s*|वय\s*(?:आहे|:)?\s*|उम्र\s*(?:है|:)?\s*)(\d{1,2})\b|"
            r"\b(\d{1,2})\s*(?:years?\s*old|years?|साल|वर्ष|वर्षांचा|वर्षांची|वर्षांचे)\b",
            ascii_text
        )
        if age_match:
            found_age = int(age_match.group(1) or age_match.group(2))
            if 0 < found_age <= 120:
                profile.age = found_age

        # 4. Extract Income
        lakh_match = re.search(
            r"(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:lakhs?|lacs?|लाख|लक्ष)",
            ascii_text
        )
        if lakh_match:
            val = float(lakh_match.group(1))
            profile.annual_income = val * 100_000.0
        else:
            income_num_match = re.search(
                r"(?:(?:income|उत्पन्न|आय|कमवता|कमवतो)\s*(?:is|of|आहे|है|:)?\s*(?:₹|rs\.?)?\s*|₹\s*)(\d[\d,]*\d|\d+)",
                ascii_text
            )
            if income_num_match:
                cleaned_num = income_num_match.group(1).replace(",", "")
                val = float(cleaned_num)
                if val >= 500:
                    profile.annual_income = val

        def _matches(needle: str) -> bool:
            if any(ord(ch) > 127 for ch in needle):
                return needle in lowered
            return bool(re.search(rf"\b{re.escape(needle)}\b", lowered))

        # 5. Extract State
        for key, canonical_state in cls.STATE_MAP.items():
            if _matches(key):
                profile.state = canonical_state
                break

        # 6. Extract Occupation
        for key, canonical_occ in cls.OCCUPATION_MAP.items():
            if _matches(key):
                profile.occupation = canonical_occ
                break

        # 7. Extract Caste / Category
        for key, canonical_cat in cls.CATEGORY_MAP.items():
            if _matches(key):
                profile.caste_category = canonical_cat
                break

        # 8. Extract Gender
        for key, canonical_gender in cls.GENDER_MAP.items():
            if _matches(key):
                profile.gender = canonical_gender
                break

        # 9. Extract Education Level
        if any(term in lowered for term in ["10th", "ssc", "१० वी", "दसवी", "10 वी"]):
            profile.education_level = "10th_pass"
        elif any(term in lowered for term in ["12th", "hsc", "१२ वी", "बारहवी", "12 वी"]):
            profile.education_level = "12th_pass"
        elif any(term in lowered for term in ["graduate", "degree", "पदवी", "स्नातक"]):
            profile.education_level = "graduate"
        elif any(term in lowered for term in ["postgraduate", "master", "पदव्युत्तर", "परास्नातक"]):
            profile.education_level = "postgraduate"

        # 10. Extract Disability Status
        if any(term in lowered for term in ["disabled", "handicapped", "दिव्यांग", "अपंग", "disability"]):
            profile.is_differently_abled = True

        return profile
