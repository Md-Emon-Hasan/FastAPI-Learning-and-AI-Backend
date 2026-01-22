from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.core.config import get_settings
from app.core.database import init_db
from app.core.middleware import (
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    setup_cors
)
from app.core.exceptions import setup_exception_handlers
from app.core.cache import cache

# API Routes import করবো
from app.api.routes import auth, chat, upload, agent

# Settings
settings = get_settings()

# Logging setup
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup এবং shutdown events
    
    Startup:
    - Database tables create করবে
    - Vector store load করবে (যদি থাকে)
    - Cache cleanup schedule করবে
    
    Shutdown:
    - Connections close করবে
    - Vector store save করবে
    """
    # ========== STARTUP ==========
    logger.info("Starting up application...")
    
    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    
    # Load vector store if exists
    try:
        from app.services.vector_db import vector_store
        import os
        vector_path = settings.VECTOR_DB_PATH
        if os.path.exists(f"{vector_path}.index"):
            logger.info("Loading existing vector store...")
            vector_store.load(vector_path)
            logger.info(f"Loaded {vector_store.index.ntotal} vectors")
        else:
            logger.info("No existing vector store found. Starting fresh.")
    except Exception as e:
        logger.warning(f"Could not load vector store: {e}")
    
    # Clear expired cache entries
    logger.info("Cleaning up expired cache entries...")
    cache.clear_expired()
    
    logger.info("Application startup complete!")
    
    yield
    
    # ========== SHUTDOWN ==========
    logger.info("Shutting down application...")
    
    # Save vector store
    try:
        from app.services.vector_db import vector_store
        logger.info("Saving vector store...")
        vector_store.save(settings.VECTOR_DB_PATH)
        logger.info("Vector store saved successfully")
    except Exception as e:
        logger.error(f"Error saving vector store: {e}")
    
    logger.info("Application shutdown complete!")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready AI Backend with FastAPI, PostgreSQL, FAISS, and Groq LLM",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# ========== Middleware Setup ==========
setup_cors(app)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.RATE_LIMIT_PER_MINUTE,
    window=60
)

# ========== Exception Handlers ==========
setup_exception_handlers(app)

# ========== Routes ==========
app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")

# ========== Health Check ==========
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    """
    Detailed health check
    
    Checks:
    - Database connection
    - Cache availability
    - Vector store status
    """
    health_status = {
        "status": "healthy",
        "checks": {}
    }
    
    # Check database
    try:
        from app.core.database import engine
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check cache
    try:
        cache.set("health_check", "ok", ttl=10)
        result = cache.get("health_check")
        health_status["checks"]["cache"] = "healthy" if result == "ok" else "unhealthy"
    except Exception as e:
        health_status["checks"]["cache"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check vector store
    try:
        from app.services.vector_db import vector_store
        health_status["checks"]["vector_store"] = {
            "status": "healthy",
            "vectors_count": vector_store.index.ntotal
        }
    except Exception as e:
        health_status["checks"]["vector_store"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )