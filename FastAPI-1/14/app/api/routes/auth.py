from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.schemas import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    নতুন user registration
    
    Steps:
    1. Email already exists কিনা check করবে
    2. Password hash করবে
    3. User create করবে
    4. User data return করবে
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_verified=False  # Email verification implement করলে True করবো
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    User login - JWT token issue করবে
    
    Steps:
    1. Email দিয়ে user খুঁজবে
    2. Password verify করবে
    3. JWT token generate করবে
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create JWT token
    # Token payload এ user_id এবং email রাখবো
    token = create_access_token(
        data={
            "user_id": user.id,
            "sub": user.email,  # "sub" = subject (standard JWT claim)
            "role": user.role.value
        }
    )
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout():
    """
    Logout endpoint
    
    JWT stateless তাই server-side logout নাই
    Client-side token delete করলেই হবে
    
    Optional: Token blacklist implement করা যায় production এ
    """
    return {"message": "Logged out successfully"}