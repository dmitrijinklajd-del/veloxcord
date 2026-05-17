from __future__ import annotations
import shlex
from typing import Any, Callable, Coroutine, Optional, Union

from .core import BaseCommand
from .cooldown import Cooldown
from .context import PrefixContext
from ..errors import CommandNotFound


class PrefixCommand(BaseCommand):
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
        "usage",
        "hidden",
        "enabled",
    )

    def __init__(
        self,
        name: str,
        callback: Callable[..., Coroutine[Any, Any, None]],
        *,
        description: str = "",
        aliases: Optional[list[str]] = None,
        usage: Optional[str] = None,
        hidden: bool = False,
        enabled: bool = True,
        cooldown: Optional[Cooldown] = None,
        checks: Optional[list[Callable[..., bool]]] = None,
    ) -> None:
        super().__init__(
            name=name,
            callback=callback,
            description=description,
            aliases=aliases,
            cooldown=cooldown,
            checks=checks,
        )
        self.usage = usage
        self.hidden = hidden
        self.enabled = enabled

    async def invoke(self, ctx: "PrefixContext", *args: Any, **kwargs: Any) -> None:
        if not self.enabled:
            return
        await super().invoke(ctx, *args, **kwargs)


class PrefixCommandHandler:
    __slots__ = (
        "_commands",
        "_aliases",
        "_prefixes",
        "_case_insensitive",
    )

    def __init__(
        self,
        prefixes: Union[str, list[str]],
        *,
        case_insensitive: bool = False,
    ) -> None:
        self._commands: dict[str, PrefixCommand] = {}
        self._aliases: dict[str, str] = {}
        self._prefixes: list[str] = [prefixes] if isinstance(prefixes, str) else list(prefixes)
        self._case_insensitive = case_insensitive

    def __repr__(self) -> str:
        return f"<PrefixCommandHandler commands={len(self._commands)} prefixes={self._prefixes!r}>"

    def add_command(self, command: PrefixCommand) -> None:
        name = command.name.lower() if self._case_insensitive else command.name
        self._commands[name] = command
        for alias in command.aliases:
            alias_key = alias.lower() if self._case_insensitive else alias
            self._aliases[alias_key] = name

    def remove_command(self, name: str) -> Optional[PrefixCommand]:
        key = name.lower() if self._case_insensitive else name
        command = self._commands.pop(key, None)
        if command:
            for alias in command.aliases:
                alias_key = alias.lower() if self._case_insensitive else alias
                self._aliases.pop(alias_key, None)
        return command

    def get_command(self, name: str) -> Optional[PrefixCommand]:
        key = name.lower() if self._case_insensitive else name
        if key in self._commands:
            return self._commands[key]
        canonical = self._aliases.get(key)
        if canonical:
            return self._commands.get(canonical)
        return None

    def get_all_commands(self) -> list[PrefixCommand]:
        return list(self._commands.values())

    def extract_prefix(self, content: str) -> Optional[str]:
        for prefix in self._prefixes:
            if content.startswith(prefix):
                return prefix
        return None

    def parse_invocation(self, content: str, prefix: str) -> Optional[tuple[str, list[str]]]:
        without_prefix = content[len(prefix):].strip()
        if not without_prefix:
            return None
        try:
            parts = shlex.split(without_prefix)
        except ValueError:
            parts = without_prefix.split()
        if not parts:
            return None
        command_name = parts[0]
        args = parts[1:]
        return command_name, args

    async def process(self, message: Any, bot: Any, http: Any) -> bool:
        content = getattr(message, "content", "")
        if not content:
            return False
        prefix = self.extract_prefix(content)
        if prefix is None:
            return False
        parsed = self.parse_invocation(content, prefix)
        if parsed is None:
            return False
        command_name, args = parsed
        command = self.get_command(command_name)
        if command is None:
            return False
        ctx = PrefixContext(
            message=message,
            bot=bot,
            prefix=prefix,
            command_name=command_name,
            args=args,
            kwargs={},
            http=http,
        )
        await command.invoke(ctx, *args)
        return True
