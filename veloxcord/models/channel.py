from __future__ import annotations
import datetime
from typing import TYPE_CHECKING, Any, Iterator, Optional

from .base import DiscordModel
from ..enums import ChannelType, VideoQualityMode
from ..utils import parse_timestamp, MISSING

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from .message import Message
    from .embed import Embed
    from .permissions import PermissionOverwrite
    from .user import User
    from .invite import Invite


class _BaseChannel(DiscordModel):
    __slots__ = ("id", "_http", "type", "name")

    def __init__(self, id: int, http: "HTTPClient", type: ChannelType, name: Optional[str]) -> None:
        super().__init__(id, http)
        self.type = type
        self.name = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name!r}>"

    @property
    def mention(self) -> str:
        return f"<#{self.id}>"


class TextChannel(_BaseChannel):
    __slots__ = (
        "id",
        "_http",
        "type",
        "name",
        "guild_id",
        "position",
        "permission_overwrites",
        "topic",
        "nsfw",
        "last_message_id",
        "rate_limit_per_user",
        "parent_id",
        "last_pin_timestamp",
        "default_auto_archive_duration",
        "default_thread_rate_limit_per_user",
        "flags",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        guild_id: int,
        name: str,
        position: int,
        permission_overwrites: list["PermissionOverwrite"],
        topic: Optional[str],
        nsfw: bool,
        last_message_id: Optional[int],
        rate_limit_per_user: int,
        parent_id: Optional[int],
        last_pin_timestamp: Optional[datetime.datetime],
        default_auto_archive_duration: Optional[int],
        default_thread_rate_limit_per_user: int,
        flags: int,
        type: ChannelType = ChannelType.GUILD_TEXT,
    ) -> None:
        super().__init__(id, http, type, name)
        self.guild_id = guild_id
        self.position = position
        self.permission_overwrites = permission_overwrites
        self.topic = topic
        self.nsfw = nsfw
        self.last_message_id = last_message_id
        self.rate_limit_per_user = rate_limit_per_user
        self.parent_id = parent_id
        self.last_pin_timestamp = last_pin_timestamp
        self.default_auto_archive_duration = default_auto_archive_duration
        self.default_thread_rate_limit_per_user = default_thread_rate_limit_per_user
        self.flags = flags

    async def send(
        self,
        content: Optional[str] = None,
        *,
        tts: bool = False,
        embeds: Optional[list["Embed"]] = None,
        components: Optional[list[Any]] = None,
        files: Optional[list[Any]] = None,
        reference: Optional[Any] = None,
        mention_reply: bool = True,
        ephemeral: bool = False,
        suppress_embeds: bool = False,
        delete_after: Optional[float] = None,
    ) -> "Message":
        from .message import Message
        payload: dict[str, Any] = {}
        if content is not None:
            payload["content"] = content
        if tts:
            payload["tts"] = tts
        if embeds:
            payload["embeds"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in embeds]
        if components:
            payload["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in components]
        if reference is not None:
            payload["message_reference"] = {
                "message_id": str(reference.id if hasattr(reference, "id") else reference),
                "fail_if_not_exists": False,
            }
            if not mention_reply:
                payload["allowed_mentions"] = {"replied_user": False}
        flags = 0
        if ephemeral:
            flags |= 64
        if suppress_embeds:
            flags |= 4
        if flags:
            payload["flags"] = flags
        data = await self._http.create_message(self.id, payload, files=files)
        msg = Message._from_data(data, self._http)
        if delete_after is not None:
            import asyncio
            asyncio.get_event_loop().call_later(delete_after, lambda: asyncio.ensure_future(msg.delete()))
        return msg

    async def fetch_message(self, message_id: int) -> "Message":
        from .message import Message
        data = await self._http.get_channel_message(self.id, message_id)
        return Message._from_data(data, self._http)

    async def history(
        self,
        *,
        limit: int = 100,
        before: Optional[int] = None,
        after: Optional[int] = None,
        around: Optional[int] = None,
    ) -> "AsyncIterator[Message]":
        from .message import Message
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        if around:
            params["around"] = around
        data_list = await self._http.get_channel_messages(self.id, params)
        for data in data_list:
            yield Message._from_data(data, self._http)

    async def purge(self, limit: int = 100, *, reason: Optional[str] = None) -> int:
        messages_data = await self._http.get_channel_messages(self.id, {"limit": min(limit, 100)})
        message_ids = [int(m["id"]) for m in messages_data]
        if len(message_ids) == 1:
            await self._http.delete_message(self.id, message_ids[0], reason=reason)
        elif len(message_ids) > 1:
            await self._http.bulk_delete_messages(self.id, message_ids, reason=reason)
        return len(message_ids)

    async def trigger_typing(self) -> None:
        await self._http.trigger_typing_indicator(self.id)

    async def create_invite(
        self,
        *,
        max_age: int = 86400,
        max_uses: int = 0,
        temporary: bool = False,
        unique: bool = False,
        reason: Optional[str] = None,
    ) -> "Invite":
        from .invite import Invite
        payload = {
            "max_age": max_age,
            "max_uses": max_uses,
            "temporary": temporary,
            "unique": unique,
        }
        data = await self._http.create_channel_invite(self.id, payload, reason=reason)
        return Invite._from_data(data, self._http)

    async def edit(
        self,
        *,
        name: str = MISSING,
        topic: Optional[str] = MISSING,
        nsfw: bool = MISSING,
        rate_limit_per_user: int = MISSING,
        position: int = MISSING,
        permission_overwrites: Optional[list["PermissionOverwrite"]] = MISSING,
        parent_id: Optional[int] = MISSING,
        reason: Optional[str] = None,
    ) -> "TextChannel":
        payload: dict[str, Any] = {}
        if name is not MISSING:
            payload["name"] = name
        if topic is not MISSING:
            payload["topic"] = topic
        if nsfw is not MISSING:
            payload["nsfw"] = nsfw
        if rate_limit_per_user is not MISSING:
            payload["rate_limit_per_user"] = rate_limit_per_user
        if position is not MISSING:
            payload["position"] = position
        if permission_overwrites is not MISSING:
            payload["permission_overwrites"] = (
                [o.to_dict() for o in permission_overwrites] if permission_overwrites else []
            )
        if parent_id is not MISSING:
            payload["parent_id"] = parent_id
        data = await self._http.edit_channel(self.id, payload, reason=reason)
        return _channel_from_data(data, self._http)

    async def delete(self, *, reason: Optional[str] = None) -> None:
        await self._http.delete_channel(self.id, reason=reason)

    async def pins(self) -> list["Message"]:
        from .message import Message
        data_list = await self._http.get_pinned_messages(self.id)
        return [Message._from_data(d, self._http) for d in data_list]

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "TextChannel":
        from .permissions import PermissionOverwrite
        return cls(
            id=int(data["id"]),
            http=http,
            guild_id=int(data["guild_id"]) if data.get("guild_id") else 0,
            name=data.get("name", ""),
            position=data.get("position", 0),
            permission_overwrites=[
                PermissionOverwrite._from_data(o) for o in data.get("permission_overwrites", [])
            ],
            topic=data.get("topic"),
            nsfw=data.get("nsfw", False),
            last_message_id=int(data["last_message_id"]) if data.get("last_message_id") else None,
            rate_limit_per_user=data.get("rate_limit_per_user", 0),
            parent_id=int(data["parent_id"]) if data.get("parent_id") else None,
            last_pin_timestamp=parse_timestamp(data.get("last_pin_timestamp")),
            default_auto_archive_duration=data.get("default_auto_archive_duration"),
            default_thread_rate_limit_per_user=data.get("default_thread_rate_limit_per_user", 0),
            flags=data.get("flags", 0),
            type=ChannelType(data.get("type", 0)),
        )


class VoiceChannel(_BaseChannel):
    __slots__ = (
        "id",
        "_http",
        "type",
        "name",
        "guild_id",
        "position",
        "permission_overwrites",
        "bitrate",
        "user_limit",
        "parent_id",
        "rtc_region",
        "video_quality_mode",
        "nsfw",
        "rate_limit_per_user",
        "flags",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        guild_id: int,
        name: str,
        position: int,
        permission_overwrites: list[Any],
        bitrate: int,
        user_limit: int,
        parent_id: Optional[int],
        rtc_region: Optional[str],
        video_quality_mode: VideoQualityMode,
        nsfw: bool,
        rate_limit_per_user: int,
        flags: int,
        type: ChannelType = ChannelType.GUILD_VOICE,
    ) -> None:
        super().__init__(id, http, type, name)
        self.guild_id = guild_id
        self.position = position
        self.permission_overwrites = permission_overwrites
        self.bitrate = bitrate
        self.user_limit = user_limit
        self.parent_id = parent_id
        self.rtc_region = rtc_region
        self.video_quality_mode = video_quality_mode
        self.nsfw = nsfw
        self.rate_limit_per_user = rate_limit_per_user
        self.flags = flags

    async def send(self, content: Optional[str] = None, **kwargs: Any) -> "Message":
        from .message import Message
        payload: dict[str, Any] = {}
        if content is not None:
            payload["content"] = content
        data = await self._http.create_message(self.id, payload)
        return Message._from_data(data, self._http)

    async def edit(self, **kwargs: Any) -> "VoiceChannel":
        data = await self._http.edit_channel(self.id, kwargs)
        return _channel_from_data(data, self._http)

    async def delete(self, *, reason: Optional[str] = None) -> None:
        await self._http.delete_channel(self.id, reason=reason)

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "VoiceChannel":
        from .permissions import PermissionOverwrite
        return cls(
            id=int(data["id"]),
            http=http,
            guild_id=int(data["guild_id"]) if data.get("guild_id") else 0,
            name=data.get("name", ""),
            position=data.get("position", 0),
            permission_overwrites=[
                PermissionOverwrite._from_data(o) for o in data.get("permission_overwrites", [])
            ],
            bitrate=data.get("bitrate", 64000),
            user_limit=data.get("user_limit", 0),
            parent_id=int(data["parent_id"]) if data.get("parent_id") else None,
            rtc_region=data.get("rtc_region"),
            video_quality_mode=VideoQualityMode(data.get("video_quality_mode", 1)),
            nsfw=data.get("nsfw", False),
            rate_limit_per_user=data.get("rate_limit_per_user", 0),
            flags=data.get("flags", 0),
            type=ChannelType(data.get("type", 2)),
        )


class CategoryChannel(_BaseChannel):
    __slots__ = (
        "id",
        "_http",
        "type",
        "name",
        "guild_id",
        "position",
        "permission_overwrites",
        "nsfw",
        "flags",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        guild_id: int,
        name: str,
        position: int,
        permission_overwrites: list[Any],
        nsfw: bool,
        flags: int,
    ) -> None:
        super().__init__(id, http, ChannelType.GUILD_CATEGORY, name)
        self.guild_id = guild_id
        self.position = position
        self.permission_overwrites = permission_overwrites
        self.nsfw = nsfw
        self.flags = flags

    async def delete(self, *, reason: Optional[str] = None) -> None:
        await self._http.delete_channel(self.id, reason=reason)

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "CategoryChannel":
        from .permissions import PermissionOverwrite
        return cls(
            id=int(data["id"]),
            http=http,
            guild_id=int(data["guild_id"]) if data.get("guild_id") else 0,
            name=data.get("name", ""),
            position=data.get("position", 0),
            permission_overwrites=[
                PermissionOverwrite._from_data(o) for o in data.get("permission_overwrites", [])
            ],
            nsfw=data.get("nsfw", False),
            flags=data.get("flags", 0),
        )


class DMChannel(_BaseChannel):
    __slots__ = ("id", "_http", "type", "name", "recipient")

    def __init__(self, id: int, http: "HTTPClient", recipient: Optional["User"]) -> None:
        super().__init__(id, http, ChannelType.DM, None)
        self.recipient = recipient

    def __repr__(self) -> str:
        return f"<DMChannel id={self.id} recipient={self.recipient!r}>"

    async def send(self, content: Optional[str] = None, **kwargs: Any) -> "Message":
        from .message import Message
        payload: dict[str, Any] = {}
        if content is not None:
            payload["content"] = content
        data = await self._http.create_message(self.id, payload)
        return Message._from_data(data, self._http)

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "DMChannel":
        from .user import User
        recipients = data.get("recipients", [])
        recipient = User._from_data(recipients[0], http) if recipients else None
        return cls(id=int(data["id"]), http=http, recipient=recipient)


def _channel_from_data(data: dict[str, Any], http: "HTTPClient") -> Any:
    channel_type = ChannelType(data.get("type", 0))
    match channel_type:
        case ChannelType.GUILD_TEXT | ChannelType.GUILD_ANNOUNCEMENT:
            return TextChannel._from_data(data, http)
        case ChannelType.GUILD_VOICE | ChannelType.GUILD_STAGE_VOICE:
            return VoiceChannel._from_data(data, http)
        case ChannelType.GUILD_CATEGORY:
            return CategoryChannel._from_data(data, http)
        case ChannelType.DM | ChannelType.GROUP_DM:
            return DMChannel._from_data(data, http)
        case _:
            return TextChannel._from_data(data, http)
