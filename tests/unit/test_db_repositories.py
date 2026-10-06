import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.repositories import SchemeRepository, ProfileRepository, ConversationRepository
from app.schemas.scheme_schema import SchemeRecord, SchemeEligibilityCriteria
from app.schemas.profile_schema import UserProfile

@pytest.fixture
def db_session():
    # Use isolated in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_scheme_repository_crud(db_session):
    scheme = SchemeRecord(
        scheme_id="test-pm-kisan",
        scheme_name="PM Kisan Test",
        description="Farmer support",
        department="Agri Dept",
        level="central",
        state=None,
        beneficiary_categories=["farmer"],
        scheme_category="Agriculture",
        benefits="₹6000/yr",
        eligibility_criteria=SchemeEligibilityCriteria(min_age=18, occupations=["farmer"]),
        documents_required=["Aadhaar"],
        application_procedure="Apply online",
        official_url="https://pmkisan.gov.in",
        source_department="Govt of India"
    )

    # Save
    SchemeRepository.save(scheme, session=db_session)

    # Retrieve
    retrieved = SchemeRepository.get_by_id("test-pm-kisan", session=db_session)
    assert retrieved is not None
    assert retrieved.scheme_name == "PM Kisan Test"
    assert retrieved.eligibility_criteria.min_age == 18

    # List all
    all_schemes = SchemeRepository.list_all(session=db_session)
    assert len(all_schemes) >= 1
    assert any(s.scheme_id == "test-pm-kisan" for s in all_schemes)

def test_profile_repository_upsert_and_get(db_session):
    profile = UserProfile(
        age=25,
        annual_income=200000.0,
        state="Maharashtra",
        occupation="farmer",
        preferred_language="mr"
    )

    ProfileRepository.upsert_profile(session_id="session_123", profile=profile, session=db_session)

    saved = ProfileRepository.get_profile(session_id="session_123", session=db_session)
    assert saved is not None
    assert saved.age == 25
    assert saved.occupation == "farmer"
    assert saved.preferred_language == "mr"

    # Update profile on next turn
    updated_profile = profile.model_copy(update={"annual_income": 250000.0})
    ProfileRepository.upsert_profile(session_id="session_123", profile=updated_profile, session=db_session)

    reloaded = ProfileRepository.get_profile(session_id="session_123", session=db_session)
    assert reloaded.annual_income == 250000.0

def test_conversation_repository(db_session):
    ConversationRepository.save_message(
        session_id="session_abc",
        role="user",
        content="Hello, find schemes for me",
        session=db_session
    )
    ConversationRepository.save_message(
        session_id="session_abc",
        role="assistant",
        content="What is your state and occupation?",
        session=db_session
    )

    history = ConversationRepository.get_history(session_id="session_abc", session=db_session)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
