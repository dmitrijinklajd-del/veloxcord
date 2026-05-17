from __future__ import annotations
import asyncio
import datetime
import re
from typing import Any, Callable, Coroutine, Optional, TypeVar

T = TypeVar("T")

DISCORD_EPOCH = 1420070400000


def snowflake_time(snowflake_id: int) -> datetime.datetime:
    timestamp_ms = (snowflake_id >> 22) + DISCORD_EPOCH
    return datetime.datetime.fromtimestamp(timestamp_ms / 1000, tz=datetime.timezone.utc)


def time_snowflake(dt: datetime.datetime) -> int:
    timestamp_ms = int(dt.timestamp() * 1000) - DISCORD_EPOCH
    return timestamp_ms << 22


def parse_timestamp(ts: Optional[str]) -> Optional[datetime.datetime]:
    if ts is None:
        return None
    return datetime.datetime.fromisoformat(ts)


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)


def compute_timedelta(dt: datetime.datetime) -> float:
    now = utcnow()
    return max((dt - now).total_seconds(), 0)


def find(predicate: Callable[[T], bool], iterable: list[T]) -> Optional[T]:
    for item in iterable:
        if predicate(item):
            return item
    return None


def get(iterable: list[T], **attrs: Any) -> Optional[T]:
    for item in iterable:
        if all(getattr(item, k, None) == v for k, v in attrs.items()):
            return item
    return None


def _maybe_coroutine(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    result = func(*args, **kwargs)
    if asyncio.iscoroutine(result):
        return result
    return result


def chunk_list(lst: list[T], size: int) -> list[list[T]]:
    return [lst[i : i + size] for i in range(0, len(lst), size)]


MENTION_RE = re.compile(r"<@!?(\d+)>|<#(\d+)>|<@&(\d+)>")


def parse_mentions(content: str) -> dict[str, list[int]]:
    users: list[int] = []
    channels: list[int] = []
    roles: list[int] = []
    for match in MENTION_RE.finditer(content):
        if match.group(1):
            users.append(int(match.group(1)))
        elif match.group(2):
            channels.append(int(match.group(2)))
        elif match.group(3):
            roles.append(int(match.group(3)))
    return {"users": users, "channels": channels, "roles": roles}


def build_query_string(params: dict[str, Any]) -> str:
    parts = []
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            parts.append(f"{key}={'true' if value else 'false'}")
        else:
            parts.append(f"{key}={value}")
    return "?" + "&".join(parts) if parts else ""


def color_to_int(color: Any) -> int:
    if isinstance(color, int):
        return color
    if isinstance(color, str):
        return int(color.lstrip("#"), 16)
    return 0


def int_to_color_hex(value: int) -> str:
    return f"#{value:06X}"


def missing_kwarg_sentinel() -> Any:
    class _MissingType:
        def __bool__(self) -> bool:
            return False
        def __repr__(self) -> str:
            return "MISSING"
    return _MissingType()


MISSING: Any = missing_kwarg_sentinel()


def resolve_invite(invite: str) -> str:
    if invite.startswith(("https://discord.gg/", "https://discord.com/invite/")):
        return invite.split("/")[-1]
    return invite


def escape_markdown(text: str) -> str:
    markdown_chars = r"\*_`~|>"
    return re.sub(f"([{re.escape(markdown_chars)}])", r"\\\1", text)


def format_dt(dt: datetime.datetime, style: str = "f") -> str:
    timestamp = int(dt.timestamp())
    return f"<t:{timestamp}:{style}>"


async def sleep_until(dt: datetime.datetime) -> None:
    delta = compute_timedelta(dt)
    await asyncio.sleep(delta)


def to_json(obj: Any) -> str:
    import json
    return json.dumps(obj, separators=(",", ":"))


def from_json(data: str) -> Any:
    import json
    return json.loads(data)
