import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.endpoints import router as api_router
from app.rag.ingest import ingestion_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("philosophy_rag")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Philosophy RAG Knowledge Base...")
    try:
        ingestion_pipeline.run()
        logger.info("Philosophical corpus and indices successfully loaded!")
    except Exception as e:
        logger.error(f"Error during corpus initialization: {e}")
    yield
    logger.info("Shutting down Philosophy RAG application...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Thinker Comparative Philosophy RAG with LangGraph, Hybrid Search, and Guardrails",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Comparative Philosophy RAG API",
        "docs_url": "/docs",
        "health_url": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
