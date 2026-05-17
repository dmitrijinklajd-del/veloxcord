from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from .base import DiscordModel
from ..enums import StageInstancePrivacyLevel
from ..utils import MISSING

if TYPE_CHECKING:
    from ..http.client import HTTPClient


class StageInstance(DiscordModel):
    __slots__ = (
        "id",
        "_http",
        "guild_id",
        "channel_id",
        "topic",
        "privacy_level",
        "discoverable_disabled",
        "guild_scheduled_event_id",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        guild_id: int,
        channel_id: int,
        topic: str,
        privacy_level: StageInstancePrivacyLevel,
        discoverable_disabled: bool,
        guild_scheduled_event_id: Optional[int],
    ) -> None:
        super().__init__(id, http)
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.topic = topic
        self.privacy_level = privacy_level
        self.discoverable_disabled = discoverable_disabled
        self.guild_scheduled_event_id = guild_scheduled_event_id

    def __repr__(self) -> str:
        return f"<StageInstance id={self.id} topic={self.topic!r}>"

    async def edit(
        self,
        *,
        topic: str = MISSING,
        privacy_level: StageInstancePrivacyLevel = MISSING,
        reason: Optional[str] = None,
    ) -> "StageInstance":
        payload: dict[str, Any] = {}
        if topic is not MISSING:
            payload["topic"] = topic
        if privacy_level is not MISSING:
            payload["privacy_level"] = privacy_level.value
        data = await self._http.edit_stage_instance(self.channel_id, payload, reason=reason)
        return StageInstance._from_data(data, self._http)

    async def delete(self, *, reason: Optional[str] = None) -> None:
        await self._http.delete_stage_instance(self.channel_id, reason=reason)

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "StageInstance":
        return cls(
            id=int(data["id"]),
            http=http,
            guild_id=int(data["guild_id"]),
            channel_id=int(data["channel_id"]),
            topic=data["topic"],
            privacy_level=StageInstancePrivacyLevel(data.get("privacy_level", 2)),
            discoverable_disabled=data.get("discoverable_disabled", False),
            guild_scheduled_event_id=int(data["guild_scheduled_event_id"]) if data.get("guild_scheduled_event_id") else None,
        )
