import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
# Load .env files into environment
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")


class Settings(BaseSettings):
    APP_NAME: str = "TalentProof AI"
    TAGLINE: str = "Don't just rank resumes. Prove the match."
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Environment check for serverless environments (Vercel / AWS Lambda)
    IS_SERVERLESS: bool = os.getenv("VERCEL") == "1" or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:////tmp/talentproof.db" if (os.getenv("VERCEL") == "1" or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None) else f"sqlite:///{BASE_DIR}/talentproof.db"
    )
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Hugging Face (Fallback AI)
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    HF_MODEL: str = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    
    # Supabase (Database, pgvector, and Storage)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", os.getenv("NEXT_PUBLIC_SUPABASE_URL", ""))
    SUPABASE_PUBLISHABLE_KEY: str = os.getenv("SUPABASE_PUBLISHABLE_KEY", os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY", ""))
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "resumes")
    
    # Uploads
    UPLOAD_DIR: Path = Path("/tmp/uploads") if (os.getenv("VERCEL") == "1" or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None) else (BASE_DIR / "uploads")
    
    # Default Match Weights (recruiter configurable)
    WEIGHT_REQUIRED_SKILLS: float = 0.35
    WEIGHT_RELEVANT_EXP: float = 0.20
    WEIGHT_PROJECT_EVIDENCE: float = 0.15
    WEIGHT_EDUCATION_CERT: float = 0.10
    WEIGHT_PREFERRED_SKILLS: float = 0.10
    WEIGHT_DOMAIN_RELEVANCE: float = 0.05
    WEIGHT_EVIDENCE_CONFIDENCE: float = 0.05

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
