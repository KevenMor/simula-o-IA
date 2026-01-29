"""Vector store operations for RAG."""

from typing import List, Dict, Any, Optional

from supabase import Client
from openai import OpenAI

from app.db.supabase_client import supabase_client
from app.config import settings
from app.utils.logger import logger


class VectorStore:
    """Vector store for semantic search.

    If Supabase is not available, all search methods safely degrade to
    returning an empty list so that the rest of the API continues to work.
    """

    def __init__(self) -> None:
        self.supabase: Optional[Client] = supabase_client.get_client()
        if self.supabase is None:
            logger.warning("Supabase client is not available. RAG search is disabled.")
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.embedding_model = settings.embedding_model

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def search_similar(
        self,
        query_embedding: List[float],
        knowledge_base_id: str,
        max_results: int = 5,
        min_score: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity."""
        if self.supabase is None:
            logger.warning(
                "Supabase client is None. Returning empty results for vector search."
            )
            return []

        try:
            # Use Supabase RPC for vector similarity search
            response = (
                self.supabase.rpc(
                    "match_documents",
                    {
                        "query_embedding": query_embedding,
                        "knowledge_base_id": knowledge_base_id,
                        "match_threshold": min_score,
                        "match_count": max_results,
                    },
                )
                .execute()
            )

            results = []
            for row in response.data or []:
                results.append(
                    {
                        "content": row.get("content", ""),
                        "score": row.get("similarity", 0.0),
                        "metadata": row.get("metadata", {}),
                    }
                )

            return results
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            # Fallback: simple text search if RPC function doesn't exist
            return await self._fallback_search(knowledge_base_id, max_results)

    async def _fallback_search(
        self, knowledge_base_id: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """Fallback search method."""
        if self.supabase is None:
            logger.warning(
                "Supabase client is None. Returning empty results for fallback search."
            )
            return []

        try:
            response = (
                self.supabase.table("knowledge_documents")
                .select("*")
                .eq("knowledge_base_id", knowledge_base_id)
                .limit(max_results)
                .execute()
            )

            return [
                {
                    "content": row.get("content", ""),
                    "score": 0.8,  # Default score
                    "metadata": row.get("metadata", {}),
                }
                for row in response.data or []
            ]
        except Exception as e:
            logger.error(f"Error in fallback search: {e}")
            return []


# Global instance
vector_store = VectorStore()
