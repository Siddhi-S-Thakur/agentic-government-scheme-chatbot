import pytest
from app.schemas.profile_schema import UserProfile
from app.profile.extractor import ProfileExtractor

def test_extract_english_profile():
    text = "I am a 28 years old farmer from Maharashtra with annual income of 2.5 lakh"
    profile = ProfileExtractor.extract_from_text(text)

    assert profile.age == 28
    assert profile.occupation == "farmer"
    assert profile.state == "Maharashtra"
    assert profile.annual_income == 250000.0

def test_extract_marathi_profile():
    # Marathi text: "मी महाराष्ट्रातील शेतकरी आहे, वय ३० वर्षे, उत्पन्न १ लाख"
    text = "मी महाराष्ट्रातील शेतकरी आहे, वय ३० वर्षे, उत्पन्न १ लाख"
    profile = ProfileExtractor.extract_from_text(text)

    assert profile.state == "Maharashtra"
    assert profile.occupation == "farmer"
    assert profile.age == 30
    assert profile.annual_income == 100000.0
    assert profile.preferred_language == "mr"

def test_extract_hindi_profile():
    # Hindi text: "मैं 21 साल का छात्र हूँ, उत्तर प्रदेश से, अनुसूचित जाति"
    text = "मैं 21 साल का छात्र हूँ, उत्तर प्रदेश से, अनुसूचित जाति"
    profile = ProfileExtractor.extract_from_text(text)

    assert profile.age == 21
    assert profile.occupation == "student"
    assert profile.state == "Uttar Pradesh"
    assert profile.caste_category == "SC"
    assert profile.preferred_language == "hi"

def test_progressive_profile_building():
    # Turn 1: User says only occupation and state
    p1 = ProfileExtractor.extract_from_text("I am a farmer from Maharashtra")
    assert p1.occupation == "farmer"
    assert p1.state == "Maharashtra"
    assert p1.age is None
    assert p1.annual_income is None

    # Turn 2: User follows up with age and income
    p2 = ProfileExtractor.extract_from_text("My age is 35 and income is ₹1,80,000", existing_profile=p1)
    assert p2.occupation == "farmer"
    assert p2.state == "Maharashtra"
    assert p2.age == 35
    assert p2.annual_income == 180000.0

def test_interaction_mode_preference():
    p1 = ProfileExtractor.extract_from_text("Please switch to MCQ mode")
    assert p1.interaction_mode == "mcq"

    p2 = ProfileExtractor.extract_from_text("Switch back to normal text mode", existing_profile=p1)
    assert p2.interaction_mode == "text"
