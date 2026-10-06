import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine():
    """
    Creates a database engine:
    Attempts PostgreSQL connection based on settings, with automatic
    fallback to SQLite for offline development and test environments.
    """
    postgres_url = settings.postgres_uri
    use_sqlite_fallback = os.getenv("USE_SQLITE_FALLBACK", "true").lower() in ("true", "1", "yes")

    # If PostgreSQL credentials are the default placeholders or explicitly offline, use SQLite
    if "your_postgres_password_here" in postgres_url or use_sqlite_fallback:
        sqlite_url = os.getenv("SQLITE_URL", "sqlite:///./data/gov_schemes.db")
        logger.info(f"Connecting to database using SQLite: {sqlite_url}")
        return create_engine(sqlite_url, connect_args={"check_same_thread": False})

    try:
        logger.info(f"Connecting to PostgreSQL database at {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
        engine = create_engine(postgres_url, pool_pre_ping=True)
        # Test connection
        with engine.connect() as conn:
            pass
        return engine
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL ({e}). Falling back to SQLite.")
        sqlite_url = "sqlite:///./data/gov_schemes.db"
        return create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = get_engine()
SessionFactory = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def init_db(target_engine=None):
    """Initialize database tables."""
    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)

def get_db_session():
    """Context manager or dependency for DB sessions."""
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()
