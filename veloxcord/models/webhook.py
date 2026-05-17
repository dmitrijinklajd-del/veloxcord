from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from .base import DiscordModel
from ..enums import WebhookType

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from .user import User
    from .guild import Guild
    from .channel import TextChannel


class Webhook(DiscordModel):
    __slots__ = (
        "id",
        "_http",
        "type",
        "guild_id",
        "channel_id",
        "user",
        "name",
        "_avatar",
        "token",
        "application_id",
        "source_guild",
        "source_channel",
        "url",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        type: WebhookType,
        guild_id: Optional[int],
        channel_id: Optional[int],
        user: Optional["User"],
        name: Optional[str],
        avatar: Optional[str],
        token: Optional[str],
        application_id: Optional[int],
        source_guild: Optional[Any],
        source_channel: Optional[Any],
        url: Optional[str],
    ) -> None:
        super().__init__(id, http)
        self.type = type
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.user = user
        self.name = name
        self._avatar = avatar
        self.token = token
        self.application_id = application_id
        self.source_guild = source_guild
        self.source_channel = source_channel
        self.url = url

    def __repr__(self) -> str:
        return f"<Webhook id={self.id} name={self.name!r} type={self.type}>"

    @property
    def avatar_url(self) -> Optional[str]:
        if self._avatar is None:
            return None
        return f"https://cdn.discordapp.com/avatars/{self.id}/{self._avatar}.png?size=1024"

    async def send(
        self,
        content: Optional[str] = None,
        *,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
        tts: bool = False,
        embeds: Optional[list[Any]] = None,
        components: Optional[list[Any]] = None,
        thread_id: Optional[int] = None,
        wait: bool = False,
    ) -> Optional[Any]:
        if not self.token:
            raise ValueError("Webhook has no token — cannot send messages")
        from .message import Message
        payload: dict[str, Any] = {}
        if content is not None:
            payload["content"] = content
        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url
        if tts:
            payload["tts"] = tts
        if embeds:
            payload["embeds"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in embeds]
        if components:
            payload["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in components]
        params: dict[str, Any] = {}
        if thread_id:
            params["thread_id"] = thread_id
        if wait:
            params["wait"] = "true"
        data = await self._http.execute_webhook(self.id, self.token, payload, params=params)
        if data and wait:
            return Message._from_data(data, self._http)
        return None

    async def edit(
        self,
        *,
        name: Optional[str] = None,
        channel_id: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> "Webhook":
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if channel_id is not None:
            payload["channel_id"] = str(channel_id)
        data = await self._http.edit_webhook(self.id, payload, token=self.token, reason=reason)
        return Webhook._from_data(data, self._http)

    async def delete(self, *, reason: Optional[str] = None) -> None:
        await self._http.delete_webhook(self.id, token=self.token, reason=reason)

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "Webhook":
        from .user import User
        user_data = data.get("user")
        return cls(
            id=int(data["id"]),
            http=http,
            type=WebhookType(data.get("type", 1)),
            guild_id=int(data["guild_id"]) if data.get("guild_id") else None,
            channel_id=int(data["channel_id"]) if data.get("channel_id") else None,
            user=User._from_data(user_data, http) if user_data else None,
            name=data.get("name"),
            avatar=data.get("avatar"),
            token=data.get("token"),
            application_id=int(data["application_id"]) if data.get("application_id") else None,
            source_guild=data.get("source_guild"),
            source_channel=data.get("source_channel"),
            url=data.get("url"),
        )
