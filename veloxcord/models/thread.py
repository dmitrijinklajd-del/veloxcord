from __future__ import annotations
import datetime
from typing import TYPE_CHECKING, Any, Optional

from .base import DiscordModel
from ..enums import ChannelType
from ..utils import parse_timestamp, MISSING

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from .message import Message
    from .member import Member


class ThreadMetadata:
    __slots__ = (
        "archived",
        "auto_archive_duration",
        "archive_timestamp",
        "locked",
        "invitable",
        "create_timestamp",
    )

    def __init__(
        self,
        archived: bool,
        auto_archive_duration: int,
        archive_timestamp: datetime.datetime,
        locked: bool,
        invitable: bool,
        create_timestamp: Optional[datetime.datetime],
    ) -> None:
        self.archived = archived
        self.auto_archive_duration = auto_archive_duration
        self.archive_timestamp = archive_timestamp
        self.locked = locked
        self.invitable = invitable
        self.create_timestamp = create_timestamp

    def __repr__(self) -> str:
        return f"<ThreadMetadata archived={self.archived} locked={self.locked}>"

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "ThreadMetadata":
        return cls(
            archived=data.get("archived", False),
            auto_archive_duration=data.get("auto_archive_duration", 1440),
            archive_timestamp=parse_timestamp(data.get("archive_timestamp")) or datetime.datetime.now(tz=datetime.timezone.utc),
            locked=data.get("locked", False),
            invitable=data.get("invitable", True),
            create_timestamp=parse_timestamp(data.get("create_timestamp")),
        )


class ThreadMember:
    __slots__ = ("id", "user_id", "join_timestamp", "flags", "member")

    def __init__(
        self,
        id: Optional[int],
        user_id: Optional[int],
        join_timestamp: datetime.datetime,
        flags: int,
        member: Optional["Member"],
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.join_timestamp = join_timestamp
        self.flags = flags
        self.member = member

    def __repr__(self) -> str:
        return f"<ThreadMember user_id={self.user_id}>"

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: Any, guild_id: int = 0) -> "ThreadMember":
        from .member import Member
        member_data = data.get("member")
        return cls(
            id=int(data["id"]) if data.get("id") else None,
            user_id=int(data["user_id"]) if data.get("user_id") else None,
            join_timestamp=parse_timestamp(data.get("join_timestamp")) or datetime.datetime.now(tz=datetime.timezone.utc),
            flags=data.get("flags", 0),
            member=Member._from_data(member_data, http, guild_id) if member_data else None,
        )


class Thread(DiscordModel):
    __slots__ = (
        "id",
        "_http",
        "type",
        "name",
        "guild_id",
        "parent_id",
        "owner_id",
        "last_message_id",
        "message_count",
        "member_count",
        "rate_limit_per_user",
        "flags",
        "metadata",
        "member",
        "nsfw",
        "total_message_sent",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        type: ChannelType,
        name: str,
        guild_id: int,
        parent_id: Optional[int],
        owner_id: Optional[int],
        last_message_id: Optional[int],
        message_count: int,
        member_count: int,
        rate_limit_per_user: int,
        flags: int,
        metadata: Optional[ThreadMetadata],
        member: Optional[ThreadMember],
        nsfw: bool,
        total_message_sent: int,
    ) -> None:
        super().__init__(id, http)
        self.type = type
        self.name = name
        self.guild_id = guild_id
        self.parent_id = parent_id
        self.owner_id = owner_id
        self.last_message_id = last_message_id
        self.message_count = message_count
        self.member_count = member_count
        self.rate_limit_per_user = rate_limit_per_user
        self.flags = flags
        self.metadata = metadata
        self.member = member
        self.nsfw = nsfw
        self.total_message_sent = total_message_sent

    def __repr__(self) -> str:
        return f"<Thread id={self.id} name={self.name!r} archived={self.metadata.archived if self.metadata else None}>"

    @property
    def mention(self) -> str:
        return f"<#{self.id}>"

    @property
    def is_private(self) -> bool:
        return self.type == ChannelType.PRIVATE_THREAD

    @property
    def archived(self) -> bool:
        return self.metadata.archived if self.metadata else False

    @property
    def locked(self) -> bool:
        return self.metadata.locked if self.metadata else False

    async def send(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[list[Any]] = None,
        components: Optional[list[Any]] = None,
    ) -> "Message":
        from .message import Message
        payload: dict[str, Any] = {}
        if content is not None:
            payload["content"] = content
        if embeds:
            payload["embeds"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in embeds]
        if components:
            payload["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in components]
        data = await self._http.create_message(self.id, payload)
        return Message._from_data(data, self._http)

    async def join(self) -> None:
        await self._http.join_thread(self.id)

    async def leave(self) -> None:
        await self._http.leave_thread(self.id)

    async def add_member(self, user_id: int) -> None:
        await self._http.add_thread_member(self.id, user_id)

    async def remove_member(self, user_id: int) -> None:
        await self._http.remove_thread_member(self.id, user_id)

    async def edit(
        self,
        *,
        name: str = MISSING,
        archived: bool = MISSING,
        auto_archive_duration: int = MISSING,
        locked: bool = MISSING,
        invitable: bool = MISSING,
        rate_limit_per_user: Optional[int] = MISSING,
        reason: Optional[str] = None,
    ) -> "Thread":
        payload: dict[str, Any] = {}
        if name is not MISSING:
            payload["name"] = name
        if archived is not MISSING:
            payload["archived"] = archived
        if auto_archive_duration is not MISSING:
            payload["auto_archive_duration"] = auto_archive_duration
        if locked is not MISSING:
            payload["locked"] = locked
        if invitable is not MISSING:
            payload["invitable"] = invitable
        if rate_limit_per_user is not MISSING:
            payload["rate_limit_per_user"] = rate_limit_per_user
        data = await self._http.edit_channel(self.id, payload, reason=reason)
        return Thread._from_data(data, self._http)

    async def delete(self, *, reason: Optional[str] = None) -> None:
        await self._http.delete_channel(self.id, reason=reason)

    async def fetch_members(self) -> list[ThreadMember]:
        data_list = await self._http.list_thread_members(self.id)
        return [ThreadMember._from_data(d, self._http, self.guild_id) for d in data_list]

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "Thread":
        metadata_data = data.get("thread_metadata")
        member_data = data.get("member")
        return cls(
            id=int(data["id"]),
            http=http,
            type=ChannelType(data.get("type", 11)),
            name=data.get("name", ""),
            guild_id=int(data["guild_id"]) if data.get("guild_id") else 0,
            parent_id=int(data["parent_id"]) if data.get("parent_id") else None,
            owner_id=int(data["owner_id"]) if data.get("owner_id") else None,
            last_message_id=int(data["last_message_id"]) if data.get("last_message_id") else None,
            message_count=data.get("message_count", 0),
            member_count=data.get("member_count", 0),
            rate_limit_per_user=data.get("rate_limit_per_user", 0),
            flags=data.get("flags", 0),
            metadata=ThreadMetadata._from_data(metadata_data) if metadata_data else None,
            member=ThreadMember._from_data(member_data, http) if member_data else None,
            nsfw=data.get("nsfw", False),
            total_message_sent=data.get("total_message_sent", 0),
        )
