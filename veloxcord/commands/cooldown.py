from __future__ import annotations
import time
from enum import Enum
from typing import Any, Optional


class BucketType(Enum):
    DEFAULT = "default"
    USER = "user"
    GUILD = "guild"
    CHANNEL = "channel"
    MEMBER = "member"


class CooldownBucket:
    __slots__ = ("rate", "per", "_tokens", "_window")

    def __init__(self, rate: int, per: float) -> None:
        self.rate = rate
        self.per = per
        self._tokens = rate
        self._window: float = 0.0

    def __repr__(self) -> str:
        return f"<CooldownBucket rate={self.rate} per={self.per} tokens={self._tokens}>"

    def _update_tokens(self) -> None:
        current = time.monotonic()
        if current > self._window + self.per:
            self._tokens = self.rate
            self._window = current

    @property
    def retry_after(self) -> float:
        current = time.monotonic()
        return max(self._window + self.per - current, 0.0)

    def is_rate_limited(self) -> bool:
        self._update_tokens()
        return self._tokens <= 0

    def acquire(self) -> bool:
        self._update_tokens()
        if self._tokens <= 0:
            return False
        self._tokens -= 1
        return True

    def reset(self) -> None:
        self._tokens = self.rate
        self._window = 0.0


class Cooldown:
    __slots__ = ("rate", "per", "type", "_buckets")

    def __init__(self, rate: int, per: float, bucket_type: BucketType = BucketType.USER) -> None:
        self.rate = rate
        self.per = per
        self.type = bucket_type
        self._buckets: dict[str, CooldownBucket] = {}

    def __repr__(self) -> str:
        return f"<Cooldown rate={self.rate} per={self.per} type={self.type}>"

    def _get_bucket_key(self, ctx: Any) -> str:
        match self.type:
            case BucketType.USER:
                author = getattr(ctx, "author", None)
                user = getattr(ctx, "user", None) or getattr(author, "user", author)
                return f"user:{getattr(user, 'id', 0)}"
            case BucketType.GUILD:
                guild_id = getattr(ctx, "guild_id", None) or getattr(getattr(ctx, "guild", None), "id", 0)
                return f"guild:{guild_id}"
            case BucketType.CHANNEL:
                channel_id = getattr(ctx, "channel_id", None) or getattr(getattr(ctx, "channel", None), "id", 0)
                return f"channel:{channel_id}"
            case BucketType.MEMBER:
                author = getattr(ctx, "author", None)
                user = getattr(ctx, "user", None) or getattr(author, "user", author)
                guild_id = getattr(ctx, "guild_id", None) or getattr(getattr(ctx, "guild", None), "id", 0)
                return f"member:{guild_id}:{getattr(user, 'id', 0)}"
            case _:
                return "global"

    def _get_bucket(self, key: str) -> CooldownBucket:
        if key not in self._buckets:
            self._buckets[key] = CooldownBucket(self.rate, self.per)
        return self._buckets[key]

    def acquire(self, ctx: Any) -> Optional[float]:
        key = self._get_bucket_key(ctx)
        bucket = self._get_bucket(key)
        if bucket.is_rate_limited():
            return bucket.retry_after
        bucket.acquire()
        return None

    def reset(self, ctx: Any) -> None:
        key = self._get_bucket_key(ctx)
        bucket = self._buckets.get(key)
        if bucket:
            bucket.reset()

    def reset_all(self) -> None:
        self._buckets.clear()
