"""RAG engine for knowledge base queries."""

from typing import List, Dict, Any
from app.db.vector_store import vector_store
from app.core.llm_client import llm_client
from app.utils.logger import logger


class RAGEngine:
    """RAG engine for querying knowledge base."""
    
    async def query(
        self,
        query: str,
        knowledge_base_id: str,
        max_results: int = 5,
        min_score: float = 0.7
    ) -> Dict[str, Any]:
        """Query knowledge base and generate answer."""
        try:
            # Generate query embedding
            query_embedding = await vector_store.get_embedding(query)
            
            # Search for similar documents
            sources = await vector_store.search_similar(
                query_embedding=query_embedding,
                knowledge_base_id=knowledge_base_id,
                max_results=max_results,
                min_score=min_score
            )
            
            if not sources:
                return {
                    "answer": "Desculpe, não encontrei informações relevantes sobre isso na base de conhecimento.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Extract content from sources
            context_texts = [src["content"] for src in sources if src.get("content")]
            
            # Generate answer using LLM with context
            answer = await llm_client.generate_with_context(
                user_query=query,
                context=context_texts
            )
            
            # Calculate confidence based on source scores
            avg_score = sum(src.get("score", 0.0) for src in sources) / len(sources) if sources else 0.0
            confidence = min(avg_score, 0.95)  # Cap at 0.95
            
            return {
                "answer": answer,
                "sources": [
                    {
                        "content": src.get("content", ""),
                        "score": src.get("score", 0.0),
                        "metadata": src.get("metadata", {})
                    }
                    for src in sources
                ],
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return {
                "answer": "Desculpe, ocorreu um erro ao processar sua consulta. Por favor, tente novamente.",
                "sources": [],
                "confidence": 0.0
            }

# Global instance
rag_engine = RAGEngine()
