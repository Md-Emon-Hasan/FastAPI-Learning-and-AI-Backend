import sqlite3
import json
from typing import Optional, Any
from functools import wraps
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import threading

class CacheService:
    def __init__(self, db_path: str = "./cache.db", default_ttl: int = 3600):
        self.db_path = db_path
        self.default_ttl = default_ttl
        self.local = threading.local()
        self._init_db()
    
    def _get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self.local.conn
    
    def _init_db(self):
        """Initialize cache database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        
        # Create index on expires_at
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at 
            ON cache(expires_at)
        """)
        
        conn.commit()
        conn.close()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Delete expired entries first
        cursor.execute(
            "DELETE FROM cache WHERE expires_at < ?",
            (datetime.utcnow(),)
        )
        conn.commit()
        
        # Get value
        cursor.execute(
            "SELECT value FROM cache WHERE key = ? AND expires_at > ?",
            (key, datetime.utcnow())
        )
        result = cursor.fetchone()
        
        if result:
            return json.loads(result[0])
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set cached value with TTL"""
        ttl = ttl or self.default_ttl
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT OR REPLACE INTO cache (key, value, expires_at)
            VALUES (?, ?, ?)
            """,
            (key, json.dumps(value, default=str), expires_at)
        )
        conn.commit()
    
    def delete(self, key: str):
        """Delete cached value"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
        conn.commit()
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern (LIKE query)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache WHERE key LIKE ?", (f"%{pattern}%",))
        conn.commit()
    
    def cleanup_expired(self):
        """Cleanup expired cache entries"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache WHERE expires_at < ?", (datetime.utcnow(),))
        conn.commit()

cache_service = CacheService()

# Decorator for caching
def cache_response(ttl: int = 3600, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            
            cache_key = hashlib.md5(
                ":".join(key_parts).encode()
            ).hexdigest()
            
            # Try cache
            cached = cache_service.get(cache_key)
            if cached is not None:
                return cached
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Session storage using SQLite
class SessionStore:
    def __init__(self, db_path: str = "./sessions.db"):
        self.db_path = db_path
        self.local = threading.local()
        self._init_db()
    
    def _get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self.local.conn
    
    def _init_db(self):
        """Initialize session database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_expires 
            ON sessions(expires_at)
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, user_id: int, data: dict, ttl: int = 3600):
        """Create user session"""
        session_id = hashlib.md5(f"{user_id}_{datetime.utcnow()}".encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT OR REPLACE INTO sessions (session_id, user_id, data, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, user_id, json.dumps(data), expires_at)
        )
        conn.commit()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Cleanup expired first
        cursor.execute("DELETE FROM sessions WHERE expires_at < ?", (datetime.utcnow(),))
        conn.commit()
        
        # Get session
        cursor.execute(
            "SELECT data FROM sessions WHERE session_id = ? AND expires_at > ?",
            (session_id, datetime.utcnow())
        )
        result = cursor.fetchone()
        
        return json.loads(result[0]) if result else None
    
    def delete_session(self, session_id: str):
        """Delete session"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()

session_store = SessionStore()