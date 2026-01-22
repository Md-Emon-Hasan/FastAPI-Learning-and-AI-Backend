# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session
# from app.db.session import get_db
# from app.db.models import User, APIKey
# from app.schemas.user import UserCreate, UserResponse, Token
# from app.core.security import (
#     verify_password, 
#     get_password_hash, 
#     create_access_token,
#     generate_api_key,
#     hash_api_key
# )
# from datetime import timedelta
# from app.core.config import settings

# router = APIRouter()

# @router.post("/auth/register", response_model=UserResponse)
# async def register(user_in: UserCreate, db: Session = Depends(get_db)):
#     """Register new user"""
#     # Check if user exists
#     existing_user = db.query(User).filter(User.email == user_in.email).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Create user
#     user = User(
#         email=user_in.email,
#         hashed_password=get_password_hash(user_in.password),
#         full_name=user_in.full_name
#     )
#     db.add(user)
#     db.commit()
#     db.refresh(user)
    
#     return user

# @router.post("/auth/login", response_model=Token)
# async def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db)
# ):
#     """Login and get JWT token"""
#     user = db.query(User).filter(User.email == form_data.username).first()
    
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password"
#         )
    
#     if not user.is_active:
#         raise HTTPException(status_code=400, detail="Inactive user")
    
#     # Create access token
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"user_id": user.id},
#         expires_delta=access_token_expires
#     )
    
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/auth/api-key")
# async def create_api_key(
#     name: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Generate API key for user"""
#     api_key = generate_api_key()
    
#     api_key_record = APIKey(
#         user_id=current_user.id,
#         key_hash=hash_api_key(api_key),
#         name=name
#     )
#     db.add(api_key_record)
#     db.commit()
    
#     return {
#         "api_key": api_key,
#         "name": name,
#         "message": "Store this key securely. It won't be shown again."
#     }



from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, APIKey
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    generate_api_key,
    hash_api_key
)
from app.api.deps import get_current_user
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("/auth/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get JWT token"""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/api-key")
async def create_api_key(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate API key for user"""
    api_key = generate_api_key()
    
    api_key_record = APIKey(
        user_id=current_user.id,
        key_hash=hash_api_key(api_key),
        name=name
    )
    db.add(api_key_record)
    db.commit()
    
    return {
        "api_key": api_key,
        "name": name,
        "message": "Store this key securely. It won't be shown again."
    }