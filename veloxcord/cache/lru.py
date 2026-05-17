from __future__ import annotations
import time
from collections import OrderedDict
from typing import Generic, Iterator, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class LRUCache(Generic[K, V]):
    __slots__ = ("_cache", "_max_size", "_ttl", "_timestamps")

    def __init__(self, max_size: int = 1024, ttl: Optional[float] = None) -> None:
        self._cache: OrderedDict[K, V] = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl
        self._timestamps: dict[K, float] = {}

    def __repr__(self) -> str:
        return f"LRUCache(size={len(self._cache)}, max_size={self._max_size}, ttl={self._ttl})"

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, key: K) -> bool:
        if key not in self._cache:
            return False
        if self._is_expired(key):
            self._evict(key)
            return False
        return True

    def __iter__(self) -> Iterator[K]:
        return iter(list(self._cache.keys()))

    def _is_expired(self, key: K) -> bool:
        if self._ttl is None:
            return False
        ts = self._timestamps.get(key)
        if ts is None:
            return False
        return time.monotonic() - ts > self._ttl

    def _evict(self, key: K) -> None:
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)

    def _evict_expired(self) -> None:
        if self._ttl is None:
            return
        now = time.monotonic()
        to_delete = [k for k, ts in self._timestamps.items() if now - ts > self._ttl]
        for key in to_delete:
            self._evict(key)

    def get(self, key: K) -> Optional[V]:
        if key not in self._cache:
            return None
        if self._is_expired(key):
            self._evict(key)
            return None
        self._cache.move_to_end(key)
        return self._cache[key]

    def set(self, key: K, value: V) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key] = value
            self._timestamps[key] = time.monotonic()
            return
        self._evict_expired()
        if len(self._cache) >= self._max_size:
            oldest = next(iter(self._cache))
            self._evict(oldest)
        self._cache[key] = value
        self._timestamps[key] = time.monotonic()

    def delete(self, key: K) -> bool:
        if key in self._cache:
            self._evict(key)
            return True
        return False

    def clear(self) -> None:
        self._cache.clear()
        self._timestamps.clear()

    def values(self) -> list[V]:
        self._evict_expired()
        return list(self._cache.values())

    def keys(self) -> list[K]:
        self._evict_expired()
        return list(self._cache.keys())

    def items(self) -> list[tuple[K, V]]:
        self._evict_expired()
        return list(self._cache.items())

    def pop(self, key: K) -> Optional[V]:
        value = self.get(key)
        if value is not None:
            self._evict(key)
        return value

    def get_or_set(self, key: K, default_factory: Any) -> V:
        value = self.get(key)
        if value is None:
            value = default_factory()
            self.set(key, value)
        return value


from typing import Any
