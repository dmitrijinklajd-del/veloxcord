from __future__ import annotations
import asyncio
import time
from typing import Optional


class RateLimitBucket:
    __slots__ = (
        "key",
        "limit",
        "remaining",
        "reset_at",
        "reset_after",
        "_lock",
    )

    def __init__(self, key: str) -> None:
        self.key = key
        self.limit: int = 1
        self.remaining: int = 1
        self.reset_at: float = 0.0
        self.reset_after: float = 0.0
        self._lock: asyncio.Lock = asyncio.Lock()

    def __repr__(self) -> str:
        return f"<RateLimitBucket key={self.key!r} remaining={self.remaining}/{self.limit}>"

    @property
    def is_rate_limited(self) -> bool:
        if self.remaining > 0:
            return False
        return time.monotonic() < self.reset_at

    @property
    def time_until_reset(self) -> float:
        return max(self.reset_at - time.monotonic(), 0.0)

    def update(
        self,
        limit: Optional[str],
        remaining: Optional[str],
        reset: Optional[str],
        reset_after: Optional[str],
    ) -> None:
        if limit is not None:
            self.limit = int(limit)
        if remaining is not None:
            self.remaining = int(remaining)
        if reset is not None:
            self.reset_at = float(reset)
        if reset_after is not None:
            self.reset_after = float(reset_after)

    async def acquire(self) -> None:
        async with self._lock:
            if self.is_rate_limited:
                wait = self.time_until_reset
                await asyncio.sleep(wait + 0.1)


class GlobalRateLimiter:
    __slots__ = ("_event", "_retry_after")

    def __init__(self) -> None:
        self._event: asyncio.Event = asyncio.Event()
        self._event.set()
        self._retry_after: float = 0.0

    @property
    def is_rate_limited(self) -> bool:
        return not self._event.is_set()

    def lock(self, retry_after: float) -> None:
        self._retry_after = retry_after
        self._event.clear()

    async def wait(self) -> None:
        await self._event.wait()

    async def unlock_after(self, delay: float) -> None:
        await asyncio.sleep(delay)
        self._event.set()


class RateLimitManager:
    __slots__ = ("_buckets", "_route_to_bucket", "_global")

    def __init__(self) -> None:
        self._buckets: dict[str, RateLimitBucket] = {}
        self._route_to_bucket: dict[str, str] = {}
        self._global: GlobalRateLimiter = GlobalRateLimiter()

    def __repr__(self) -> str:
        return f"<RateLimitManager buckets={len(self._buckets)}>"

    def get_bucket(self, route_key: str) -> Optional[RateLimitBucket]:
        bucket_hash = self._route_to_bucket.get(route_key)
        if bucket_hash is None:
            return None
        return self._buckets.get(bucket_hash)

    def update_bucket(
        self,
        route_key: str,
        bucket_hash: Optional[str],
        limit: Optional[str],
        remaining: Optional[str],
        reset: Optional[str],
        reset_after: Optional[str],
    ) -> None:
        if bucket_hash is None:
            return
        self._route_to_bucket[route_key] = bucket_hash
        if bucket_hash not in self._buckets:
            self._buckets[bucket_hash] = RateLimitBucket(bucket_hash)
        self._buckets[bucket_hash].update(limit, remaining, reset, reset_after)

    async def acquire(self, route_key: str) -> None:
        await self._global.wait()
        bucket = self.get_bucket(route_key)
        if bucket is not None:
            await bucket.acquire()

    def trigger_global(self, retry_after: float) -> None:
        import asyncio as _asyncio
        self._global.lock(retry_after)
        _asyncio.ensure_future(self._global.unlock_after(retry_after))

    def is_globally_rate_limited(self) -> bool:
        return self._global.is_rate_limited
