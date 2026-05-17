from __future__ import annotations
from typing import Any, Callable, Coroutine, Optional

from .core import BaseCommand
from .cooldown import Cooldown
from ..enums import ApplicationCommandType


class UserCommand(BaseCommand):
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
        "default_member_permissions",
        "dm_permission",
    )

    def __init__(
        self,
        name: str,
        callback: Callable[..., Coroutine[Any, Any, None]],
        *,
        guild_ids: Optional[list[int]] = None,
        default_member_permissions: Optional[int] = None,
        dm_permission: bool = True,
        cooldown: Optional[Cooldown] = None,
        checks: Optional[list[Callable[..., bool]]] = None,
    ) -> None:
        super().__init__(
            name=name,
            callback=callback,
            description="",
            guild_ids=guild_ids,
            cooldown=cooldown,
            checks=checks,
        )
        self.default_member_permissions = default_member_permissions
        self.dm_permission = dm_permission

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "type": ApplicationCommandType.USER.value,
            "dm_permission": self.dm_permission,
        }
        if self.default_member_permissions is not None:
            payload["default_member_permissions"] = str(self.default_member_permissions)
        return payload


class MessageCommand(BaseCommand):
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
        "default_member_permissions",
        "dm_permission",
    )

    def __init__(
        self,
        name: str,
        callback: Callable[..., Coroutine[Any, Any, None]],
        *,
        guild_ids: Optional[list[int]] = None,
        default_member_permissions: Optional[int] = None,
        dm_permission: bool = True,
        cooldown: Optional[Cooldown] = None,
        checks: Optional[list[Callable[..., bool]]] = None,
    ) -> None:
        super().__init__(
            name=name,
            callback=callback,
            description="",
            guild_ids=guild_ids,
            cooldown=cooldown,
            checks=checks,
        )
        self.default_member_permissions = default_member_permissions
        self.dm_permission = dm_permission

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "type": ApplicationCommandType.MESSAGE.value,
            "dm_permission": self.dm_permission,
        }
        if self.default_member_permissions is not None:
            payload["default_member_permissions"] = str(self.default_member_permissions)
        return payload
