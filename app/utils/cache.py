"""Simple in-memory cache for LLM responses to reduce token costs."""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.config import settings
from app.utils.logger import logger


class ResponseCache:
    """Cache for LLM responses to avoid duplicate API calls."""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = settings.cache_ttl_seconds
    
    def _make_key(self, tenant_id: str, question: str, context_hash: str) -> str:
        """Generate cache key from question and context."""
        # Normalize question (lowercase, strip)
        normalized = question.lower().strip()
        # Create hash
        key_data = f"{tenant_id}:{normalized}:{context_hash}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, tenant_id: str, question: str, context_hash: str) -> Optional[str]:
        """Get cached response if available and not expired."""
        key = self._make_key(tenant_id, question, context_hash)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        expires_at = entry.get("expires_at")
        
        if expires_at and datetime.now() > expires_at:
            # Expired, remove it
            del self.cache[key]
            return None
        
        logger.info(f"Cache hit for question: {question[:50]}...")
        return entry.get("response")
    
    def set(self, tenant_id: str, question: str, context_hash: str, response: str):
        """Cache a response."""
        key = self._make_key(tenant_id, question, context_hash)
        
        expires_at = datetime.now() + timedelta(seconds=self.ttl_seconds)
        
        self.cache[key] = {
            "response": response,
            "expires_at": expires_at,
            "created_at": datetime.now(),
        }
        
        logger.info(f"Cached response for question: {question[:50]}...")
    
    def clear_expired(self):
        """Remove expired entries (call periodically)."""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.get("expires_at") and entry["expires_at"] < now
        ]
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")


# Global cache instance
response_cache = ResponseCache()
