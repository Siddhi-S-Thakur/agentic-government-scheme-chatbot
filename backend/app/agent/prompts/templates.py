from typing import Any

# Multilingual follow-up questions when information is missing
CLARIFICATION_QUESTIONS = {
    "state": {
        "en": "Which state do you currently reside in? (Many welfare schemes are state-specific)",
        "hi": "आप वर्तमान में किस राज्य के निवासी हैं? (कई योजनाएं राज्य-विशिष्ट होती हैं)",
        "mr": "तुम्ही सध्या कोणत्या राज्यात राहता? (अनेक कल्याणकारी योजना राज्य-विशिष्ट असतात)"
    },
    "occupation": {
        "en": "What is your current occupation or profession? (e.g., Farmer, Student, Unemployed)",
        "hi": "आपका वर्तमान व्यवसाय क्या है? (जैसे: किसान, छात्र/विद्यार्थी, बेरोजगार)",
        "mr": "तुमचा सध्याचा व्यवसाय काय आहे? (उदा. शेतकरी, विद्यार्थी, बेरोजगार)"
    },
    "annual_income": {
        "en": "What is your approximate annual household income in rupees?",
        "hi": "आपकी अनुमानित वार्षिक पारिवारिक आय (रुपये में) कितनी है?",
        "mr": "तुमचे अंदाजे वार्षिक कौटुंबिक उत्पन्न (रुपयांमध्ये) किती आहे?"
    },
    "age": {
        "en": "What is your current age in years?",
        "hi": "आपकी वर्तमान आयु (उम्र) कितने वर्ष है?",
        "mr": "तुमचे सध्याचे वय किती वर्षे आहे?"
    },
    "caste_category": {
        "en": "Which social category do you belong to? (General, SC, ST, OBC, EWS)",
        "hi": "आप किस सामाजिक वर्ग से संबंधित हैं? (सामान्य, अनुसूचित जाति, अनुसूचित जनजाति, अन्य पिछड़ा वर्ग)",
        "mr": "तुम्ही कोणत्या सामाजिक प्रवर्गातील आहात? (खुला, अनुसूचित जाती, अनुसूचित जमाती, इतर मागास वर्ग)"
    }
}

# Standard MCQ Option Banks for optional MCQ interaction mode
MCQ_OPTION_BANKS = {
    "occupation": [
        {"id": "occ_farmer", "label_en": "Farmer / Agriculture", "label_hi": "किसान / कृषि", "label_mr": "शेतकरी / कृषी", "field_name": "occupation", "value": "farmer"},
        {"id": "occ_student", "label_en": "Student", "label_hi": "विद्यार्थी / छात्र", "label_mr": "विद्यार्थी", "field_name": "occupation", "value": "student"},
        {"id": "occ_unemployed", "label_en": "Unemployed / Looking for work", "label_hi": "बेरोजगार", "label_mr": "बेरोजगार", "field_name": "occupation", "value": "unemployed"},
        {"id": "occ_destitute", "label_en": "Destitute / Senior Citizen / Disabled", "label_hi": "निराधार / वरिष्ठ नागरिक / दिव्यांग", "label_mr": "निराधार / ज्येष्ठ नागरिक / दिव्यांग", "field_name": "occupation", "value": "destitute"}
    ],
    "state": [
        {"id": "state_mh", "label_en": "Maharashtra", "label_hi": "महाराष्ट्र", "label_mr": "महाराष्ट्र", "field_name": "state", "value": "Maharashtra"},
        {"id": "state_gj", "label_en": "Gujarat", "label_hi": "गुजरात", "label_mr": "गुजरात", "field_name": "state", "value": "Gujarat"},
        {"id": "state_up", "label_en": "Uttar Pradesh", "label_hi": "उत्तर प्रदेश", "label_mr": "उत्तर प्रदेश", "field_name": "state", "value": "Uttar Pradesh"},
        {"id": "state_other", "label_en": "Other State / Central", "label_hi": "अन्य राज्य / केंद्र", "label_mr": "इतर राज्य / केंद्र", "field_name": "state", "value": "Other"}
    ],
    "annual_income": [
        {"id": "inc_1", "label_en": "Below ₹21,000 / year", "label_hi": "₹21,000 प्रति वर्ष से कम", "label_mr": "वार्षिक ₹21,000 पेक्षा कमी", "field_name": "annual_income", "value": 20000.0},
        {"id": "inc_2", "label_en": "₹21,000 to ₹2.5 Lakh", "label_hi": "₹21,000 से ₹2.5 लाख", "label_mr": "₹21,000 ते ₹2.5 लाख", "field_name": "annual_income", "value": 150000.0},
        {"id": "inc_3", "label_en": "₹2.5 Lakh to ₹5 Lakh", "label_hi": "₹2.5 लाख से ₹5 लाख", "label_mr": "₹2.5 लाख ते ₹5 लाख", "field_name": "annual_income", "value": 350000.0},
        {"id": "inc_4", "label_en": "Above ₹5 Lakh", "label_hi": "₹5 लाख से अधिक", "label_mr": "₹5 लाख पेक्षा जास्त", "field_name": "annual_income", "value": 600000.0}
    ],
    "caste_category": [
        {"id": "cat_gen", "label_en": "General (Open)", "label_hi": "सामान्य (खुला)", "label_mr": "खुला (General)", "field_name": "caste_category", "value": "General"},
        {"id": "cat_sc", "label_en": "SC (Scheduled Caste)", "label_hi": "अनुसूचित जाति (SC)", "label_mr": "अनुसूचित जाती (SC)", "field_name": "caste_category", "value": "SC"},
        {"id": "cat_st", "label_en": "ST (Scheduled Tribe)", "label_hi": "अनुसूचित जनजाति (ST)", "label_mr": "अनुसूचित जमाती (ST)", "field_name": "caste_category", "value": "ST"},
        {"id": "cat_obc", "label_en": "OBC (Other Backward Class)", "label_hi": "अन्य पिछड़ा वर्ग (OBC)", "label_mr": "इतर मागास प्रवर्ग (OBC)", "field_name": "caste_category", "value": "OBC"}
    ]
}

def format_mcq_options(field_name: str, language: str = "en") -> list[dict[str, Any]]:
    """Format MCQ options tailored to user language."""
    options = MCQ_OPTION_BANKS.get(field_name, [])
    label_key = f"label_{language}"
    formatted = []
    for opt in options:
        formatted.append({
            "id": opt["id"],
            "label": opt.get(label_key, opt["label_en"]),
            "field_name": opt["field_name"],
            "value": opt["value"]
        })
    return formatted
