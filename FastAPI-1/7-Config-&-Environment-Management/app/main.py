from fastapi import FastAPI
from app.core.config import settings
from app.api.users import router as user_router

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

app.include_router(
    user_router,
    prefix=settings.API_PREFIX
)

@app.get("/")
def health_check():
    return {
        "app_name": settings.APP_NAME,
        "environment": settings.ENV,
        "debug": settings.DEBUG
    }
