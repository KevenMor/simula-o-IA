"""Complete message processing endpoint."""

from fastapi import APIRouter, HTTPException, Depends
from app.models.requests import ProcessMessageRequest
from app.models.responses import (
    ProcessMessageResponse,
    SentimentAnalysisResponse,
    RAGContext,
    ProcessingMetadata
)
from app.core.sentiment_analyzer import sentiment_analyzer
from app.core.rag_engine import rag_engine
from app.core.humanizer import humanizer
from app.utils.validators import sanitize_text, validate_knowledge_base_id
from app.utils.logger import logger
from app.utils.auth import verify_api_key
from datetime import datetime
import time

router = APIRouter(prefix="/process", tags=["Message Processing"])


@router.post("/message", response_model=ProcessMessageResponse, dependencies=[Depends(verify_api_key)])
async def process_message(request: ProcessMessageRequest):
    """Complete message processing pipeline."""
    try:
        start_time = time.time()
        
        # Validate and sanitize input
        message = sanitize_text(request.message)
        if not message:
            raise HTTPException(status_code=400, detail="Mensagem não pode estar vazia")
        
        if not validate_knowledge_base_id(request.knowledge_base_id):
            raise HTTPException(status_code=400, detail="ID da base de conhecimento inválido")
        
        # Step 1: Sentiment Analysis
        sentiment_result = await sentiment_analyzer.analyze(
            text=message,
            context="customer_support"
        )
        
        # Step 2: RAG Query
        rag_result = await rag_engine.query(
            query=message,
            knowledge_base_id=request.knowledge_base_id,
            max_results=5,
            min_score=0.7
        )
        
        # Step 3: Humanize Response
        humanized_result = await humanizer.humanize(
            ai_response=rag_result["answer"],
            tone="friendly",
            customer_sentiment=sentiment_result["sentiment"],
            time_context=_get_time_context()
        )
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Build response
        response = ProcessMessageResponse(
            response=humanized_result["humanized_response"],
            sentiment_analysis=SentimentAnalysisResponse(**sentiment_result),
            rag_context=RAGContext(
                sources_used=len(rag_result["sources"]),
                confidence=rag_result["confidence"]
            ),
            metadata=ProcessingMetadata(
                processing_time_ms=processing_time_ms,
                model_used="gpt-4-turbo",  # From config
                cost_estimate=_estimate_cost(len(message), len(humanized_result["humanized_response"]))
            )
        )
        
        logger.info(
            f"Message processed in {processing_time_ms}ms - "
            f"Sentiment: {sentiment_result['sentiment']}, "
            f"Confidence: {rag_result['confidence']:.2f}"
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in message processing endpoint: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar mensagem")


def _get_time_context() -> str:
    """Get current time context."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    else:
        return "evening"


def _estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Estimate cost in USD (rough estimate)."""
    # GPT-4 Turbo pricing (approximate)
    input_cost_per_1k = 0.01
    output_cost_per_1k = 0.03
    
    input_cost = (input_tokens / 1000) * input_cost_per_1k
    output_cost = (output_tokens / 1000) * output_cost_per_1k
    
    return round(input_cost + output_cost, 4)
