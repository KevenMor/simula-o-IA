"""Sentiment analysis endpoint."""

from fastapi import APIRouter, HTTPException, Depends
from app.models.requests import SentimentAnalysisRequest
from app.models.responses import SentimentAnalysisResponse
from app.core.sentiment_analyzer import sentiment_analyzer
from app.utils.validators import sanitize_text
from app.utils.logger import logger
from app.utils.auth import verify_api_key

router = APIRouter(prefix="/sentiment", tags=["Sentiment Analysis"])


@router.post("/analyze", response_model=SentimentAnalysisResponse, dependencies=[Depends(verify_api_key)])
async def analyze_sentiment(request: SentimentAnalysisRequest):
    """Analyze sentiment of text."""
    try:
        # Validate and sanitize input
        text = sanitize_text(request.text)
        if not text:
            raise HTTPException(status_code=400, detail="Texto não pode estar vazio")
        
        # Analyze sentiment
        result = await sentiment_analyzer.analyze(
            text=text,
            context=request.context or "general"
        )
        
        logger.info(f"Sentiment analysis: {result['sentiment']} (score: {result['score']:.2f})")
        
        return SentimentAnalysisResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in sentiment analysis endpoint: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao analisar sentimento")
