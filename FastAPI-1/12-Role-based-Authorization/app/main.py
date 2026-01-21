from fastapi import FastAPI, Depends
from app.db.base import Base
from app.db.session import engine
from app.api.auth import router as auth_router
from app.dependencies.auth import get_current_user, require_admin

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)


@app.get("/protected")
def protected_route(current_user=Depends(get_current_user)):
    return {
        "message": "Authenticated user",
        "user": current_user
    }


@app.get("/admin")
def admin_route(current_user=Depends(require_admin)):
    return {
        "message": "Welcome admin",
        "admin": current_user
    }
