from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, APIKey
from app.core.security import decode_access_token, verify_password
from typing import Optional
from datetime import datetime

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency: Get current user from JWT token"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

async def verify_api_key(
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
) -> User:
    """Dependency: Verify API key"""
    api_key_record = db.query(APIKey).filter(
        APIKey.is_active == True
    ).all()
    
    for record in api_key_record:
        if verify_password(x_api_key, record.key_hash):
            # Update last used
            record.last_used = datetime.utcnow()
            db.commit()
            
            # Get user
            user = db.query(User).filter(User.id == record.user_id).first()
            if user and user.is_active:
                return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key"
    )