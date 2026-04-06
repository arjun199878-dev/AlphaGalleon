# AlphaGalleon Caching Module
# Provides Redis-based caching for API responses
# Usage: @cache_result(ttl=300) decorator on endpoints

import redis
import json
import functools
import os
from typing import Optional, Any, Callable
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages Redis caching for API responses"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        
        try:
            # Parse Redis URL
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("✓ Redis cache connected")
        except Exception as e:
            logger.warning(f"⚠ Redis cache failed: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL (Time To Live) in seconds"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            self.redis_client.setex(
                key, 
                ttl, 
                json.dumps(value)
            )
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            cursor = 0
            count = 0
            while True:
                cursor, keys = self.redis_client.scan(cursor, match=pattern, count=100)
                if keys:
                    count += self.redis_client.delete(*keys)
                if cursor == 0:
                    break
            return count
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled or not self.redis_client:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "memory_used": info.get("used_memory_human", "?"),
                "connected_clients": info.get("connected_clients", "?"),
                "commands_processed": info.get("total_commands_processed", "?"),
                "evicted_keys": info.get("evicted_keys", 0),
            }
        except Exception as e:
            logger.warning(f"Cache stats error: {e}")
            return {"enabled": False, "error": str(e)}

# Global cache manager instance
cache_manager = CacheManager()

def cache_result(ttl: int = 300, key_prefix: str = "cache"):
    """
    Decorator to cache function results in Redis
    
    Args:
        ttl: Time to live in seconds (default 300 = 5 minutes)
        key_prefix: Prefix for cache key (default "cache")
    
    Usage:
        @cache_result(ttl=600)
        def get_user_data(user_id: str):
            return some_expensive_operation(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached = cache_manager.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache HIT: {cache_key[:50]}...")
                return cached
            
            # Call function and cache result
            logger.debug(f"Cache MISS: {cache_key[:50]}...")
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

def invalidate_cache(pattern: str = "*"):
    """Invalidate cache entries matching pattern"""
    return cache_manager.clear_pattern(pattern)

# Session management using Redis
class SessionManager:
    """Manages user sessions with Redis"""
    
    def __init__(self):
        self.cache = cache_manager
        self.session_ttl = 30 * 24 * 60 * 60  # 30 days
    
    def create_session(self, user_id: str, user_data: dict) -> str:
        """Create session for user"""
        session_key = f"session:{user_id}"
        self.cache.set(session_key, user_data, self.session_ttl)
        return session_key
    
    def get_session(self, user_id: str) -> Optional[dict]:
        """Get user session"""
        session_key = f"session:{user_id}"
        return self.cache.get(session_key)
    
    def delete_session(self, user_id: str) -> bool:
        """Delete user session (logout)"""
        session_key = f"session:{user_id}"
        return self.cache.delete(session_key)
    
    def refresh_session(self, user_id: str) -> bool:
        """Extend session TTL"""
        session = self.get_session(user_id)
        if session:
            return self.create_session(user_id, session) is not None
        return False

session_manager = SessionManager()
