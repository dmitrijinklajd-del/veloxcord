from __future__ import annotations
import asyncio
from typing import Any, Callable, Coroutine, Optional

from .cooldown import Cooldown, BucketType
from ..errors import CommandOnCooldown, CheckFailure, MissingPermissions, BotMissingPermissions


class BaseCommand:
    __slots__ = (
        "name",
        "callback",
        "description",
        "aliases",
        "checks",
        "cooldown",
        "guild_ids",
        "required_permissions",
        "required_bot_permissions",
        "parent",
        "cog",
    )

    def __init__(
        self,
        name: str,
        callback: Callable[..., Coroutine[Any, Any, None]],
        *,
        description: str = "",
        aliases: Optional[list[str]] = None,
        checks: Optional[list[Callable[..., bool]]] = None,
        cooldown: Optional[Cooldown] = None,
        guild_ids: Optional[list[int]] = None,
        required_permissions: Optional[list[str]] = None,
        required_bot_permissions: Optional[list[str]] = None,
    ) -> None:
        self.name = name
        self.callback = callback
        self.description = description
        self.aliases = aliases or []
        self.checks = checks or []
        self.cooldown = cooldown
        self.guild_ids = guild_ids or []
        self.required_permissions = required_permissions or []
        self.required_bot_permissions = required_bot_permissions or []
        self.parent: Optional[Any] = None
        self.cog: Optional[Any] = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BaseCommand):
            return self.name == other.name
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.name)

    def add_check(self, check: Callable[..., bool]) -> None:
        self.checks.append(check)

    def remove_check(self, check: Callable[..., bool]) -> None:
        try:
            self.checks.remove(check)
        except ValueError:
            pass

    async def _run_checks(self, ctx: Any) -> None:
        for check in self.checks:
            result = check(ctx)
            if asyncio.iscoroutine(result):
                result = await result
            if not result:
                raise CheckFailure(f"Check {check.__name__!r} failed for {self.name!r}")

    async def _run_cooldown(self, ctx: Any) -> None:
        if self.cooldown is None:
            return
        retry_after = self.cooldown.acquire(ctx)
        if retry_after is not None:
            raise CommandOnCooldown(retry_after)

    async def invoke(self, ctx: Any, *args: Any, **kwargs: Any) -> None:
        await self._run_checks(ctx)
        await self._run_cooldown(ctx)
        if self.cog is not None:
            await self.callback(self.cog, ctx, *args, **kwargs)
        else:
            await self.callback(ctx, *args, **kwargs)
