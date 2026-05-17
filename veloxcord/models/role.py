from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from .base import DiscordModel
from ..flags import Permissions
from ..utils import MISSING

if TYPE_CHECKING:
    from ..http.client import HTTPClient


class RoleTags:
    __slots__ = (
        "bot_id",
        "integration_id",
        "premium_subscriber",
        "subscription_listing_id",
        "available_for_purchase",
        "guild_connections",
    )

    def __init__(
        self,
        bot_id: Optional[int],
        integration_id: Optional[int],
        premium_subscriber: bool,
        subscription_listing_id: Optional[int],
        available_for_purchase: bool,
        guild_connections: bool,
    ) -> None:
        self.bot_id = bot_id
        self.integration_id = integration_id
        self.premium_subscriber = premium_subscriber
        self.subscription_listing_id = subscription_listing_id
        self.available_for_purchase = available_for_purchase
        self.guild_connections = guild_connections

    def __repr__(self) -> str:
        return f"<RoleTags bot_id={self.bot_id} integration_id={self.integration_id}>"

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "RoleTags":
        return cls(
            bot_id=int(data["bot_id"]) if "bot_id" in data else None,
            integration_id=int(data["integration_id"]) if "integration_id" in data else None,
            premium_subscriber="premium_subscriber" in data,
            subscription_listing_id=int(data["subscription_listing_id"]) if "subscription_listing_id" in data else None,
            available_for_purchase="available_for_purchase" in data,
            guild_connections="guild_connections" in data,
        )


class Role(DiscordModel):
    __slots__ = (
        "id",
        "_http",
        "guild_id",
        "name",
        "color",
        "hoist",
        "icon",
        "unicode_emoji",
        "position",
        "permissions",
        "managed",
        "mentionable",
        "tags",
        "flags",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        guild_id: int,
        name: str,
        color: int,
        hoist: bool,
        icon: Optional[str],
        unicode_emoji: Optional[str],
        position: int,
        permissions: Permissions,
        managed: bool,
        mentionable: bool,
        tags: Optional[RoleTags],
        flags: int,
    ) -> None:
        super().__init__(id, http)
        self.guild_id = guild_id
        self.name = name
        self.color = color
        self.hoist = hoist
        self.icon = icon
        self.unicode_emoji = unicode_emoji
        self.position = position
        self.permissions = permissions
        self.managed = managed
        self.mentionable = mentionable
        self.tags = tags
        self.flags = flags

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.name!r} position={self.position}>"

    @property
    def mention(self) -> str:
        return f"<@&{self.id}>"

    @property
    def color_hex(self) -> str:
        return f"#{self.color:06X}"

    @property
    def icon_url(self) -> Optional[str]:
        if self.icon is None:
            return None
        return f"https://cdn.discordapp.com/role-icons/{self.id}/{self.icon}.png"

    @property
    def is_default(self) -> bool:
        return self.id == self.guild_id

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient", guild_id: int = 0) -> "Role":
        tags_data = data.get("tags")
        return cls(
            id=int(data["id"]),
            http=http,
            guild_id=guild_id,
            name=data["name"],
            color=data.get("color", 0),
            hoist=data.get("hoist", False),
            icon=data.get("icon"),
            unicode_emoji=data.get("unicode_emoji"),
            position=data.get("position", 0),
            permissions=Permissions(int(data.get("permissions", 0))),
            managed=data.get("managed", False),
            mentionable=data.get("mentionable", False),
            tags=RoleTags._from_data(tags_data) if tags_data else None,
            flags=data.get("flags", 0),
        )

    async def edit(
        self,
        *,
        name: str = MISSING,
        permissions: Permissions = MISSING,
        color: int = MISSING,
        hoist: bool = MISSING,
        mentionable: bool = MISSING,
        icon: Optional[str] = MISSING,
        unicode_emoji: Optional[str] = MISSING,
        reason: Optional[str] = None,
    ) -> "Role":
        payload: dict[str, Any] = {}
        if name is not MISSING:
            payload["name"] = name
        if permissions is not MISSING:
            payload["permissions"] = str(permissions.value)
        if color is not MISSING:
            payload["color"] = color
        if hoist is not MISSING:
            payload["hoist"] = hoist
        if mentionable is not MISSING:
            payload["mentionable"] = mentionable
        if icon is not MISSING:
            payload["icon"] = icon
        if unicode_emoji is not MISSING:
            payload["unicode_emoji"] = unicode_emoji
        data = await self._http.edit_guild_role(self.guild_id, self.id, payload, reason=reason)
        return Role._from_data(data, self._http, self.guild_id)

    async def delete(self, *, reason: Optional[str] = None) -> None:
        await self._http.delete_guild_role(self.guild_id, self.id, reason=reason)
