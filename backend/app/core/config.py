import os
from typing import Optional
from pydantic import BaseModel, Field

class Settings(BaseModel):
    app_env: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    debug_retrieval: bool = Field(default_factory=lambda: os.getenv("DEBUG_RETRIEVAL", "true").lower() in ("true", "1", "yes"))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    
    # API Settings
    api_host: str = Field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = Field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    
    # PostgreSQL Settings
    postgres_host: str = Field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    postgres_port: int = Field(default_factory=lambda: int(os.getenv("POSTGRES_PORT", "5432")))
    postgres_db: str = Field(default_factory=lambda: os.getenv("POSTGRES_DB", "gov_scheme_db"))
    postgres_user: str = Field(default_factory=lambda: os.getenv("POSTGRES_USER", "postgres"))
    postgres_password: str = Field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", ""))
    
    # Qdrant Settings
    qdrant_host: str = Field(default_factory=lambda: os.getenv("QDRANT_HOST", "localhost"))
    qdrant_port: int = Field(default_factory=lambda: int(os.getenv("QDRANT_PORT", "6333")))
    qdrant_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("QDRANT_API_KEY", None))
    qdrant_collection: str = Field(default_factory=lambda: os.getenv("QDRANT_COLLECTION", "gov_schemes"))
    
    # Embeddings & Reranking Models
    embedding_model_name: str = Field(
        default_factory=lambda: os.getenv(
            "EMBEDDING_MODEL_NAME",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    )
    reranker_model_name: str = Field(
        default_factory=lambda: os.getenv("RERANKER_MODEL_NAME", "BAAI/bge-reranker-base")
    )
    
    # LLM Settings
    llm_provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "gemini"))
    gemini_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", None))
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", None))
    llm_model: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "gemini-1.5-flash"))

    @property
    def postgres_uri(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

settings = Settings()
