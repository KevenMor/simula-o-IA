"""Supabase client initialization."""

from typing import Optional

from supabase import create_client, Client
from app.config import settings
from app.utils.logger import logger


class SupabaseClient:
    """Supabase client wrapper.

    For now this client is optional: if initialization fails (e.g. library
    incompatibility), we log and continue with `client = None` so that
    non-RAG features keep working.
    """

    def __init__(self) -> None:
        self.client: Optional[Client] = None
        try:
            self.client = create_client(settings.supabase_url, settings.supabase_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client (RAG disabled): {e}")
            self.client = None

    def get_client(self) -> Optional[Client]:
        """Get the Supabase client instance, may be None if init failed."""
        return self.client


# Global instance
supabase_client = SupabaseClient()
