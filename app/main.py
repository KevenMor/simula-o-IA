"""FastAPI application main file."""

import os
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from contextlib import asynccontextmanager
import time
from app.config import settings
from app.utils.logger import logger
from app.utils.rate_limiter import check_rate_limit_middleware
from app.utils.auth import verify_api_key
from app.api.v1 import rag, sentiment, humanize, process, qa, settings as settings_router, training

SERVE_CHAT_SPA = os.getenv("SERVE_CHAT_SPA", "").strip().lower() in ("1", "true", "yes")
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    try:
        logger.info("Starting AI Agent API...")
        logger.info(f"Environment: {settings.environment}")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
    yield
    # Shutdown
    try:
        logger.info("Shutting down AI Agent API...")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="AI Agent API",
    description="RAG, Sentiment Analysis & Humanization Platform for WhatsApp Chatbots",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.middleware("http")(check_rate_limit_middleware)


# Request logging middleware (must be after rate limiting)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"{request.method} {request.url.path} - "
            f"Error: {str(e)} - "
            f"Time: {process_time:.3f}s"
        )
        raise


# Health check endpoint (no auth required)
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment
    }


# Include routers
app.include_router(rag.router, prefix="/api/v1")
app.include_router(sentiment.router, prefix="/api/v1")
app.include_router(humanize.router, prefix="/api/v1")
app.include_router(process.router, prefix="/api/v1")
app.include_router(qa.router, prefix="/api/v1")
app.include_router(settings_router.router, prefix="/api/v1")
app.include_router(training.router, prefix="/api/v1")


# SPA do chat (hotel/creche) — deploy "só a página" para o cliente
if SERVE_CHAT_SPA and STATIC_DIR.exists():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve SPA: arquivos estáticos ou index.html para rotas do frontend."""
        if full_path.startswith("api/") or full_path in ("docs", "redoc", "openapi.json", "health"):
            raise HTTPException(status_code=404, detail="Not found")
        path = (STATIC_DIR / full_path).resolve()
        if not str(path).startswith(str(STATIC_DIR.resolve())):
            raise HTTPException(status_code=404, detail="Not found")
        if path.is_file():
            return FileResponse(path)
        return FileResponse(STATIC_DIR / "index.html")
else:
    @app.get("/")
    async def root():
        """Root endpoint (quando não está servindo a SPA do chat)."""
        return {
            "message": "AI Agent API - RAG, Sentiment Analysis & Humanization Platform",
            "docs": "/docs",
            "health": "/health"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )
