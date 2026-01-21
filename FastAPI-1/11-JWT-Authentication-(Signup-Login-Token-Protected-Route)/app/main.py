from fastapi import FastAPI, Depends
from app.db.base import Base
from app.db.session import engine
from app.api.auth import router as auth_router
from app.dependencies.auth import get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)


@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": current_user
    }
