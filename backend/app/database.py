from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
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
    from app.models import orm  # noqa
    Base.metadata.create_all(bind=engine)
    # Ensure job_id column exists on candidates table in case table pre-existed
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # Check if column exists
            if settings.DATABASE_URL.startswith("sqlite"):
                cursor = conn.execute(text("PRAGMA table_info(candidates)"))
                columns = [row[1] for row in cursor.fetchall()]
                if "job_id" not in columns:
                    conn.execute(text("ALTER TABLE candidates ADD COLUMN job_id INTEGER REFERENCES jobs(id)"))
                    conn.commit()
            else:
                conn.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS job_id INTEGER REFERENCES jobs(id)"))
                conn.commit()
    except Exception as e:
        print(f"Migration notice: {e}")

