from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from ..models.guild import Guild
    from ..models.channel import TextChannel
    from ..models.member import Member
    from ..models.user import User
    from ..models.message import Message
    from ..models.interaction import Interaction
    from ..models.embed import Embed


class PrefixContext:
    __slots__ = (
        "message",
        "bot",
        "prefix",
        "command_name",
        "args",
        "kwargs",
        "_http",
    )

    def __init__(
        self,
        message: "Message",
        bot: Any,
        prefix: str,
        command_name: str,
        args: list[str],
        kwargs: dict[str, Any],
        http: "HTTPClient",
    ) -> None:
        self.message = message
        self.bot = bot
        self.prefix = prefix
        self.command_name = command_name
        self.args = args
        self.kwargs = kwargs
        self._http = http

    def __repr__(self) -> str:
        return f"<PrefixContext command={self.command_name!r} author={self.author!r}>"

    @property
    def guild_id(self) -> Optional[int]:
        return self.message.guild_id

    @property
    def channel_id(self) -> int:
        return self.message.channel_id

    @property
    def channel(self) -> Any:
        return self.message.channel

    @property
    def author(self) -> Any:
        return self.message.member or self.message.author

    @property
    def user(self) -> Any:
        return self.message.author

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
        mention_author: bool = False,
    ) -> "Message":
        return await self.message.reply(
            content,
            mention_author=mention_author,
            embeds=embeds,
            components=components,
        )

    async def send(self, content: Optional[str] = None, **kwargs: Any) -> "Message":
        from ..models.message import Message
        payload: dict[str, Any] = {}
        if content is not None:
            payload["content"] = content
        for k, v in kwargs.items():
            if k == "embeds" and v:
                payload["embeds"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in v]
            elif k == "components" and v:
                payload["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in v]
            else:
                payload[k] = v
        data = await self._http.create_message(self.channel_id, payload)
        return Message._from_data(data, self._http)


class SlashContext:
    __slots__ = (
        "interaction",
        "bot",
        "command_name",
        "_http",
    )

    def __init__(
        self,
        interaction: "Interaction",
        bot: Any,
        command_name: str,
        http: "HTTPClient",
    ) -> None:
        self.interaction = interaction
        self.bot = bot
        self.command_name = command_name
        self._http = http

    def __repr__(self) -> str:
        return f"<SlashContext command={self.command_name!r} author={self.author!r}>"

    @property
    def guild_id(self) -> Optional[int]:
        return self.interaction.guild_id

    @property
    def channel_id(self) -> Optional[int]:
        return self.interaction.channel_id

    @property
    def channel(self) -> Optional[Any]:
        return self.interaction.channel

    @property
    def author(self) -> Optional[Any]:
        return self.interaction.member or self.interaction.user

    @property
    def user(self) -> Optional[Any]:
        return self.interaction.user

    @property
    def guild(self) -> Optional[Any]:
        return None

    @property
    def data(self) -> Optional[Any]:
        return self.interaction.data

    @property
    def locale(self) -> str:
        return self.interaction.locale

    def get_option(self, name: str) -> Optional[Any]:
        if self.interaction.data is None:
            return None
        return self.interaction.data.get_option_value(name)

    async def respond(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[list["Embed"]] = None,
        components: Optional[list[Any]] = None,
        ephemeral: bool = False,
        tts: bool = False,
    ) -> None:
        if self.interaction._deferred:
            # Уже задефёрено (auto-defer сработал) — редактируем ответ
            await self.interaction.edit_response(
                content, embeds=embeds, components=components
            )
        else:
            await self.interaction.respond(
                content,
                embeds=embeds,
                components=components,
                ephemeral=ephemeral,
                tts=tts,
            )

    async def defer(self, *, ephemeral: bool = False) -> None:
        await self.interaction.defer(ephemeral=ephemeral)

    async def followup(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[list[Any]] = None,
        components: Optional[list[Any]] = None,
        ephemeral: bool = False,
    ) -> "Message":
        return await self.interaction.followup(
            content, embeds=embeds, components=components, ephemeral=ephemeral
        )

    async def edit_response(self, content: Optional[str] = None, **kwargs: Any) -> "Message":
        return await self.interaction.edit_response(content, **kwargs)

    async def send_modal(self, modal: Any) -> None:
        await self.interaction.send_modal(modal)


class ComponentContext:
    __slots__ = (
        "interaction",
        "bot",
        "custom_id",
        "_http",
    )

    def __init__(
        self,
        interaction: "Interaction",
        bot: Any,
        custom_id: str,
        http: "HTTPClient",
    ) -> None:
        self.interaction = interaction
        self.bot = bot
        self.custom_id = custom_id
        self._http = http

    def __repr__(self) -> str:
        return f"<ComponentContext custom_id={self.custom_id!r} author={self.author!r}>"

    @property
    def guild_id(self) -> Optional[int]:
        return self.interaction.guild_id

    @property
    def channel_id(self) -> Optional[int]:
        return self.interaction.channel_id

    @property
    def author(self) -> Optional[Any]:
        return self.interaction.member or self.interaction.user

    @property
    def user(self) -> Optional[Any]:
        return self.interaction.user

    @property
    def message(self) -> Optional[Any]:
        return self.interaction.message

    @property
    def values(self) -> list[str]:
        if self.interaction.data is None:
            return []
        return self.interaction.data.values

    async def respond(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[list[Any]] = None,
        components: Optional[list[Any]] = None,
        ephemeral: bool = False,
    ) -> None:
        await self.interaction.respond(
            content, embeds=embeds, components=components, ephemeral=ephemeral
        )

    async def update_message(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[list[Any]] = None,
        components: Optional[list[Any]] = None,
    ) -> None:
        await self.interaction.update_message(
            content, embeds=embeds, components=components
        )

    async def defer(self, *, ephemeral: bool = False) -> None:
        await self.interaction.defer(ephemeral=ephemeral, thinking=False)

    async def followup(self, content: Optional[str] = None, **kwargs: Any) -> "Message":
        return await self.interaction.followup(content, **kwargs)


class ModalContext:
    __slots__ = (
        "interaction",
        "bot",
        "custom_id",
        "_modal_data",
        "_http",
    )

    def __init__(
        self,
        interaction: "Interaction",
        bot: Any,
        custom_id: str,
        http: "HTTPClient",
    ) -> None:
        self.interaction = interaction
        self.bot = bot
        self.custom_id = custom_id
        self._http = http
        self._modal_data: dict[str, str] = self._extract_modal_data()

    def __repr__(self) -> str:
        return f"<ModalContext custom_id={self.custom_id!r}>"

    def _extract_modal_data(self) -> dict[str, str]:
        result: dict[str, str] = {}
        if self.interaction.data is None:
            return result
        for row in self.interaction.data.components:
            for component in row.get("components", []) if isinstance(row, dict) else getattr(row, "components", []):
                if isinstance(component, dict):
                    cid = component.get("custom_id")
                    val = component.get("value")
                else:
                    cid = getattr(component, "custom_id", None)
                    val = getattr(component, "value", None)
                if cid and val is not None:
                    result[cid] = val
        return result

    @property
    def guild_id(self) -> Optional[int]:
        return self.interaction.guild_id

    @property
    def author(self) -> Optional[Any]:
        return self.interaction.member or self.interaction.user

    def get_value(self, custom_id: str) -> Optional[str]:
        return self._modal_data.get(custom_id)

    async def respond(self, content: Optional[str] = None, **kwargs: Any) -> None:
        await self.interaction.respond(content, **kwargs)

    async def defer(self, *, ephemeral: bool = False) -> None:
        await self.interaction.defer(ephemeral=ephemeral)
