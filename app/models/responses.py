"""Response models for API endpoints."""

from typing import List, Optional, Any
from pydantic import BaseModel, Field


class Source(BaseModel):
    """RAG source document."""

    content: str = Field("", description="Source content")
    score: float = Field(0.0, description="Similarity score")
    metadata: Optional[dict] = Field(default_factory=dict, description="Optional metadata")


class RAGQueryResponse(BaseModel):
    """Response for RAG query."""

    answer: str = Field(..., description="Generated answer")
    sources: List[Source] = Field(default_factory=list, description="Source documents")
    confidence: float = Field(0.0, description="Confidence score")


class HumanizeResponse(BaseModel):
    """Response from humanization."""

    humanized_response: str = Field(..., description="Humanized text")
    tone_applied: str = Field(..., description="Tone applied")


class SentimentAnalysisResponse(BaseModel):
    """Response from sentiment analysis."""

    sentiment: str = Field(..., description="positive, neutral, or negative")
    score: float = Field(..., description="Sentiment score")
    emotions: List[str] = Field(default_factory=list, description="Detected emotions")
    requires_human: bool = Field(False, description="Whether human review is recommended")
    urgency_level: str = Field("normal", description="Urgency level")


class RAGContext(BaseModel):
    """RAG context in process response."""

    sources_used: int = Field(0, description="Number of sources used")
    confidence: float = Field(0.0, description="Confidence score")


class ProcessingMetadata(BaseModel):
    """Processing metadata."""

    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    model_used: str = Field(..., description="Model used")
    cost_estimate: float = Field(0.0, description="Estimated cost in USD")


class ProcessMessageResponse(BaseModel):
    """Response from full message processing."""

    response: str = Field(..., description="Final humanized response")
    sentiment_analysis: SentimentAnalysisResponse = Field(..., description="Sentiment result")
    rag_context: RAGContext = Field(..., description="RAG context")
    metadata: ProcessingMetadata = Field(..., description="Processing metadata")
