"""Redis caching client"""
import redis
import json
from typing import Optional, Any
from app.config import settings

class RedisClient:
    """Redis client for caching"""

    def __init__(self, url: str):
        self.redis = redis.from_url(url, decode_responses=True)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL (default 1 hour)"""
        try:
            self.redis.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False

    def delete(self, key: str):
        """Delete key from cache"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return self.redis.exists(key) > 0
        except Exception as e:
            print(f"Redis EXISTS error: {e}")
            return False

    def publish(self, channel: str, message: dict):
        """Publish message to channel"""
        try:
            self.redis.publish(channel, json.dumps(message))
            return True
        except Exception as e:
            print(f"Redis PUBLISH error: {e}")
            return False

    def flush_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        try:
            for key in self.redis.scan_iter(match=pattern):
                self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Redis FLUSH_PATTERN error: {e}")
            return False

    def ping(self) -> bool:
        """Check if Redis is alive"""
        try:
            return self.redis.ping()
        except Exception:
            return False

# Global Redis client instance
_redis_client: Optional[RedisClient] = None

def get_redis_client() -> RedisClient:
    """Get or create Redis client instance"""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient(settings.redis_url)
    return _redis_client
