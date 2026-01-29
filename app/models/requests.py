"""Request models for API endpoints."""

from typing import Optional
from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    """Request for RAG knowledge base query."""

    query: str = Field(..., description="Search query")
    knowledge_base_id: str = Field(..., description="Knowledge base ID")
    max_results: int = Field(5, ge=1, le=20, description="Max results to return")
    min_score: float = Field(0.7, ge=0.0, le=1.0, description="Minimum similarity score")


class HumanizeRequest(BaseModel):
    """Request for humanizing an AI response."""

    ai_response: str = Field(..., description="AI-generated response to humanize")
    tone: Optional[str] = Field("friendly", description="Tone: friendly, formal, etc.")
    customer_sentiment: Optional[str] = Field(None, description="Customer sentiment")
    time_context: Optional[str] = Field(None, description="Time context: morning, afternoon, evening")


class SentimentAnalysisRequest(BaseModel):
    """Request for sentiment analysis."""

    text: str = Field(..., description="Text to analyze")
    context: Optional[str] = Field("general", description="Context for analysis")


class ProcessMessageRequest(BaseModel):
    """Request for full message processing pipeline."""

    message: str = Field(..., description="Customer message")
    knowledge_base_id: str = Field(..., description="Knowledge base ID")
