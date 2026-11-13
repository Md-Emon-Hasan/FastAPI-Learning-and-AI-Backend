from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth_schema import RegisterRequest
from app.schemas.auth_schema import LoginRequest
from app.schemas.auth_schema import TokenResponse
from app.schemas.response_schema import APIResponse
from app.services.auth_service import AuthService
from app.services.auth_service import get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=APIResponse)
def register_user(
    request: RegisterRequest,
    db = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = auth_service.register_user(db, email=request.email, password=request.password)
    if not user:
        raise HTTPException(status_code=400, detail="User already exists")
    return APIResponse(
    status="success",
    data={"user_id": user.id},
    error=None
)

@router.post("/login", response_model=APIResponse)
def login_user(
    request: LoginRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = auth_service.authenticate_user(
        db,
        email=request.email,
        password=request.password
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth_service.generate_token(user)

    return APIResponse(
        status="success",
        data={
            "access_token": token,
            "token_type": "bearer"
        },
        error=None
    )