from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

class AIBackendException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code

class LLMException(AIBackendException):
    def __init__(self, message: str):
        super().__init__(message, status_code=503)

class VectorStoreException(AIBackendException):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class RateLimitException(AIBackendException):
    def __init__(self):
        super().__init__("Rate limit exceeded", status_code=429)

async def ai_exception_handler(request: Request, exc: AIBackendException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "type": exc.__class__.__name__
        }
    )