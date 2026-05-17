from __future__ import annotations
import datetime
from typing import TYPE_CHECKING, Any, Optional

from .base import DiscordModel
from ..flags import Permissions
from ..utils import parse_timestamp, MISSING

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from .user import User
    from .guild import Guild
    from .role import Role


class Member(DiscordModel):
    __slots__ = (
        "id",
        "_http",
        "guild_id",
        "user",
        "nick",
        "_avatar",
        "role_ids",
        "joined_at",
        "premium_since",
        "deaf",
        "mute",
        "flags",
        "pending",
        "permissions",
        "communication_disabled_until",
    )

    def __init__(
        self,
        user: "User",
        http: "HTTPClient",
        guild_id: int,
        nick: Optional[str],
        avatar: Optional[str],
        role_ids: list[int],
        joined_at: Optional[datetime.datetime],
        premium_since: Optional[datetime.datetime],
        deaf: bool,
        mute: bool,
        flags: int,
        pending: bool,
        permissions: Optional[Permissions],
        communication_disabled_until: Optional[datetime.datetime],
    ) -> None:
        super().__init__(user.id, http)
        self.user = user
        self.guild_id = guild_id
        self.nick = nick
        self._avatar = avatar
        self.role_ids = role_ids
        self.joined_at = joined_at
        self.premium_since = premium_since
        self.deaf = deaf
        self.mute = mute
        self.flags = flags
        self.pending = pending
        self.permissions = permissions
        self.communication_disabled_until = communication_disabled_until

    def __repr__(self) -> str:
        return f"<Member id={self.id} name={self.display_name!r} guild_id={self.guild_id}>"

    @property
    def display_name(self) -> str:
        return self.nick or self.user.display_name

    @property
    def name(self) -> str:
        return self.user.name

    @property
    def mention(self) -> str:
        return f"<@{self.id}>"

    @property
    def avatar_url(self) -> Optional[str]:
        if self._avatar:
            ext = "gif" if self._avatar.startswith("a_") else "png"
            return f"https://cdn.discordapp.com/guilds/{self.guild_id}/users/{self.id}/avatars/{self._avatar}.{ext}?size=1024"
        return self.user.avatar_url

    @property
    def is_timed_out(self) -> bool:
        if self.communication_disabled_until is None:
            return False
        from ..utils import utcnow
        return self.communication_disabled_until > utcnow()

    @property
    def top_role_id(self) -> Optional[int]:
        if not self.role_ids:
            return None
        return self.role_ids[-1]

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient", guild_id: int = 0) -> "Member":
        from .user import User
        user_data = data.get("user", {})
        user = User._from_data(user_data, http)
        permissions_raw = data.get("permissions")
        return cls(
            user=user,
            http=http,
            guild_id=guild_id,
            nick=data.get("nick"),
            avatar=data.get("avatar"),
            role_ids=[int(r) for r in data.get("roles", [])],
            joined_at=parse_timestamp(data.get("joined_at")),
            premium_since=parse_timestamp(data.get("premium_since")),
            deaf=data.get("deaf", False),
            mute=data.get("mute", False),
            flags=data.get("flags", 0),
            pending=data.get("pending", False),
            permissions=Permissions(int(permissions_raw)) if permissions_raw else None,
            communication_disabled_until=parse_timestamp(data.get("communication_disabled_until")),
        )

    async def ban(
        self,
        *,
        delete_message_seconds: int = 0,
        reason: Optional[str] = None,
    ) -> None:
        await self._http.create_guild_ban(
            self.guild_id, self.id, delete_message_seconds=delete_message_seconds, reason=reason
        )

    async def kick(self, *, reason: Optional[str] = None) -> None:
        await self._http.remove_guild_member(self.guild_id, self.id, reason=reason)

    async def timeout(
        self,
        until: Optional[datetime.datetime],
        *,
        reason: Optional[str] = None,
    ) -> "Member":
        payload: dict[str, Any] = {}
        payload["communication_disabled_until"] = until.isoformat() if until else None
        data = await self._http.edit_guild_member(self.guild_id, self.id, payload, reason=reason)
        return Member._from_data(data, self._http, self.guild_id)

    async def add_role(self, role_id: int, *, reason: Optional[str] = None) -> None:
        await self._http.add_guild_member_role(self.guild_id, self.id, role_id, reason=reason)

    async def remove_role(self, role_id: int, *, reason: Optional[str] = None) -> None:
        await self._http.remove_guild_member_role(self.guild_id, self.id, role_id, reason=reason)

    async def edit(
        self,
        *,
        nick: Optional[str] = MISSING,
        roles: Optional[list[int]] = MISSING,
        mute: bool = MISSING,
        deaf: bool = MISSING,
        channel_id: Optional[int] = MISSING,
        communication_disabled_until: Optional[datetime.datetime] = MISSING,
        flags: int = MISSING,
        reason: Optional[str] = None,
    ) -> "Member":
        payload: dict[str, Any] = {}
        if nick is not MISSING:
            payload["nick"] = nick
        if roles is not MISSING:
            payload["roles"] = [str(r) for r in (roles or [])]
        if mute is not MISSING:
            payload["mute"] = mute
        if deaf is not MISSING:
            payload["deaf"] = deaf
        if channel_id is not MISSING:
            payload["channel_id"] = channel_id
        if communication_disabled_until is not MISSING:
            payload["communication_disabled_until"] = (
                communication_disabled_until.isoformat() if communication_disabled_until else None
            )
        if flags is not MISSING:
            payload["flags"] = flags
        data = await self._http.edit_guild_member(self.guild_id, self.id, payload, reason=reason)
        return Member._from_data(data, self._http, self.guild_id)

    async def send(self, content: Optional[str] = None, **kwargs: Any) -> Any:
        return await self.user.send(content, **kwargs)
