import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("talentproof.database")

# Normalize DATABASE_URL for SQLAlchemy 2.0 (PostgreSQL driver psycopg2)
raw_db_url = settings.DATABASE_URL
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
}

if raw_db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # PostgreSQL / Supabase connection tuning
    if "sslmode" not in raw_db_url and "?" not in raw_db_url:
        connect_args["sslmode"] = "require"
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 300,
    })

engine = create_engine(
    raw_db_url,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models import orm  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Safe automated schema upgrades for existing tables
    try:
        is_sqlite = raw_db_url.startswith("sqlite")
        with engine.connect() as conn:
            if is_sqlite:
                # Candidates table checks
                cand_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(candidates)")).fetchall()]
                if "job_id" not in cand_cols:
                    conn.execute(text("ALTER TABLE candidates ADD COLUMN job_id INTEGER REFERENCES jobs(id)"))
                if "processing_status" not in cand_cols:
                    conn.execute(text("ALTER TABLE candidates ADD COLUMN processing_status VARCHAR(50) DEFAULT 'COMPLETED'"))
                if "processing_error" not in cand_cols:
                    conn.execute(text("ALTER TABLE candidates ADD COLUMN processing_error TEXT"))
                
                # Resumes table checks
                res_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(resumes)")).fetchall()]
                if "job_id" not in res_cols:
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN job_id INTEGER REFERENCES jobs(id)"))
                if "original_filename" not in res_cols:
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN original_filename VARCHAR(255)"))
                if "storage_bucket" not in res_cols:
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN storage_bucket VARCHAR(100) DEFAULT 'resume-files'"))
                if "storage_path" not in res_cols:
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN storage_path VARCHAR(500)"))
                if "file_hash" not in res_cols:
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN file_hash VARCHAR(64)"))
                if "processing_status" not in res_cols:
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN processing_status VARCHAR(50) DEFAULT 'COMPLETED'"))
                if "processing_error" not in res_cols:
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN processing_error TEXT"))
                if "resume_version" not in res_cols:
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN resume_version INTEGER DEFAULT 1"))
                if "file_size" not in res_cols:
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN file_size INTEGER"))
                conn.commit()
            else:
                # PostgreSQL safe column migrations
                conn.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS job_id INTEGER REFERENCES jobs(id)"))
                conn.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS processing_status VARCHAR(50) DEFAULT 'COMPLETED'"))
                conn.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS processing_error TEXT"))
                conn.execute(text("ALTER TABLE resumes ADD COLUMN IF NOT EXISTS job_id INTEGER REFERENCES jobs(id)"))
                conn.execute(text("ALTER TABLE resumes ADD COLUMN IF NOT EXISTS original_filename VARCHAR(255)"))
                conn.execute(text("ALTER TABLE resumes ADD COLUMN IF NOT EXISTS storage_bucket VARCHAR(100) DEFAULT 'resume-files'"))
                conn.execute(text("ALTER TABLE resumes ADD COLUMN IF NOT EXISTS storage_path VARCHAR(500)"))
                conn.execute(text("ALTER TABLE resumes ADD COLUMN IF NOT EXISTS file_hash VARCHAR(64)"))
                conn.execute(text("ALTER TABLE resumes ADD COLUMN IF NOT EXISTS processing_status VARCHAR(50) DEFAULT 'COMPLETED'"))
                conn.execute(text("ALTER TABLE resumes ADD COLUMN IF NOT EXISTS processing_error TEXT"))
                conn.execute(text("ALTER TABLE resumes ADD COLUMN IF NOT EXISTS resume_version INTEGER DEFAULT 1"))
                conn.execute(text("ALTER TABLE resumes ADD COLUMN IF NOT EXISTS file_size INTEGER"))
                conn.commit()
    except Exception as e:
        logger.debug(f"[DATABASE INIT] Migration notice: {e}")

