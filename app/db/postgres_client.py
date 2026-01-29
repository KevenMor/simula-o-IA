"""PostgreSQL client for direct database access (alternative to Supabase)."""

from typing import Optional
import asyncpg
from app.config import settings
from app.utils.logger import logger


class PostgresClient:
    """PostgreSQL client for vector operations.
    
    This is an alternative to Supabase, allowing direct PostgreSQL access.
    Requires pgvector extension to be installed.
    """
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._connection_string = None
        
    def _get_connection_string(self) -> Optional[str]:
        """Build PostgreSQL connection string from settings."""
        # Check if PostgreSQL settings are available
        postgres_host = getattr(settings, 'postgres_host', None)
        postgres_port = getattr(settings, 'postgres_port', 5432)
        postgres_db = getattr(settings, 'postgres_db', None)
        postgres_user = getattr(settings, 'postgres_user', None)
        postgres_password = getattr(settings, 'postgres_password', None)
        
        if not all([postgres_host, postgres_db, postgres_user, postgres_password]):
            return None
        
        return f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    
    async def initialize(self):
        """Initialize connection pool."""
        connection_string = self._get_connection_string()
        if not connection_string:
            logger.warning("PostgreSQL settings not configured. Using Supabase or local storage.")
            return
        
        try:
            self.pool = await asyncpg.create_pool(
                connection_string,
                min_size=1,
                max_size=10,
            )
            logger.info("PostgreSQL connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            self.pool = None
    
    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed")
    
    async def search_similar_vectors(
        self,
        query_embedding: list[float],
        knowledge_base_id: str,
        max_results: int = 5,
        min_score: float = 0.7,
    ) -> list[dict]:
        """Search for similar documents using vector similarity."""
        if not self.pool:
            logger.warning("PostgreSQL pool not initialized")
            return []
        
        try:
            async with self.pool.acquire() as conn:
                # Query using pgvector cosine similarity
                query = """
                    SELECT 
                        id,
                        content,
                        metadata,
                        1 - (embedding <=> $1::vector) as similarity
                    FROM knowledge_documents
                    WHERE knowledge_base_id = $2
                        AND embedding IS NOT NULL
                        AND (1 - (embedding <=> $1::vector)) >= $3
                    ORDER BY embedding <=> $1::vector
                    LIMIT $4
                """
                
                rows = await conn.fetch(
                    query,
                    query_embedding,
                    knowledge_base_id,
                    min_score,
                    max_results
                )
                
                results = []
                for row in rows:
                    results.append({
                        "content": row["content"],
                        "score": float(row["similarity"]),
                        "metadata": row["metadata"] or {},
                    })
                
                return results
        except Exception as e:
            logger.error(f"Error in PostgreSQL vector search: {e}")
            return []
    
    async def insert_document(
        self,
        knowledge_base_id: str,
        content: str,
        embedding: list[float],
        metadata: Optional[dict] = None,
    ) -> Optional[str]:
        """Insert a document with embedding."""
        if not self.pool:
            logger.warning("PostgreSQL pool not initialized")
            return None
        
        try:
            async with self.pool.acquire() as conn:
                query = """
                    INSERT INTO knowledge_documents 
                    (knowledge_base_id, content, embedding, metadata)
                    VALUES ($1, $2, $3::vector, $4)
                    RETURNING id
                """
                
                result = await conn.fetchrow(
                    query,
                    knowledge_base_id,
                    content,
                    embedding,
                    metadata or {}
                )
                
                return str(result["id"]) if result else None
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            return None


# Global instance
postgres_client = PostgresClient()
