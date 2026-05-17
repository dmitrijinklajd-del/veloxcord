from __future__ import annotations
from typing import Any, Callable, Coroutine, Optional, Union

from .cooldown import Cooldown, BucketType
from .core import BaseCommand
from ..errors import MissingPermissions, BotMissingPermissions, CheckFailure
from ..flags import Permissions


def cooldown(
    rate: int,
    per: float,
    bucket: BucketType = BucketType.USER,
) -> Callable[[Any], Any]:
    def decorator(func_or_command: Any) -> Any:
        cd = Cooldown(rate, per, bucket)
        if isinstance(func_or_command, BaseCommand):
            func_or_command.cooldown = cd
        else:
            func_or_command.__velox_cooldown__ = cd
        return func_or_command
    return decorator


def guild_only() -> Callable[[Any], Any]:
    def check(ctx: Any) -> bool:
        if getattr(ctx, "guild_id", None) is None:
            raise CheckFailure("This command can only be used in a guild")
        return True

    def decorator(func_or_command: Any) -> Any:
        if isinstance(func_or_command, BaseCommand):
            func_or_command.add_check(check)
        else:
            checks = getattr(func_or_command, "__velox_checks__", [])
            checks.append(check)
            func_or_command.__velox_checks__ = checks
        return func_or_command
    return decorator


def dm_only() -> Callable[[Any], Any]:
    def check(ctx: Any) -> bool:
        if getattr(ctx, "guild_id", None) is not None:
            raise CheckFailure("This command can only be used in DMs")
        return True

    def decorator(func_or_command: Any) -> Any:
        if isinstance(func_or_command, BaseCommand):
            func_or_command.add_check(check)
        else:
            checks = getattr(func_or_command, "__velox_checks__", [])
            checks.append(check)
            func_or_command.__velox_checks__ = checks
        return func_or_command
    return decorator


def require_permissions(*permission_names: str) -> Callable[[Any], Any]:
    def check(ctx: Any) -> bool:
        author = getattr(ctx, "author", None)
        if author is None:
            raise CheckFailure("Cannot resolve author permissions")
        member_permissions = getattr(author, "permissions", None)
        if member_permissions is None:
            return True
        missing = []
        for perm_name in permission_names:
            if not getattr(member_permissions, perm_name, False):
                missing.append(perm_name)
        if missing:
            raise MissingPermissions(missing)
        return True

    def decorator(func_or_command: Any) -> Any:
        if isinstance(func_or_command, BaseCommand):
            func_or_command.add_check(check)
            func_or_command.required_permissions = list(permission_names)
        else:
            checks = getattr(func_or_command, "__velox_checks__", [])
            checks.append(check)
            func_or_command.__velox_checks__ = checks
            func_or_command.__velox_required_permissions__ = list(permission_names)
        return func_or_command
    return decorator


def require_bot_permissions(*permission_names: str) -> Callable[[Any], Any]:
    def check(ctx: Any) -> bool:
        bot = getattr(ctx, "bot", None)
        if bot is None:
            return True
        guild_id = getattr(ctx, "guild_id", None)
        if guild_id is None:
            return True
        return True

    def decorator(func_or_command: Any) -> Any:
        if isinstance(func_or_command, BaseCommand):
            func_or_command.add_check(check)
            func_or_command.required_bot_permissions = list(permission_names)
        else:
            checks = getattr(func_or_command, "__velox_checks__", [])
            checks.append(check)
            func_or_command.__velox_checks__ = checks
        return func_or_command
    return decorator


def check(predicate: Callable[[Any], Union[bool, Coroutine[Any, Any, bool]]]) -> Callable[[Any], Any]:
    def decorator(func_or_command: Any) -> Any:
        if isinstance(func_or_command, BaseCommand):
            func_or_command.add_check(predicate)
        else:
            checks = getattr(func_or_command, "__velox_checks__", [])
            checks.append(predicate)
            func_or_command.__velox_checks__ = checks
        return func_or_command
    return decorator


def is_owner() -> Callable[[Any], Any]:
    async def check_owner(ctx: Any) -> bool:
        bot = getattr(ctx, "bot", None)
        if bot is None:
            raise CheckFailure("Cannot resolve bot")
        owner_id = getattr(bot, "owner_id", None)
        if owner_id is None:
            return True
        author = getattr(ctx, "author", None)
        user = getattr(author, "user", author)
        user_id = getattr(user, "id", None)
        if user_id != owner_id:
            raise CheckFailure("You must be the bot owner to use this command")
        return True

    return check(check_owner)


def max_concurrency(
    number: int,
    per: BucketType = BucketType.USER,
    *,
    wait: bool = False,
) -> Callable[[Any], Any]:
    import asyncio

    _semaphores: dict[str, asyncio.Semaphore] = {}

    async def acquire(ctx: Any) -> bool:
        key = f"{per.value}:{id(ctx)}"
        if key not in _semaphores:
            _semaphores[key] = asyncio.Semaphore(number)
        sem = _semaphores[key]
        if wait:
            await sem.acquire()
            return True
        acquired = sem._value > 0
        if acquired:
            await sem.acquire()
        return acquired

    def decorator(func_or_command: Any) -> Any:
        return func_or_command
    return decorator
