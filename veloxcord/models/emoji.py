from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from .base import DiscordModel
from ..utils import MISSING

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from .user import User
    from .role import Role


class Emoji(DiscordModel):
    __slots__ = (
        "id",
        "_http",
        "guild_id",
        "name",
        "roles",
        "user",
        "require_colons",
        "managed",
        "animated",
        "available",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        guild_id: int,
        name: str,
        roles: list[int],
        user: Optional["User"],
        require_colons: bool,
        managed: bool,
        animated: bool,
        available: bool,
    ) -> None:
        super().__init__(id, http)
        self.guild_id = guild_id
        self.name = name
        self.roles = roles
        self.user = user
        self.require_colons = require_colons
        self.managed = managed
        self.animated = animated
        self.available = available

    def __repr__(self) -> str:
        return f"<Emoji id={self.id} name={self.name!r} animated={self.animated}>"

    def __str__(self) -> str:
        if self.animated:
            return f"<a:{self.name}:{self.id}>"
        return f"<:{self.name}:{self.id}>"

    @property
    def url(self) -> str:
        ext = "gif" if self.animated else "png"
        return f"https://cdn.discordapp.com/emojis/{self.id}.{ext}"

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient", guild_id: int = 0) -> "Emoji":
        from .user import User
        user_data = data.get("user")
        return cls(
            id=int(data["id"]) if data.get("id") else 0,
            http=http,
            guild_id=guild_id,
            name=data.get("name", ""),
            roles=[int(r) for r in data.get("roles", [])],
            user=User._from_data(user_data, http) if user_data else None,
            require_colons=data.get("require_colons", False),
            managed=data.get("managed", False),
            animated=data.get("animated", False),
            available=data.get("available", True),
        )

    async def edit(
        self,
        *,
        name: str = MISSING,
        roles: Optional[list[int]] = MISSING,
        reason: Optional[str] = None,
    ) -> "Emoji":
        payload: dict[str, Any] = {}
        if name is not MISSING:
            payload["name"] = name
        if roles is not MISSING:
            payload["roles"] = [str(r) for r in (roles or [])]
        data = await self._http.edit_guild_emoji(self.guild_id, self.id, payload, reason=reason)
        return Emoji._from_data(data, self._http, self.guild_id)

    async def delete(self, *, reason: Optional[str] = None) -> None:
        await self._http.delete_guild_emoji(self.guild_id, self.id, reason=reason)


class PartialEmoji:
    __slots__ = ("id", "name", "animated")

    def __init__(
        self,
        id: Optional[int],
        name: Optional[str],
        animated: bool = False,
    ) -> None:
        self.id = id
        self.name = name
        self.animated = animated

    def __repr__(self) -> str:
        return f"<PartialEmoji id={self.id} name={self.name!r}>"

    def __str__(self) -> str:
        if self.id is None:
            return self.name or ""
        if self.animated:
            return f"<a:{self.name}:{self.id}>"
        return f"<:{self.name}:{self.id}>"

    @property
    def is_unicode(self) -> bool:
        return self.id is None

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "PartialEmoji":
        return cls(
            id=int(data["id"]) if data.get("id") else None,
            name=data.get("name"),
            animated=data.get("animated", False),
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.id is not None:
            payload["id"] = str(self.id)
        if self.name is not None:
            payload["name"] = self.name
        if self.animated:
            payload["animated"] = self.animated
        return payload
