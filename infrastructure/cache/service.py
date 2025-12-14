"""
Cache service for the AI-driven learning platform.
Implements caching mechanisms for performance optimization.
"""

from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import json
import hashlib


class CacheService:
    def __init__(self):
        self.cache = {}
        self.expiration_times = {}
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """
        Set a value in cache with TTL.
        """
        try:
            # Serialize the value to handle complex objects
            serialized_value = json.dumps(value, default=str)
            self.cache[key] = serialized_value
            self.expiration_times[key] = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            return True
        except Exception:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache, return None if not found or expired.
        """
        # Check if key exists and is not expired
        if key in self.cache:
            if datetime.utcnow() < self.expiration_times[key]:
                try:
                    return json.loads(self.cache[key])
                except json.JSONDecodeError:
                    return None
            else:
                # Clean up expired entry
                self.delete(key)
        
        return None
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        """
        if key in self.cache:
            del self.cache[key]
            if key in self.expiration_times:
                del self.expiration_times[key]
            return True
        return False
    
    def clear(self) -> bool:
        """
        Clear all cache entries.
        """
        self.cache.clear()
        self.expiration_times.clear()
        return True
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache and is not expired.
        """
        if key in self.cache:
            if datetime.utcnow() < self.expiration_times[key]:
                return True
            else:
                self.delete(key)  # Clean up expired entry
        
        return False
    
    def keys(self) -> list:
        """
        Get all cache keys that are not expired.
        """
        current_time = datetime.utcnow()
        valid_keys = []
        
        for key, expiration_time in self.expiration_times.items():
            if current_time < expiration_time:
                valid_keys.append(key)
            else:
                # Clean up expired entry
                self.delete(key)
        
        return valid_keys
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for a key in seconds.
        """
        if key in self.cache:
            if datetime.utcnow() < self.expiration_times[key]:
                ttl = (self.expiration_times[key] - datetime.utcnow()).total_seconds()
                return int(ttl)
            else:
                self.delete(key)  # Clean up expired entry
        
        return None
    
    def create_key(self, *args, **kwargs) -> str:
        """
        Create a cache key from arguments.
        """
        key_str = f"{'_'.join(map(str, args))}_{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.sha256(key_str.encode()).hexdigest()


class CacheDecorator:
    """
    Decorator for caching function results.
    """
    def __init__(self, cache_service: CacheService, ttl_seconds: int = 3600, 
                 key_prefix: str = "func_cache"):
        self.cache_service = cache_service
        self.ttl_seconds = ttl_seconds
        self.key_prefix = key_prefix
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{self.key_prefix}:{func.__name__}:{hash(str(args))}:{hash(str(kwargs))}"
            
            # Try to get result from cache
            cached_result = self.cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            self.cache_service.set(cache_key, result, self.ttl_seconds)
            
            return result
        return wrapper