import logging
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.rag.schema import (
    QueryRequest,
    QueryResponse,
    ThinkerMetadata,
    EvaluationSummary,
    SessionHistoryResponse
)
from app.graph.workflow import run_query_workflow
from app.rag.ingest import ingestion_pipeline
from app.core.session_store import session_store
from app.core.evaluator import evaluator_service

logger = logging.getLogger("philosophy_rag.api")
router = APIRouter()

@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Execute multi-thinker comparative philosophical query",
    status_code=status.HTTP_200_OK
)
async def query_endpoint(request: QueryRequest):
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty."
            )
        
        logger.info(f"Processing query: '{request.question[:60]}...' for thinkers: {request.thinkers}")
        response = await run_query_workflow(
            question=request.question.strip(),
            requested_thinkers=request.thinkers,
            session_id=request.session_id or "default_session"
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Internal error processing query: {e}", exc_info=False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your philosophical query. Please try again."
        )

@router.get(
    "/thinkers",
    response_model=List[ThinkerMetadata],
    summary="Get all available philosophers with corpus statistics",
    status_code=status.HTTP_200_OK
)
async def get_thinkers():
    try:
        return ingestion_pipeline.get_thinkers_metadata()
    except Exception as e:
        logger.error(f"Error fetching thinkers: {e}", exc_info=False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load philosophical corpus metadata."
        )

@router.get(
    "/health",
    summary="System health check",
    status_code=status.HTTP_200_OK
)
async def health_check():
    return {
        "status": "healthy",
        "service": "Comparative Philosophy RAG API",
        "version": "1.0.0",
        "vector_store_active": True,
        "bm25_active": True,
        "thinkers_count": len(ingestion_pipeline.get_thinkers_metadata())
    }

@router.post(
    "/evaluate",
    response_model=EvaluationSummary,
    summary="Trigger the automated RAG evaluation benchmark suite",
    status_code=status.HTTP_200_OK
)
async def run_evaluation():
    try:
        logger.info("Starting automated evaluation benchmark suite...")
        summary = await evaluator_service.run_evaluation()
        return summary
    except Exception as e:
        logger.error(f"Evaluation error: {e}", exc_info=False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete evaluation benchmark run."
        )

@router.get(
    "/session/{session_id}/history",
    response_model=SessionHistoryResponse,
    summary="Retrieve multi-turn chat history for a session",
    status_code=status.HTTP_200_OK
)
async def get_session_history(session_id: str):
    try:
        return session_store.get_history(session_id)
    except Exception as e:
        logger.error(f"Error fetching session history: {e}", exc_info=False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve session conversation history."
        )

@router.delete(
    "/session/{session_id}",
    summary="Clear conversation history for a session",
    status_code=status.HTTP_200_OK
)
async def clear_session(session_id: str):
    session_store.clear(session_id)
    return {"message": f"Session {session_id} history cleared successfully."}
