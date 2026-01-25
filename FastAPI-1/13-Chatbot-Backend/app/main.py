from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import (
    AIBackendException, 
    ai_exception_handler,
    LLMException,
    VectorStoreException,
    RateLimitException
)
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.api.v1 import chat, upload, agent, auth
from app.db.session import engine
from app.db.models import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)

# Exception handlers
app.add_exception_handler(AIBackendException, ai_exception_handler)
app.add_exception_handler(LLMException, ai_exception_handler)
app.add_exception_handler(VectorStoreException, ai_exception_handler)
app.add_exception_handler(RateLimitException, ai_exception_handler)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(upload.router, prefix=settings.API_V1_STR, tags=["upload"])
app.include_router(agent.router, prefix=settings.API_V1_STR, tags=["agent"])

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} started")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)