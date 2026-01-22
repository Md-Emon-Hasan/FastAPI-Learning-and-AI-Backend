import sqlite3
import json
import time
from typing import Optional, Any
from contextlib import contextmanager
from app.core.config import get_settings

settings = get_settings()

class CacheManager:
    """
    SQLite based cache - Redis এর alternative
    Use cases:
    - Rate limiting
    - Session storage  
    - Response caching
    - Temporary data with TTL
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.CACHE_DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Cache table তৈরি করবে"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expire_at REAL,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            # Expired entries দ্রুত খুঁজে পাওয়ার জন্য index
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expire 
                ON cache(expire_at)
            """)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Connection manager - automatic close করবে"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def set(self, key: str, value: Any, ttl: int = None):
        """
        Cache এ data store করবে
        Args:
            key: Cache key
            value: Any JSON serializable data
            ttl: Time to live in seconds (None = no expiry)
        """
        expire_at = time.time() + ttl if ttl else None
        value_str = json.dumps(value)
        
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, expire_at) VALUES (?, ?, ?)",
                (key, value_str, expire_at)
            )
            conn.commit()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Cache থেকে data retrieve করবে
        Expired data automatically None return করবে
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value, expire_at FROM cache WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            value_str, expire_at = row
            
            # Check if expired
            if expire_at and time.time() > expire_at:
                self.delete(key)
                return None
            
            return json.loads(value_str)
    
    def delete(self, key: str):
        """Cache থেকে delete করবে"""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()
    
    def clear_expired(self):
        """
        Expired entries cleanup করবে
        Background task এ periodically run করা যায়
        """
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM cache WHERE expire_at IS NOT NULL AND expire_at < ?",
                (time.time(),)
            )
            conn.commit()
    
    def increment(self, key: str, amount: int = 1, ttl: int = None) -> int:
        """
        Counter increment করবে (rate limiting এর জন্য)
        Returns: New value
        """
        current = self.get(key) or 0
        new_value = current + amount
        self.set(key, new_value, ttl)
        return new_value
    
    def exists(self, key: str) -> bool:
        """Check if key exists এবং expired না"""
        return self.get(key) is not None

# Singleton instance
cache = CacheManager()