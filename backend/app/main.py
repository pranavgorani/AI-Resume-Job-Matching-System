from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db
from app.routes import jobs, resumes, candidates, matching, compare, copilot, demo, export, reports

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup
    init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Evidence-First AI Recruitment Intelligence Platform",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Middleware to allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(candidates.router)
app.include_router(matching.router)
app.include_router(compare.router)
app.include_router(copilot.router)
app.include_router(demo.router)
app.include_router(export.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "status": "healthy",
        "docs_url": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "ok"}
