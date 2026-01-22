from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.core.security import decode_access_token, hash_password
from app.core.cache import cache
from app.models.user import User, APIKey
from app.core.config import get_settings
import time

settings = get_settings()
security = HTTPBearer()

# ============= Authentication Dependencies =============

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    JWT token থেকে current user বের করবে
    
    Usage:
        @app.get("/profile")
        async def profile(user: User = Depends(get_current_user)):
            return {"email": user.email}
    """
    token = credentials.credentials
    
    # Token decode করবে
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # User ID extract করবে
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Database থেকে user fetch করবে
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Active user check করবে"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Admin access check করবে"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def verify_api_key(
    x_api_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    API Key authentication (JWT এর alternative)
    Header: X-API-Key: sk_xxxxx
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required"
        )
    
    # API key hash করবে
    key_hash = hash_password(x_api_key)
    
    # Database এ check করবে
    result = await db.execute(
        select(APIKey).where(
            APIKey.key_hash == key_hash,
            APIKey.is_active == True
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # User fetch করবে
    result = await db.execute(
        select(User).where(User.id == api_key.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user

# ============= Rate Limiting Dependency =============

def rate_limit(max_requests: int = None):
    """
    Rate limiting dependency
    
    Usage:
        @app.get("/expensive", dependencies=[Depends(rate_limit(10))])
        async def expensive_endpoint():
            ...
    """
    max_req = max_requests or settings.RATE_LIMIT_PER_MINUTE
    
    async def check_rate_limit(
        current_user: User = Depends(get_current_user)
    ):
        # Cache key: user_id + current minute
        current_minute = int(time.time() / 60)
        key = f"rate_limit:{current_user.id}:{current_minute}"
        
        # Increment counter
        count = cache.increment(key, ttl=60)
        
        if count > max_req:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {max_req} requests per minute."
            )
        
        return True
    
    return check_rate_limit