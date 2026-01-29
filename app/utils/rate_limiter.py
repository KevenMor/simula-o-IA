"""Rate limiting utilities."""

from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from app.config import settings
from app.utils.logger import logger


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.max_requests = settings.rate_limit_per_minute
        self.window_seconds = 60
    
    def check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit."""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Get requests in current window
        client_requests = self.requests[client_id]
        client_requests[:] = [
            req_time for req_time in client_requests
            if req_time > window_start
        ]
        
        # Check limit
        if len(client_requests) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return False
        
        # Add current request
        client_requests.append(now)
        return True
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        client_requests = self.requests[client_id]
        client_requests[:] = [
            req_time for req_time in client_requests
            if req_time > window_start
        ]
        
        return max(0, self.max_requests - len(client_requests))


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_rate_limit_middleware(request: Request, call_next):
    """Middleware to check rate limits."""
    # Skip rate limiting for health check
    if request.url.path == "/health":
        return await call_next(request)
    
    # Get client identifier (API key or IP)
    client_id = request.headers.get("X-API-Key") or request.client.host
    
    if not rate_limiter.check_rate_limit(client_id):
        remaining = rate_limiter.get_remaining_requests(client_id)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again later. Remaining: {remaining}"
        )
    
    response = await call_next(request)
    
    # Add rate limit headers
    remaining = rate_limiter.get_remaining_requests(client_id)
    response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response
