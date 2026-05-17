from __future__ import annotations
import inspect
from typing import Any, Callable, Coroutine, Optional, get_type_hints

from .core import BaseCommand
from .cooldown import Cooldown
from ..enums import ApplicationCommandType, ApplicationCommandOptionType


_TYPE_MAP: dict[type, ApplicationCommandOptionType] = {
    str: ApplicationCommandOptionType.STRING,
    int: ApplicationCommandOptionType.INTEGER,
    float: ApplicationCommandOptionType.NUMBER,
    bool: ApplicationCommandOptionType.BOOLEAN,
}


def _infer_option_type(annotation: Any) -> ApplicationCommandOptionType:
    origin = getattr(annotation, "__origin__", None)
    if origin is not None:
        args = getattr(annotation, "__args__", ())
        if args:
            annotation = args[0]
    return _TYPE_MAP.get(annotation, ApplicationCommandOptionType.STRING)


class SlashCommandOption:
    __slots__ = (
        "name",
        "description",
        "type",
        "required",
        "choices",
        "autocomplete",
        "min_value",
        "max_value",
        "min_length",
        "max_length",
        "channel_types",
    )

    def __init__(
        self,
        name: str,
        description: str,
        type: ApplicationCommandOptionType,
        required: bool = True,
        choices: Optional[list[dict[str, Any]]] = None,
        autocomplete: bool = False,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        channel_types: Optional[list[int]] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.type = type
        self.required = required
        self.choices = choices or []
        self.autocomplete = autocomplete
        self.min_value = min_value
        self.max_value = max_value
        self.min_length = min_length
        self.max_length = max_length
        self.channel_types = channel_types or []

    def __repr__(self) -> str:
        return f"<SlashCommandOption name={self.name!r} type={self.type}>"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "description": self.description or "No description",
            "type": self.type.value,
            "required": self.required,
        }
        if self.choices:
            payload["choices"] = self.choices
        if self.autocomplete:
            payload["autocomplete"] = self.autocomplete
        if self.min_value is not None:
            payload["min_value"] = self.min_value
        if self.max_value is not None:
            payload["max_value"] = self.max_value
        if self.min_length is not None:
            payload["min_length"] = self.min_length
        if self.max_length is not None:
            payload["max_length"] = self.max_length
        if self.channel_types:
            payload["channel_types"] = self.channel_types
        return payload


class SlashCommand(BaseCommand):
    __slots__ = (
        "name",
        "callback",
        "description",
        "aliases",
        "checks",
        "cooldown",
        "guild_ids",
        "required_permissions",
        "required_bot_permissions",
        "parent",
        "cog",
        "options",
        "default_member_permissions",
        "dm_permission",
        "nsfw",
        "_autocomplete_handlers",
    )

    def __init__(
        self,
        name: str,
        callback: Callable[..., Coroutine[Any, Any, None]],
        *,
        description: str = "",
        options: Optional[list[SlashCommandOption]] = None,
        guild_ids: Optional[list[int]] = None,
        default_member_permissions: Optional[int] = None,
        dm_permission: bool = True,
        nsfw: bool = False,
        cooldown: Optional[Cooldown] = None,
        checks: Optional[list[Callable[..., bool]]] = None,
    ) -> None:
        super().__init__(
            name=name,
            callback=callback,
            description=description,
            guild_ids=guild_ids,
            cooldown=cooldown,
            checks=checks,
        )
        self.options: list[SlashCommandOption] = options or self._infer_options(callback)
        self.default_member_permissions = default_member_permissions
        self.dm_permission = dm_permission
        self.nsfw = nsfw
        self._autocomplete_handlers: dict[str, Callable[..., Coroutine[Any, Any, None]]] = {}

    def _infer_options(
        self, callback: Callable[..., Coroutine[Any, Any, None]]
    ) -> list[SlashCommandOption]:
        sig = inspect.signature(callback)
        options: list[SlashCommandOption] = []
        params = list(sig.parameters.values())
        skip = 1
        if params and params[0].name == "self":
            skip += 1
        for param in params[skip:]:
            annotation = param.annotation
            if annotation is inspect.Parameter.empty:
                annotation = str
            opt_type = _infer_option_type(annotation)
            required = param.default is inspect.Parameter.empty
            options.append(
                SlashCommandOption(
                    name=param.name,
                    description=param.name.replace("_", " ").title(),
                    type=opt_type,
                    required=required,
                )
            )
        return options

    def autocomplete(
        self, option_name: str
    ) -> Callable[[Callable[..., Coroutine[Any, Any, None]]], Callable[..., Coroutine[Any, Any, None]]]:
        def decorator(
            func: Callable[..., Coroutine[Any, Any, None]]
        ) -> Callable[..., Coroutine[Any, Any, None]]:
            self._autocomplete_handlers[option_name] = func
            for opt in self.options:
                if opt.name == option_name:
                    opt.autocomplete = True
                    break
            return func
        return decorator

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "description": self.description or "No description",
            "type": ApplicationCommandType.CHAT_INPUT.value,
            "options": [o.to_dict() for o in self.options],
            "dm_permission": self.dm_permission,
            "nsfw": self.nsfw,
        }
        if self.default_member_permissions is not None:
            payload["default_member_permissions"] = str(self.default_member_permissions)
        return payload

    async def invoke_autocomplete(
        self, ctx: Any, option_name: str, current_value: str
    ) -> list[dict[str, Any]]:
        handler = self._autocomplete_handlers.get(option_name)
        if handler is None:
            return []
        result = await handler(ctx, current_value)
        return result or []
