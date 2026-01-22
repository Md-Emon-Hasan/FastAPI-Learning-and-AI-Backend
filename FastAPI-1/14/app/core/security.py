from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()

# Password hashing context - bcrypt algorithm use করবে
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Plain password কে hash করবে
    Database এ কখনো plain password store করবো না
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Login এর সময় password verify করবে
    Returns: True if match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT token তৈরি করবে
    Args:
        data: Token এ যা data রাখতে চাও (user_id, email etc)
        expires_delta: Token কতক্ষণ valid থাকবে
    
    Returns: JWT token string
    
    Example:
        token = create_access_token({"sub": user.email, "user_id": user.id})
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # JWT encode করবে SECRET_KEY দিয়ে
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    JWT token decode করবে এবং validate করবে
    Returns: Token payload if valid, None if invalid/expired
    
    Example:
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("user_id")
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        # Invalid token or expired
        return None

def create_api_key() -> str:
    """
    Random API key generate করবে
    Machine-to-machine authentication এর জন্য
    """
    import secrets
    return f"sk_{secrets.token_urlsafe(32)}"