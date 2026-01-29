"""Authentication utilities."""

from fastapi import Request, HTTPException
from app.config import settings


async def verify_api_key(request: Request):
    """Verify API key from header."""
    api_key = request.headers.get("X-API-Key")
    
    # Log para debug (remover em produção)
    from app.utils.logger import logger
    logger.debug(f"Received API key: {api_key[:20] if api_key else 'None'}...")
    logger.debug(f"Expected API key: {settings.api_key_n8n[:20]}...")
    
    if not api_key:
        logger.warning("No API key provided in request")
        raise HTTPException(status_code=401, detail="API key não fornecida")
    
    if api_key.strip() != settings.api_key_n8n.strip():
        logger.warning(f"API key mismatch. Received: {api_key[:30]}..., Expected: {settings.api_key_n8n[:30]}...")
        raise HTTPException(status_code=401, detail="API key inválida")
    
    return api_key
