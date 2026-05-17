from __future__ import annotations
import datetime
from typing import TYPE_CHECKING, Any, Optional

from .base import DiscordModel
from ..enums import MessageType
from ..flags import MessageFlags
from ..utils import parse_timestamp, MISSING

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from .user import User
    from .member import Member
    from .embed import Embed
    from .attachment import Attachment
    from .emoji import PartialEmoji
    from .sticker import StickerItem
    from .channel import TextChannel


class MessageReference:
    __slots__ = ("message_id", "channel_id", "guild_id", "fail_if_not_exists")

    def __init__(
        self,
        message_id: Optional[int],
        channel_id: Optional[int],
        guild_id: Optional[int],
        fail_if_not_exists: bool = True,
    ) -> None:
        self.message_id = message_id
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.fail_if_not_exists = fail_if_not_exists

    def __repr__(self) -> str:
        return f"<MessageReference message_id={self.message_id}>"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.message_id:
            payload["message_id"] = str(self.message_id)
        if self.channel_id:
            payload["channel_id"] = str(self.channel_id)
        if self.guild_id:
            payload["guild_id"] = str(self.guild_id)
        payload["fail_if_not_exists"] = self.fail_if_not_exists
        return payload

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "MessageReference":
        return cls(
            message_id=int(data["message_id"]) if data.get("message_id") else None,
            channel_id=int(data["channel_id"]) if data.get("channel_id") else None,
            guild_id=int(data["guild_id"]) if data.get("guild_id") else None,
            fail_if_not_exists=data.get("fail_if_not_exists", True),
        )


class Reaction:
    __slots__ = ("count", "me", "emoji")

    def __init__(self, count: int, me: bool, emoji: "PartialEmoji") -> None:
        self.count = count
        self.me = me
        self.emoji = emoji

    def __repr__(self) -> str:
        return f"<Reaction emoji={self.emoji} count={self.count}>"

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "Reaction":
        from .emoji import PartialEmoji
        return cls(
            count=data.get("count", 0),
            me=data.get("me", False),
            emoji=PartialEmoji._from_data(data["emoji"]),
        )


class Message(DiscordModel):
    __slots__ = (
        "id",
        "_http",
        "channel_id",
        "guild_id",
        "author",
        "member",
        "content",
        "timestamp",
        "edited_timestamp",
        "tts",
        "mention_everyone",
        "mentions",
        "mention_role_ids",
        "mention_channels",
        "attachments",
        "embeds",
        "reactions",
        "nonce",
        "pinned",
        "webhook_id",
        "type",
        "activity",
        "application",
        "application_id",
        "message_reference",
        "flags",
        "referenced_message",
        "interaction",
        "thread",
        "components",
        "sticker_items",
        "position",
        "_channel",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        channel_id: int,
        guild_id: Optional[int],
        author: "User",
        member: Optional["Member"],
        content: str,
        timestamp: datetime.datetime,
        edited_timestamp: Optional[datetime.datetime],
        tts: bool,
        mention_everyone: bool,
        mentions: list["User"],
        mention_role_ids: list[int],
        mention_channels: list[Any],
        attachments: list["Attachment"],
        embeds: list["Embed"],
        reactions: list[Reaction],
        nonce: Optional[str | int],
        pinned: bool,
        webhook_id: Optional[int],
        type: MessageType,
        activity: Optional[Any],
        application: Optional[Any],
        application_id: Optional[int],
        message_reference: Optional[MessageReference],
        flags: MessageFlags,
        referenced_message: Optional["Message"],
        interaction: Optional[Any],
        thread: Optional[Any],
        components: list[Any],
        sticker_items: list["StickerItem"],
        position: Optional[int],
    ) -> None:
        super().__init__(id, http)
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.author = author
        self.member = member
        self.content = content
        self.timestamp = timestamp
        self.edited_timestamp = edited_timestamp
        self.tts = tts
        self.mention_everyone = mention_everyone
        self.mentions = mentions
        self.mention_role_ids = mention_role_ids
        self.mention_channels = mention_channels
        self.attachments = attachments
        self.embeds = embeds
        self.reactions = reactions
        self.nonce = nonce
        self.pinned = pinned
        self.webhook_id = webhook_id
        self.type = type
        self.activity = activity
        self.application = application
        self.application_id = application_id
        self.message_reference = message_reference
        self.flags = flags
        self.referenced_message = referenced_message
        self.interaction = interaction
        self.thread = thread
        self.components = components
        self.sticker_items = sticker_items
        self.position = position
        self._channel: Optional[Any] = None

    def __repr__(self) -> str:
        return f"<Message id={self.id} channel_id={self.channel_id} author={self.author!r}>"

    @property
    def channel(self) -> Any:
        if self._channel is not None:
            return self._channel
        from .channel import TextChannel, _channel_from_data
        return _channel_from_data({"id": str(self.channel_id), "type": 0, "guild_id": str(self.guild_id) if self.guild_id else None}, self._http)

    @channel.setter
    def channel(self, value: Any) -> None:
        self._channel = value

    @property
    def guild(self) -> Optional[Any]:
        return None

    @property
    def jump_url(self) -> str:
        guild_id = self.guild_id or "@me"
        return f"https://discord.com/channels/{guild_id}/{self.channel_id}/{self.id}"

    @property
    def is_system(self) -> bool:
        return self.type not in (MessageType.DEFAULT, MessageType.REPLY, MessageType.CHAT_INPUT_COMMAND, MessageType.CONTEXT_MENU_COMMAND)

    async def reply(
        self,
        content: Optional[str] = None,
        *,
        mention_author: bool = True,
        **kwargs: Any,
    ) -> "Message":
        payload: dict[str, Any] = {}
        if content is not None:
            payload["content"] = content
        payload["message_reference"] = {"message_id": str(self.id), "fail_if_not_exists": False}
        payload["allowed_mentions"] = {"replied_user": mention_author}
        for k, v in kwargs.items():
            if k == "embeds" and v:
                payload["embeds"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in v]
            elif k == "components" and v:
                payload["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in v]
            else:
                payload[k] = v
        data = await self._http.create_message(self.channel_id, payload)
        return Message._from_data(data, self._http)

    async def edit(
        self,
        content: Optional[str] = MISSING,
        *,
        embeds: Optional[list[Any]] = MISSING,
        components: Optional[list[Any]] = MISSING,
        suppress_embeds: bool = MISSING,
    ) -> "Message":
        payload: dict[str, Any] = {}
        if content is not MISSING:
            payload["content"] = content
        if embeds is not MISSING:
            payload["embeds"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in (embeds or [])]
        if components is not MISSING:
            payload["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in (components or [])]
        if suppress_embeds is not MISSING:
            flags = self.flags.value
            if suppress_embeds:
                flags |= 4
            else:
                flags &= ~4
            payload["flags"] = flags
        data = await self._http.edit_message(self.channel_id, self.id, payload)
        return Message._from_data(data, self._http)

    async def delete(self, *, delay: Optional[float] = None, reason: Optional[str] = None) -> None:
        if delay is not None:
            import asyncio
            await asyncio.sleep(delay)
        await self._http.delete_message(self.channel_id, self.id, reason=reason)

    async def pin(self, *, reason: Optional[str] = None) -> None:
        await self._http.pin_message(self.channel_id, self.id, reason=reason)

    async def unpin(self, *, reason: Optional[str] = None) -> None:
        await self._http.unpin_message(self.channel_id, self.id, reason=reason)

    async def add_reaction(self, emoji: str) -> None:
        await self._http.create_reaction(self.channel_id, self.id, emoji)

    async def remove_reaction(self, emoji: str, user_id: Optional[int] = None) -> None:
        if user_id is None:
            await self._http.delete_own_reaction(self.channel_id, self.id, emoji)
        else:
            await self._http.delete_user_reaction(self.channel_id, self.id, emoji, user_id)

    async def clear_reactions(self) -> None:
        await self._http.delete_all_reactions(self.channel_id, self.id)

    async def publish(self) -> "Message":
        data = await self._http.crosspost_message(self.channel_id, self.id)
        return Message._from_data(data, self._http)

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "Message":
        from .user import User
        from .member import Member
        from .embed import Embed
        from .attachment import Attachment
        from .sticker import StickerItem

        author_data = data.get("author", {})
        author = User._from_data(author_data, http) if author_data else None

        member_data = data.get("member")
        member = None
        if member_data and author:
            member_data["user"] = author_data
            guild_id = int(data["guild_id"]) if data.get("guild_id") else 0
            member = Member._from_data(member_data, http, guild_id)

        ref_data = data.get("referenced_message")

        return cls(
            id=int(data["id"]),
            http=http,
            channel_id=int(data["channel_id"]),
            guild_id=int(data["guild_id"]) if data.get("guild_id") else None,
            author=author,
            member=member,
            content=data.get("content", ""),
            timestamp=parse_timestamp(data.get("timestamp")) or datetime.datetime.now(tz=datetime.timezone.utc),
            edited_timestamp=parse_timestamp(data.get("edited_timestamp")),
            tts=data.get("tts", False),
            mention_everyone=data.get("mention_everyone", False),
            mentions=[User._from_data(u, http) for u in data.get("mentions", [])],
            mention_role_ids=[int(r) for r in data.get("mention_roles", [])],
            mention_channels=data.get("mention_channels", []),
            attachments=[Attachment._from_data(a) for a in data.get("attachments", [])],
            embeds=[Embed._from_data(e) for e in data.get("embeds", [])],
            reactions=[Reaction._from_data(r) for r in data.get("reactions", [])],
            nonce=data.get("nonce"),
            pinned=data.get("pinned", False),
            webhook_id=int(data["webhook_id"]) if data.get("webhook_id") else None,
            type=MessageType(data.get("type", 0)),
            activity=data.get("activity"),
            application=data.get("application"),
            application_id=int(data["application_id"]) if data.get("application_id") else None,
            message_reference=MessageReference._from_data(data["message_reference"]) if data.get("message_reference") else None,
            flags=MessageFlags(data.get("flags", 0)),
            referenced_message=cls._from_data(ref_data, http) if ref_data else None,
            interaction=data.get("interaction"),
            thread=data.get("thread"),
            components=data.get("components", []),
            sticker_items=[StickerItem._from_data(s) for s in data.get("sticker_items", [])],
            position=data.get("position"),
        )
