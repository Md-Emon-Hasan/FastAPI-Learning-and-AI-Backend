from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

# Custom Exceptions

class AIBackendException(Exception):
    """Base exception for our application"""
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class LLMException(AIBackendException):
    """LLM related errors"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="LLM_ERROR"
        )

class VectorDBException(AIBackendException):
    """Vector DB related errors"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="VECTOR_DB_ERROR"
        )

class DocumentProcessingException(AIBackendException):
    """Document processing errors"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="DOCUMENT_PROCESSING_ERROR"
        )

# Exception Handlers

async def ai_backend_exception_handler(request: Request, exc: AIBackendException):
    """Custom exception handler"""
    logger.error(
        f"AIBackendException: {exc.message} | "
        f"Code: {exc.error_code} | "
        f"Path: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Pydantic validation error handler
    User input validation fail হলে
    """
    logger.warning(f"Validation error: {exc.errors()} | Path: {request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Database error handler"""
    logger.error(f"Database error: {str(exc)} | Path: {request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "error_code": "DATABASE_ERROR"
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    logger.error(
        f"Unhandled exception: {str(exc)} | "
        f"Type: {type(exc).__name__} | "
        f"Path: {request.url.path}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )

def setup_exception_handlers(app):
    """All exception handlers register করবে"""
    app.add_exception_handler(AIBackendException, ai_backend_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)