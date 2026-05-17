from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from .base import DiscordModel
from ..enums import InteractionType, InteractionCallbackType
from ..utils import MISSING

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from .user import User
    from .member import Member
    from .message import Message
    from .channel import TextChannel
    from .guild import Guild
    from .modal import Modal
    from .embed import Embed


class InteractionData:
    __slots__ = (
        "id",
        "name",
        "type",
        "resolved",
        "options",
        "guild_id",
        "target_id",
        "custom_id",
        "component_type",
        "values",
        "components",
    )

    def __init__(
        self,
        id: Optional[int],
        name: Optional[str],
        type: Optional[int],
        resolved: Optional[dict[str, Any]],
        options: list[Any],
        guild_id: Optional[int],
        target_id: Optional[int],
        custom_id: Optional[str],
        component_type: Optional[int],
        values: list[str],
        components: list[Any],
    ) -> None:
        self.id = id
        self.name = name
        self.type = type
        self.resolved = resolved or {}
        self.options = options
        self.guild_id = guild_id
        self.target_id = target_id
        self.custom_id = custom_id
        self.component_type = component_type
        self.values = values
        self.components = components

    def __repr__(self) -> str:
        return f"<InteractionData name={self.name!r} custom_id={self.custom_id!r}>"

    def get_option(self, name: str) -> Optional[Any]:
        for option in self.options:
            if option.get("name") == name:
                return option
        return None

    def get_option_value(self, name: str) -> Optional[Any]:
        option = self.get_option(name)
        return option.get("value") if option else None

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "InteractionData":
        return cls(
            id=int(data["id"]) if data.get("id") else None,
            name=data.get("name"),
            type=data.get("type"),
            resolved=data.get("resolved"),
            options=data.get("options", []),
            guild_id=int(data["guild_id"]) if data.get("guild_id") else None,
            target_id=int(data["target_id"]) if data.get("target_id") else None,
            custom_id=data.get("custom_id"),
            component_type=data.get("component_type"),
            values=data.get("values", []),
            components=data.get("components", []),
        )


class Interaction(DiscordModel):
    __slots__ = (
        "id",
        "_http",
        "application_id",
        "type",
        "data",
        "guild_id",
        "channel",
        "channel_id",
        "member",
        "user",
        "token",
        "version",
        "message",
        "app_permissions",
        "locale",
        "guild_locale",
        "_responded",
        "_deferred",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        application_id: int,
        type: InteractionType,
        data: Optional[InteractionData],
        guild_id: Optional[int],
        channel: Optional[Any],
        channel_id: Optional[int],
        member: Optional["Member"],
        user: Optional["User"],
        token: str,
        version: int,
        message: Optional["Message"],
        app_permissions: Optional[int],
        locale: str,
        guild_locale: Optional[str],
    ) -> None:
        super().__init__(id, http)
        self.application_id = application_id
        self.type = type
        self.data = data
        self.guild_id = guild_id
        self.channel = channel
        self.channel_id = channel_id
        self.member = member
        self.user = user
        self.token = token
        self.version = version
        self.message = message
        self.app_permissions = app_permissions
        self.locale = locale
        self.guild_locale = guild_locale
        self._responded = False
        self._deferred = False

    def __repr__(self) -> str:
        return f"<Interaction id={self.id} type={self.type} guild_id={self.guild_id}>"

    @property
    def author(self) -> Optional[Any]:
        return self.member or self.user

    @property
    def guild(self) -> Optional[Any]:
        return None

    async def respond(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[list["Embed"]] = None,
        components: Optional[list[Any]] = None,
        ephemeral: bool = False,
        tts: bool = False,
        suppress_embeds: bool = False,
    ) -> None:
        # Если уже задефёрено auto-defer'ом — редактируем вместо нового ответа
        if self._deferred:
            await self.edit_response(content, embeds=embeds, components=components)
            return
        if self._responded:
            await self.followup(content, embeds=embeds, components=components, ephemeral=ephemeral)
            return
        flags = 0
        if ephemeral:
            flags |= 64
        if suppress_embeds:
            flags |= 4
        payload: dict[str, Any] = {"type": InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE.value, "data": {}}
        if content is not None:
            payload["data"]["content"] = content
        if embeds:
            payload["data"]["embeds"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in embeds]
        if components:
            payload["data"]["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in components]
        if tts:
            payload["data"]["tts"] = tts
        if flags:
            payload["data"]["flags"] = flags
        await self._http.create_interaction_response(self.id, self.token, payload)
        self._responded = True

    async def defer(self, *, ephemeral: bool = False, thinking: bool = True) -> None:
        callback_type = (
            InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
            if thinking
            else InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
        )
        payload: dict[str, Any] = {"type": callback_type.value}
        if ephemeral:
            payload["data"] = {"flags": 64}
        await self._http.create_interaction_response(self.id, self.token, payload)
        self._responded = True
        self._deferred = True

    async def edit_response(
        self,
        content: Optional[str] = MISSING,
        *,
        embeds: Optional[list[Any]] = MISSING,
        components: Optional[list[Any]] = MISSING,
    ) -> "Message":
        from .message import Message
        payload: dict[str, Any] = {}
        if content is not MISSING:
            payload["content"] = content
        if embeds is not MISSING:
            payload["embeds"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in (embeds or [])]
        if components is not MISSING:
            payload["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in (components or [])]
        data = await self._http.edit_original_interaction_response(self.application_id, self.token, payload)
        return Message._from_data(data, self._http)

    async def delete_response(self) -> None:
        await self._http.delete_original_interaction_response(self.application_id, self.token)

    async def followup(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[list[Any]] = None,
        components: Optional[list[Any]] = None,
        ephemeral: bool = False,
    ) -> "Message":
        from .message import Message
        flags = 64 if ephemeral else 0
        payload: dict[str, Any] = {}
        if content is not None:
            payload["content"] = content
        if embeds:
            payload["embeds"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in embeds]
        if components:
            payload["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in components]
        if flags:
            payload["flags"] = flags
        data = await self._http.create_followup_message(self.application_id, self.token, payload)
        return Message._from_data(data, self._http)

    async def send_modal(self, modal: "Modal") -> None:
        payload = {
            "type": InteractionCallbackType.MODAL.value,
            "data": modal.to_dict(),
        }
        await self._http.create_interaction_response(self.id, self.token, payload)
        self._responded = True

    async def update_message(
        self,
        content: Optional[str] = MISSING,
        *,
        embeds: Optional[list[Any]] = MISSING,
        components: Optional[list[Any]] = MISSING,
    ) -> None:
        payload: dict[str, Any] = {"type": InteractionCallbackType.UPDATE_MESSAGE.value, "data": {}}
        if content is not MISSING:
            payload["data"]["content"] = content
        if embeds is not MISSING:
            payload["data"]["embeds"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in (embeds or [])]
        if components is not MISSING:
            payload["data"]["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in (components or [])]
        await self._http.create_interaction_response(self.id, self.token, payload)
        self._responded = True

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "Interaction":
        from .member import Member
        from .user import User
        from .message import Message
        from .channel import _channel_from_data

        interaction_type = InteractionType(data["type"])
        interaction_data_raw = data.get("data")
        interaction_data = InteractionData._from_data(interaction_data_raw) if interaction_data_raw else None

        guild_id = int(data["guild_id"]) if data.get("guild_id") else None

        member_data = data.get("member")
        member = Member._from_data(member_data, http, guild_id or 0) if member_data else None

        user_data = data.get("user")
        if user_data is None and member_data:
            user_data = member_data.get("user")
        user = User._from_data(user_data, http) if user_data else None

        channel_data = data.get("channel")
        channel = _channel_from_data(channel_data, http) if channel_data else None

        message_data = data.get("message")
        message = Message._from_data(message_data, http) if message_data else None

        return cls(
            id=int(data["id"]),
            http=http,
            application_id=int(data["application_id"]),
            type=interaction_type,
            data=interaction_data,
            guild_id=guild_id,
            channel=channel,
            channel_id=int(data["channel_id"]) if data.get("channel_id") else None,
            member=member,
            user=user,
            token=data["token"],
            version=data.get("version", 1),
            message=message,
            app_permissions=int(data["app_permissions"]) if data.get("app_permissions") else None,
            locale=data.get("locale", "en-US"),
            guild_locale=data.get("guild_locale"),
        )
