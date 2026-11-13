from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.api.users import router as user_router
from app.core.exceptions import AppException
from app.schemas.error import ErrorResponse

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

app.include_router(
    user_router,
    prefix=settings.API_PREFIX
)

# App-level custom exceptions
@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException
):
    error = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error.dict()
    )

# Validation errors (override FastAPI default)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    error = ErrorResponse(
        error_code="VALIDATION_ERROR",
        message="Invalid request data",
        details=exc.errors()
    )
    return JSONResponse(
        status_code=422,
        content=error.dict()
    )

@app.get("/")
def health_check():
    return {
        "app_name": settings.APP_NAME,
        "env": settings.ENV
    }
