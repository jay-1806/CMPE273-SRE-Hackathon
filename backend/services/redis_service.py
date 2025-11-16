"""
Redis service for caching and session management
"""
import json
from typing import Optional, Any
from backend.core.config import settings

# In-memory fallback cache
_memory_cache = {}

# Redis client (will be initialized if Redis is available)
redis_client = None

if settings.USE_REDIS:
    try:
        import redis
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )
        # Test connection
        redis_client.ping()
        print("✓ Redis connected successfully")
    except Exception as e:
        print(f"⚠ Redis connection failed: {e}. Using in-memory cache.")
        redis_client = None
else:
    print("ℹ Using in-memory cache (Redis disabled)")


class CacheService:
    """Cache service with Redis or in-memory fallback"""

    @staticmethod
    def set(key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a value in cache"""
        try:
            if redis_client:
                # Use Redis
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                redis_client.set(key, value, ex=expire)
            else:
                # Use in-memory cache
                _memory_cache[key] = value
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get a value from cache"""
        try:
            if redis_client:
                # Use Redis
                value = redis_client.get(key)
                if value:
                    try:
                        return json.loads(value)
                    except:
                        return value
                return None
            else:
                # Use in-memory cache
                return _memory_cache.get(key)
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    @staticmethod
    def delete(key: str) -> bool:
        """Delete a key from cache"""
        try:
            if redis_client:
                redis_client.delete(key)
            else:
                if key in _memory_cache:
                    del _memory_cache[key]
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    @staticmethod
    def exists(key: str) -> bool:
        """Check if a key exists in cache"""
        try:
            if redis_client:
                return redis_client.exists(key) > 0
            else:
                return key in _memory_cache
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False

    @staticmethod
    def increment(key: str, amount: int = 1) -> int:
        """Increment a counter"""
        try:
            if redis_client:
                return redis_client.incrby(key, amount)
            else:
                current = _memory_cache.get(key, 0)
                _memory_cache[key] = current + amount
                return _memory_cache[key]
        except Exception as e:
            print(f"Cache increment error: {e}")
            return 0

    @staticmethod
    def get_all_keys(pattern: str = "*") -> list:
        """Get all keys matching a pattern"""
        try:
            if redis_client:
                return [k.decode() if isinstance(k, bytes) else k for k in redis_client.keys(pattern)]
            else:
                import re
                regex = pattern.replace("*", ".*")
                return [k for k in _memory_cache.keys() if re.match(regex, k)]
        except Exception as e:
            print(f"Cache get_all_keys error: {e}")
            return []

    @staticmethod
    def clear_all() -> bool:
        """Clear all cache"""
        try:
            if redis_client:
                redis_client.flushdb()
            else:
                _memory_cache.clear()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False


# Export singleton instance
cache = CacheService()
