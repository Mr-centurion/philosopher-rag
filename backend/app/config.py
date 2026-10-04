from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "Comparative Philosophy RAG"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "*"
    ]
    
    # API Keys
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    
    # Model Selection
    DEFAULT_LLM_PROVIDER: str = "gemini"  # "gemini", "groq", or "local"
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # Retrieval Configuration
    EMBEDDING_PROVIDER: str = "auto"  # "gemini", "local", "auto"
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "chroma_db")
    CORPUS_DIR: str = str(BASE_DIR / "app" / "data" / "corpus")
    
    VECTOR_TOP_K: int = 5
    BM25_TOP_K: int = 5
    RERANK_TOP_K: int = 3
    
    # Evaluation settings
    EVAL_DATASET_PATH: str = str(BASE_DIR / "app" / "data" / "eval_dataset.json")
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
