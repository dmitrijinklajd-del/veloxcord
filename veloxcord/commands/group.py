from __future__ import annotations
from typing import Any, Callable, Coroutine, Optional

from .slash import SlashCommand, SlashCommandOption
from ..enums import ApplicationCommandOptionType, ApplicationCommandType


class SubCommand:
    __slots__ = ("name", "description", "callback", "options", "cog", "parent")

    def __init__(
        self,
        name: str,
        description: str,
        callback: Callable[..., Coroutine[Any, Any, None]],
        options: Optional[list[SlashCommandOption]] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.callback = callback
        self.options: list[SlashCommandOption] = options or []
        self.cog: Optional[Any] = None
        self.parent: Optional[Any] = None

    def __repr__(self) -> str:
        return f"<SubCommand name={self.name!r}>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description or "No description",
            "type": ApplicationCommandOptionType.SUB_COMMAND.value,
            "options": [o.to_dict() for o in self.options],
        }

    async def invoke(self, ctx: Any, *args: Any, **kwargs: Any) -> None:
        if self.cog is not None:
            await self.callback(self.cog, ctx, *args, **kwargs)
        else:
            await self.callback(ctx, *args, **kwargs)


class SubCommandGroup:
    __slots__ = ("name", "description", "subcommands", "cog", "parent")

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self.subcommands: dict[str, SubCommand] = {}
        self.cog: Optional[Any] = None
        self.parent: Optional[Any] = None

    def __repr__(self) -> str:
        return f"<SubCommandGroup name={self.name!r} subcommands={len(self.subcommands)}>"

    def sub_command(
        self,
        name: Optional[str] = None,
        description: str = "",
        options: Optional[list[SlashCommandOption]] = None,
    ) -> Callable[[Callable[..., Coroutine[Any, Any, None]]], SubCommand]:
        def decorator(func: Callable[..., Coroutine[Any, Any, None]]) -> SubCommand:
            cmd_name = name or func.__name__
            sub = SubCommand(cmd_name, description or func.__doc__ or "", func, options)
            sub.parent = self
            self.subcommands[cmd_name] = sub
            return sub
        return decorator

    def get_subcommand(self, name: str) -> Optional[SubCommand]:
        return self.subcommands.get(name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description or "No description",
            "type": ApplicationCommandOptionType.SUB_COMMAND_GROUP.value,
            "options": [sc.to_dict() for sc in self.subcommands.values()],
        }


class SlashCommandGroup(SlashCommand):
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
        "subcommands",
        "subcommand_groups",
    )

    def __init__(
        self,
        name: str,
        description: str = "",
        *,
        guild_ids: Optional[list[int]] = None,
        default_member_permissions: Optional[int] = None,
        dm_permission: bool = True,
    ) -> None:
        async def _placeholder(ctx: Any) -> None:
            pass

        super().__init__(
            name=name,
            callback=_placeholder,
            description=description,
            options=[],
            guild_ids=guild_ids,
            default_member_permissions=default_member_permissions,
            dm_permission=dm_permission,
        )
        self.subcommands: dict[str, SubCommand] = {}
        self.subcommand_groups: dict[str, SubCommandGroup] = {}

    def sub_command(
        self,
        name: Optional[str] = None,
        description: str = "",
        options: Optional[list[SlashCommandOption]] = None,
    ) -> Callable[[Callable[..., Coroutine[Any, Any, None]]], SubCommand]:
        def decorator(func: Callable[..., Coroutine[Any, Any, None]]) -> SubCommand:
            cmd_name = name or func.__name__
            sub = SubCommand(cmd_name, description or func.__doc__ or "", func, options)
            sub.parent = self
            self.subcommands[cmd_name] = sub
            return sub
        return decorator

    def sub_command_group(
        self,
        name: str,
        description: str = "",
    ) -> SubCommandGroup:
        group = SubCommandGroup(name, description)
        group.parent = self
        self.subcommand_groups[name] = group
        return group

    def get_subcommand(self, name: str) -> Optional[SubCommand]:
        return self.subcommands.get(name)

    def get_subcommand_group(self, name: str) -> Optional[SubCommandGroup]:
        return self.subcommand_groups.get(name)

    def to_dict(self) -> dict[str, Any]:
        options: list[dict[str, Any]] = []
        for sub in self.subcommands.values():
            options.append(sub.to_dict())
        for group in self.subcommand_groups.values():
            options.append(group.to_dict())
        payload: dict[str, Any] = {
            "name": self.name,
            "description": self.description or "No description",
            "type": ApplicationCommandType.CHAT_INPUT.value,
            "options": options,
            "dm_permission": self.dm_permission,
        }
        if self.default_member_permissions is not None:
            payload["default_member_permissions"] = str(self.default_member_permissions)
        return payload

    async def invoke(self, ctx: Any, *args: Any, **kwargs: Any) -> None:
        if ctx.data is None:
            return
        options = ctx.data.options
        if not options:
            return
        first = options[0]
        sub_name = first.get("name") if isinstance(first, dict) else getattr(first, "name", None)
        sub_type = first.get("type") if isinstance(first, dict) else getattr(first, "type", None)

        if sub_type == ApplicationCommandOptionType.SUB_COMMAND_GROUP.value:
            group = self.subcommand_groups.get(sub_name)
            if group is None:
                return
            nested_options = first.get("options", []) if isinstance(first, dict) else getattr(first, "options", [])
            if not nested_options:
                return
            nested_first = nested_options[0]
            nested_name = nested_first.get("name") if isinstance(nested_first, dict) else getattr(nested_first, "name", None)
            sub = group.get_subcommand(nested_name)
            if sub is None:
                return
            await sub.invoke(ctx)
        else:
            sub = self.subcommands.get(sub_name)
            if sub is None:
                return
            await sub.invoke(ctx)
