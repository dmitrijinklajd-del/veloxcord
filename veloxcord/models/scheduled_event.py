from __future__ import annotations
import datetime
from typing import TYPE_CHECKING, Any, Optional

from .base import DiscordModel
from ..enums import (
    GuildScheduledEventStatus,
    GuildScheduledEventEntityType,
    StageInstancePrivacyLevel,
)
from ..utils import parse_timestamp, MISSING

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from .user import User


class GuildScheduledEventEntityMetadata:
    __slots__ = ("location",)

    def __init__(self, location: Optional[str]) -> None:
        self.location = location

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "GuildScheduledEventEntityMetadata":
        return cls(location=data.get("location"))


class GuildScheduledEvent(DiscordModel):
    __slots__ = (
        "id",
        "_http",
        "guild_id",
        "channel_id",
        "creator_id",
        "name",
        "description",
        "scheduled_start_time",
        "scheduled_end_time",
        "privacy_level",
        "status",
        "entity_type",
        "entity_id",
        "entity_metadata",
        "creator",
        "user_count",
        "image",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        guild_id: int,
        channel_id: Optional[int],
        creator_id: Optional[int],
        name: str,
        description: Optional[str],
        scheduled_start_time: datetime.datetime,
        scheduled_end_time: Optional[datetime.datetime],
        privacy_level: int,
        status: GuildScheduledEventStatus,
        entity_type: GuildScheduledEventEntityType,
        entity_id: Optional[int],
        entity_metadata: Optional[GuildScheduledEventEntityMetadata],
        creator: Optional["User"],
        user_count: Optional[int],
        image: Optional[str],
    ) -> None:
        super().__init__(id, http)
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.creator_id = creator_id
        self.name = name
        self.description = description
        self.scheduled_start_time = scheduled_start_time
        self.scheduled_end_time = scheduled_end_time
        self.privacy_level = privacy_level
        self.status = status
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.entity_metadata = entity_metadata
        self.creator = creator
        self.user_count = user_count
        self.image = image

    def __repr__(self) -> str:
        return f"<GuildScheduledEvent id={self.id} name={self.name!r} status={self.status}>"

    @property
    def cover_image_url(self) -> Optional[str]:
        if self.image is None:
            return None
        return f"https://cdn.discordapp.com/guild-events/{self.id}/{self.image}.png?size=1024"

    async def edit(
        self,
        *,
        name: str = MISSING,
        status: GuildScheduledEventStatus = MISSING,
        description: Optional[str] = MISSING,
        reason: Optional[str] = None,
    ) -> "GuildScheduledEvent":
        payload: dict[str, Any] = {}
        if name is not MISSING:
            payload["name"] = name
        if status is not MISSING:
            payload["status"] = status.value
        if description is not MISSING:
            payload["description"] = description
        data = await self._http.edit_guild_scheduled_event(self.guild_id, self.id, payload, reason=reason)
        return GuildScheduledEvent._from_data(data, self._http)

    async def delete(self) -> None:
        await self._http.delete_guild_scheduled_event(self.guild_id, self.id)

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "GuildScheduledEvent":
        from .user import User
        entity_meta = data.get("entity_metadata")
        creator_data = data.get("creator")
        return cls(
            id=int(data["id"]),
            http=http,
            guild_id=int(data["guild_id"]),
            channel_id=int(data["channel_id"]) if data.get("channel_id") else None,
            creator_id=int(data["creator_id"]) if data.get("creator_id") else None,
            name=data["name"],
            description=data.get("description"),
            scheduled_start_time=parse_timestamp(data["scheduled_start_time"]) or datetime.datetime.now(tz=datetime.timezone.utc),
            scheduled_end_time=parse_timestamp(data.get("scheduled_end_time")),
            privacy_level=data.get("privacy_level", 2),
            status=GuildScheduledEventStatus(data.get("status", 1)),
            entity_type=GuildScheduledEventEntityType(data.get("entity_type", 3)),
            entity_id=int(data["entity_id"]) if data.get("entity_id") else None,
            entity_metadata=GuildScheduledEventEntityMetadata._from_data(entity_meta) if entity_meta else None,
            creator=User._from_data(creator_data, http) if creator_data else None,
            user_count=data.get("user_count"),
            image=data.get("image"),
        )
