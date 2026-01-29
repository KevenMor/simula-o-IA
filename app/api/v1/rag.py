"""RAG query endpoint."""

from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.requests import RAGQueryRequest
from app.models.responses import RAGQueryResponse, Source
from app.core.rag_engine import rag_engine
from app.utils.validators import sanitize_text, validate_knowledge_base_id
from app.utils.logger import logger
from app.utils.auth import verify_api_key
import time

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/query", response_model=RAGQueryResponse, dependencies=[Depends(verify_api_key)])
async def query_rag(request: RAGQueryRequest):
    """Query knowledge base using RAG."""
    try:
        start_time = time.time()
        
        # Validate and sanitize input
        query = sanitize_text(request.query)
        if not query:
            raise HTTPException(status_code=400, detail="Query não pode estar vazia")
        
        if not validate_knowledge_base_id(request.knowledge_base_id):
            raise HTTPException(status_code=400, detail="ID da base de conhecimento inválido")
        
        # Query RAG engine
        result = await rag_engine.query(
            query=query,
            knowledge_base_id=request.knowledge_base_id,
            max_results=request.max_results,
            min_score=request.min_score
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        logger.info(f"RAG query completed in {processing_time}ms")
        
        return RAGQueryResponse(
            answer=result["answer"],
            sources=[
                Source(**source) for source in result["sources"]
            ],
            confidence=result["confidence"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in RAG query endpoint: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar consulta RAG")
