from datetime import datetime, timedelta
from typing import Any, Optional, Dict
import threading


class CacheService:
    """Simple in-memory cache service with TTL support."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        with self._lock:
            if key not in self._cache:
                return None
            
            cache_entry = self._cache[key]
            if datetime.now() > cache_entry['expires_at']:
                del self._cache[key]
                return None
            
            return cache_entry['value']
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set value in cache with TTL."""
        with self._lock:
            self._cache[key] = {
                'value': value,
                'expires_at': datetime.now() + timedelta(seconds=ttl_seconds)
            }
    
    def delete(self, key: str):
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self):
        """Remove expired entries from cache."""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, entry in self._cache.items()
                if now > entry['expires_at']
            ]
            for key in expired_keys:
                del self._cache[key]


# Global cache instance
cache = CacheService()