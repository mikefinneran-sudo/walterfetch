"""
Response Caching
Multi-tier caching strategy with TTL support
"""

import asyncio
import time
import json
import hashlib
import logging
from typing import Optional, Any, Dict
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Single cache entry with metadata"""
    key: str
    value: Any
    created_at: float
    ttl: int
    hits: int = 0
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl <= 0:
            return False  # Never expires
        return time.time() - self.created_at > self.ttl

    def touch(self):
        """Update hit count"""
        self.hits += 1


class LRUCache:
    """
    LRU (Least Recently Used) cache with TTL support

    Features:
    - Automatic eviction of least recently used items
    - TTL (Time To Live) for cache entries
    - Memory-efficient with size limits
    - Thread-safe operations
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize LRU cache

        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds (0 = never expire)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

        logger.info(f"LRUCache initialized: max_size={max_size}, ttl={default_ttl}s")

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            if key not in self._cache:
                self._misses += 1
                logger.debug(f"Cache miss: {key}")
                return None

            entry = self._cache[key]

            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache expired: {key}")
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            self._hits += 1

            logger.debug(f"Cache hit: {key} (hits={entry.hits})")
            return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds (None = use default)
        """
        async with self._lock:
            ttl = ttl if ttl is not None else self.default_ttl

            # Calculate size
            try:
                size_bytes = len(json.dumps(value))
            except:
                size_bytes = 0

            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                ttl=ttl,
                size_bytes=size_bytes
            )

            # If key exists, update it
            if key in self._cache:
                self._cache[key] = entry
                self._cache.move_to_end(key)
            else:
                # Add new entry
                self._cache[key] = entry

                # Evict if over capacity
                while len(self._cache) > self.max_size:
                    evicted_key, evicted_entry = self._cache.popitem(last=False)
                    logger.debug(f"Cache evicted (LRU): {evicted_key}")

            logger.debug(f"Cache set: {key} (ttl={ttl}s, size={size_bytes}B)")

    async def delete(self, key: str) -> bool:
        """
        Delete entry from cache

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache deleted: {key}")
                return True
            return False

    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info("Cache cleared")

    async def cleanup_expired(self):
        """Remove all expired entries"""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired entries")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        total_size = sum(entry.size_bytes for entry in self._cache.values())

        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate,
            'total_size_bytes': total_size,
            'utilization': len(self._cache) / self.max_size
        }


class ResponseCache(LRUCache):
    """
    Specialized cache for HTTP responses

    Automatically generates cache keys from URLs and handles
    response-specific caching logic.
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        super().__init__(max_size, default_ttl)

    def _make_key(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict] = None,
        body: Optional[str] = None
    ) -> str:
        """
        Generate cache key from request parameters

        Args:
            url: Request URL
            method: HTTP method
            headers: Request headers (only some are included)
            body: Request body

        Returns:
            Cache key string
        """
        # Include specific headers that affect response
        cache_headers = {}
        if headers:
            for key in ['Accept', 'Accept-Language', 'User-Agent']:
                if key in headers:
                    cache_headers[key] = headers[key]

        key_components = {
            'url': url,
            'method': method,
            'headers': cache_headers,
            'body': body
        }

        key_string = json.dumps(key_components, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]

        return f"response:{method}:{key_hash}"

    async def get_response(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict] = None,
        body: Optional[str] = None
    ) -> Optional[Any]:
        """Get cached response"""
        key = self._make_key(url, method, headers, body)
        return await self.get(key)

    async def set_response(
        self,
        url: str,
        response: Any,
        method: str = 'GET',
        headers: Optional[Dict] = None,
        body: Optional[str] = None,
        ttl: Optional[int] = None
    ):
        """Cache response"""
        key = self._make_key(url, method, headers, body)
        await self.set(key, response, ttl)


class TieredCache:
    """
    Multi-tier caching strategy

    Layers:
    1. Memory (L1): Fast, small capacity
    2. Redis (L2): Medium speed, larger capacity
    3. Database (L3): Slow, unlimited capacity

    Data flows from L3 -> L2 -> L1 on read,
    and L1 -> L2 -> L3 on write.
    """

    def __init__(
        self,
        l1_cache: Optional[LRUCache] = None,
        l2_cache: Optional[Any] = None,  # Redis client
        l3_cache: Optional[Any] = None   # Database client
    ):
        """
        Initialize tiered cache

        Args:
            l1_cache: L1 (memory) cache
            l2_cache: L2 (Redis) cache
            l3_cache: L3 (database) cache
        """
        self.l1 = l1_cache or LRUCache(max_size=100, default_ttl=300)
        self.l2 = l2_cache
        self.l3 = l3_cache

        logger.info("TieredCache initialized")

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (checks all tiers)

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        # Check L1 (memory)
        value = await self.l1.get(key)
        if value is not None:
            logger.debug(f"L1 cache hit: {key}")
            return value

        # Check L2 (Redis)
        if self.l2:
            value = await self._get_from_l2(key)
            if value is not None:
                logger.debug(f"L2 cache hit: {key}")
                # Promote to L1
                await self.l1.set(key, value)
                return value

        # Check L3 (Database)
        if self.l3:
            value = await self._get_from_l3(key)
            if value is not None:
                logger.debug(f"L3 cache hit: {key}")
                # Promote to L2 and L1
                if self.l2:
                    await self._set_to_l2(key, value)
                await self.l1.set(key, value)
                return value

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in all cache tiers

        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds
        """
        # Set in all tiers
        await self.l1.set(key, value, ttl)

        if self.l2:
            await self._set_to_l2(key, value, ttl)

        if self.l3:
            await self._set_to_l3(key, value, ttl)

    async def _get_from_l2(self, key: str) -> Optional[Any]:
        """Get from Redis cache (implement based on Redis client)"""
        # Placeholder - implement with actual Redis client
        return None

    async def _set_to_l2(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set to Redis cache (implement based on Redis client)"""
        # Placeholder - implement with actual Redis client
        pass

    async def _get_from_l3(self, key: str) -> Optional[Any]:
        """Get from database cache (implement based on DB client)"""
        # Placeholder - implement with actual database client
        return None

    async def _set_to_l3(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set to database cache (implement based on DB client)"""
        # Placeholder - implement with actual database client
        pass
