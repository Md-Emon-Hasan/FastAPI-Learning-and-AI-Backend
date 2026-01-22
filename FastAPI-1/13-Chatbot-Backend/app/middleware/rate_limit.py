from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.exceptions import RateLimitException
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

class RateLimiter:
    def __init__(self, db_path: str = "./rate_limit.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize rate limit database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                key TEXT PRIMARY KEY,
                count INTEGER NOT NULL,
                reset_at TIMESTAMP NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_reset_at 
            ON rate_limits(reset_at)
        """)
        
        conn.commit()
        conn.close()
    
    def check_rate_limit(self, key: str, limit: int = 100, window: int = 60) -> tuple[bool, int]:
        """
        Check if rate limit exceeded
        Returns: (is_allowed, remaining_requests)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Cleanup expired entries
        cursor.execute("DELETE FROM rate_limits WHERE reset_at < ?", (datetime.utcnow(),))
        conn.commit()
        
        # Get current count
        cursor.execute("SELECT count, reset_at FROM rate_limits WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        if result:
            count, reset_at = result
            reset_at = datetime.fromisoformat(reset_at)
            
            if datetime.utcnow() < reset_at:
                # Within window
                if count >= limit:
                    conn.close()
                    return False, 0
                
                # Increment count
                cursor.execute(
                    "UPDATE rate_limits SET count = count + 1 WHERE key = ?",
                    (key,)
                )
                conn.commit()
                remaining = limit - (count + 1)
                conn.close()
                return True, remaining
        
        # New window
        reset_at = datetime.utcnow() + timedelta(seconds=window)
        cursor.execute(
            """
            INSERT OR REPLACE INTO rate_limits (key, count, reset_at)
            VALUES (?, 1, ?)
            """,
            (key, reset_at)
        )
        conn.commit()
        conn.close()
        
        return True, limit - 1

rate_limiter = RateLimiter()

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get client IP or user ID
        client_id = request.client.host
        if hasattr(request.state, "user_id"):
            client_id = f"user_{request.state.user_id}"
        
        # Rate limit key
        key = f"rate_limit:{client_id}:{request.url.path}"
        
        # Check rate limit (100 requests per minute)
        is_allowed, remaining = rate_limiter.check_rate_limit(key, limit=100, window=60)
        
        if not is_allowed:
            raise RateLimitException()
        
        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response