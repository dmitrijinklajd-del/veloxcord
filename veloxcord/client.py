from __future__ import annotations
import asyncio
import logging
import re
import signal
from typing import Any, Callable, Coroutine, Optional, Union

from .http.client import HTTPClient
from .gateway.connection import GatewayConnection
from .gateway.shard import ShardManager
from .events.dispatcher import EventDispatcher, ListenerFunc
from .cache.store import CacheStore, CacheConfig
from .intents import Intents
from .enums import EventType, InteractionType, ApplicationCommandType, ActivityType, Status
from .errors import VeloxException

logger = logging.getLogger("veloxcord.client")


class Client:
    __slots__ = (
        "intents",
        "_http",
        "_gateway",
        "_shard_manager",
        "_dispatcher",
        "_cache",
        "_application_id",
        "_user",
        "_owner_id",
        "_owner_ids",
        "_status",
        "_activity",
        "_slash_commands",
        "_prefix_handler",
        "_component_handlers",
        "_modal_handlers",
        "_ready",
        "_closed",
    )

    def __init__(
        self,
        *,
        intents: Intents,
        cache_config: Optional[CacheConfig] = None,
        shard_ids: Optional[list[int]] = None,
        shard_count: Optional[int] = None,
        owner_id: Optional[int] = None,
        owner_ids: Optional[list[int]] = None,
        prefix: Optional[Union[str, list[str]]] = None,
        case_insensitive: bool = False,
    ) -> None:
        self.intents = intents
        self._http: Optional[HTTPClient] = None
        self._gateway: Optional[GatewayConnection] = None
        self._shard_manager: Optional[ShardManager] = None
        self._dispatcher = EventDispatcher()
        self._cache = CacheStore(cache_config)
        self._application_id: Optional[int] = None
        self._user: Optional[Any] = None
        self._owner_id = owner_id
        self._owner_ids = set(owner_ids or [])
        self._status: str = Status.ONLINE
        self._activity: Optional[dict[str, Any]] = None
        self._slash_commands: dict[str, Any] = {}
        self._component_handlers: dict[str, Callable[..., Coroutine[Any, Any, None]]] = {}
        self._modal_handlers: dict[str, Callable[..., Coroutine[Any, Any, None]]] = {}
        self._ready: asyncio.Event = asyncio.Event()
        self._closed = False

        if prefix is not None:
            from .commands.prefix import PrefixCommandHandler
            self._prefix_handler: Optional[Any] = PrefixCommandHandler(
                prefix, case_insensitive=case_insensitive
            )
        else:
            self._prefix_handler = None

    def __repr__(self) -> str:
        user = self._user
        return f"<Client user={user!r} guilds={len(self._cache.guilds)}>"

    @property
    def user(self) -> Optional[Any]:
        return self._user

    @property
    def application_id(self) -> Optional[int]:
        return self._application_id

    @property
    def latency(self) -> float:
        if self._shard_manager:
            return self._shard_manager.latency
        if self._gateway:
            return self._gateway.latency
        return float("inf")

    @property
    def guilds(self) -> list[Any]:
        return self._cache.guilds.values()

    @property
    def users(self) -> list[Any]:
        return self._cache.users.values()

    @property
    def is_ready(self) -> bool:
        return self._ready.is_set()

    @property
    def is_closed(self) -> bool:
        return self._closed

    @property
    def cache(self) -> CacheStore:
        return self._cache

    def get_guild(self, guild_id: int) -> Optional[Any]:
        return self._cache.get_guild(guild_id)

    def get_channel(self, channel_id: int) -> Optional[Any]:
        return self._cache.get_channel(channel_id)

    def get_user(self, user_id: int) -> Optional[Any]:
        return self._cache.get_user(user_id)

    def get_message(self, message_id: int) -> Optional[Any]:
        return self._cache.get_message(message_id)

    def on(
        self,
        event: Union[str, EventType],
        *,
        priority: int = 0,
    ) -> Callable[[ListenerFunc], ListenerFunc]:
        event_name = str(event)
        return self._dispatcher.on(event_name, priority=priority)

    def once(
        self,
        event: Union[str, EventType],
        *,
        priority: int = 0,
    ) -> Callable[[ListenerFunc], ListenerFunc]:
        event_name = str(event)
        return self._dispatcher.once(event_name, priority=priority)

    def listen(
        self,
        event: Union[str, EventType],
        *,
        priority: int = 0,
    ) -> Callable[[ListenerFunc], ListenerFunc]:
        return self.on(event, priority=priority)

    def add_listener(
        self,
        func: ListenerFunc,
        event: Union[str, EventType],
        *,
        priority: int = 0,
    ) -> None:
        self._dispatcher.register(str(event), func, priority=priority)

    def remove_listener(self, func: ListenerFunc, event: Union[str, EventType]) -> None:
        event_name = str(event)
        for listener in self._dispatcher.listeners_for(event_name):
            if listener.func is func:
                self._dispatcher.unregister(listener)
                break

    def add_middleware(self, middleware: Any) -> None:
        self._dispatcher.add_middleware(middleware)

    def wait_for(
        self,
        event: Union[str, EventType],
        *,
        check: Optional[Callable[..., bool]] = None,
        timeout: Optional[float] = None,
    ) -> asyncio.Future[Any]:
        return self._dispatcher.wait_for(str(event), check=check, timeout=timeout)

    def slash_command(
        self,
        name: Optional[str] = None,
        description: str = "",
        *,
        guild_ids: Optional[list[int]] = None,
        options: Optional[list[Any]] = None,
        default_member_permissions: Optional[int] = None,
        dm_permission: bool = True,
        nsfw: bool = False,
    ) -> Callable[[Callable[..., Coroutine[Any, Any, None]]], Any]:
        def decorator(func: Callable[..., Coroutine[Any, Any, None]]) -> Any:
            from .commands.slash import SlashCommand
            cmd_name = name or func.__name__
            cmd = SlashCommand(
                name=cmd_name,
                callback=func,
                description=description or func.__doc__ or "",
                options=options,
                guild_ids=guild_ids,
                default_member_permissions=default_member_permissions,
                dm_permission=dm_permission,
                nsfw=nsfw,
            )
            self._slash_commands[cmd_name] = cmd
            return cmd
        return decorator

    def user_command(
        self,
        name: Optional[str] = None,
        *,
        guild_ids: Optional[list[int]] = None,
    ) -> Callable[[Callable[..., Coroutine[Any, Any, None]]], Any]:
        def decorator(func: Callable[..., Coroutine[Any, Any, None]]) -> Any:
            from .commands.context_menu import UserCommand
            cmd_name = name or func.__name__
            cmd = UserCommand(name=cmd_name, callback=func, guild_ids=guild_ids)
            self._slash_commands[cmd_name] = cmd
            return cmd
        return decorator

    def message_command(
        self,
        name: Optional[str] = None,
        *,
        guild_ids: Optional[list[int]] = None,
    ) -> Callable[[Callable[..., Coroutine[Any, Any, None]]], Any]:
        def decorator(func: Callable[..., Coroutine[Any, Any, None]]) -> Any:
            from .commands.context_menu import MessageCommand
            cmd_name = name or func.__name__
            cmd = MessageCommand(name=cmd_name, callback=func, guild_ids=guild_ids)
            self._slash_commands[cmd_name] = cmd
            return cmd
        return decorator

    def command(
        self,
        name: Optional[str] = None,
        description: str = "",
        *,
        aliases: Optional[list[str]] = None,
        hidden: bool = False,
    ) -> Callable[[Callable[..., Coroutine[Any, Any, None]]], Any]:
        def decorator(func: Callable[..., Coroutine[Any, Any, None]]) -> Any:
            if self._prefix_handler is None:
                raise RuntimeError("Cannot register prefix commands without a prefix set")
            from .commands.prefix import PrefixCommand
            cmd_name = name or func.__name__
            cmd = PrefixCommand(
                name=cmd_name,
                callback=func,
                description=description or func.__doc__ or "",
                aliases=aliases,
                hidden=hidden,
            )
            self._prefix_handler.add_command(cmd)
            return cmd
        return decorator

    def on_component(
        self,
        custom_id: Optional[str] = None,
        *,
        pattern: Optional[str] = None,
    ) -> Callable[[Callable[..., Coroutine[Any, Any, None]]], Callable[..., Coroutine[Any, Any, None]]]:
        def decorator(
            func: Callable[..., Coroutine[Any, Any, None]]
        ) -> Callable[..., Coroutine[Any, Any, None]]:
            key = pattern or custom_id or func.__name__
            self._component_handlers[key] = func
            return func
        return decorator

    def on_modal(
        self,
        custom_id: Optional[str] = None,
    ) -> Callable[[Callable[..., Coroutine[Any, Any, None]]], Callable[..., Coroutine[Any, Any, None]]]:
        def decorator(
            func: Callable[..., Coroutine[Any, Any, None]]
        ) -> Callable[..., Coroutine[Any, Any, None]]:
            key = custom_id or func.__name__
            self._modal_handlers[key] = func
            return func
        return decorator

    def _presence_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self._status,
            "afk": False,
            "since": None,
            "activities": [],
        }
        if self._activity:
            payload["activities"] = [self._activity]
        return payload

    async def change_presence(
        self,
        *,
        status: str = Status.ONLINE,
        activity_name: Optional[str] = None,
        activity_type: ActivityType = ActivityType.PLAYING,
        activity_url: Optional[str] = None,
    ) -> None:
        self._status = status
        if activity_name:
            self._activity = {
                "name": activity_name,
                "type": activity_type.value,
            }
            if activity_url:
                self._activity["url"] = activity_url
        else:
            self._activity = None

        presence = self._presence_payload()
        if self._shard_manager:
            for shard in self._shard_manager.shards.values():
                await shard.update_presence(presence)
        elif self._gateway:
            await self._gateway.update_presence(presence)

    async def fetch_guild(self, guild_id: int) -> Any:
        from .models.guild import Guild
        data = await self._http.get_guild(guild_id)
        guild = Guild._from_data(data, self._http)
        self._cache.store_guild(guild)
        return guild

    async def fetch_channel(self, channel_id: int) -> Any:
        from .models.channel import _channel_from_data
        data = await self._http.get_channel(channel_id)
        channel = _channel_from_data(data, self._http)
        self._cache.store_channel(channel)
        return channel

    async def fetch_user(self, user_id: int) -> Any:
        from .models.user import User
        cached = self._cache.get_user(user_id)
        if cached:
            return cached
        data = await self._http.get_user(user_id)
        user = User._from_data(data, self._http)
        self._cache.store_user(user)
        return user

    async def sync_commands(
        self,
        *,
        guild_id: Optional[int] = None,
    ) -> list[Any]:
        if self._application_id is None:
            raise RuntimeError("Cannot sync commands before bot is ready")
        guild_commands = []
        global_commands = []
        for cmd in self._slash_commands.values():
            if hasattr(cmd, "guild_ids") and cmd.guild_ids:
                guild_commands.append(cmd)
            else:
                global_commands.append(cmd)

        result = []
        if guild_id is not None:
            all_cmds = [c.to_dict() for c in self._slash_commands.values()]
            result = await self._http.bulk_overwrite_guild_application_commands(
                self._application_id, guild_id, all_cmds
            )
        else:
            if global_commands:
                global_payloads = [c.to_dict() for c in global_commands]
                result += await self._http.bulk_overwrite_global_application_commands(
                    self._application_id, global_payloads
                )
            for cmd in guild_commands:
                for gid in cmd.guild_ids:
                    guild_result = await self._http.bulk_overwrite_guild_application_commands(
                        self._application_id,
                        gid,
                        [cmd.to_dict()],
                    )
                    result += guild_result
        return result

    async def _handle_event(self, event_name: Optional[str], data: dict[str, Any]) -> None:
        if event_name is None:
            return
        try:
            processor = getattr(self, f"_process_{event_name.lower()}", None)
            if processor:
                obj = await processor(data)
                if obj is not None:
                    await self._dispatcher.dispatch(event_name, obj)
            else:
                await self._dispatcher.dispatch(event_name, data)
        except Exception as exc:
            logger.exception(f"Error processing event {event_name!r}: {exc}")
            await self._dispatcher.dispatch("ERROR", exc)

    async def _process_ready(self, data: dict[str, Any]) -> Any:
        from .models.user import User
        user_data = data.get("user", {})
        self._user = User._from_data(user_data, self._http)
        self._application_id = int(data["application"]["id"]) if data.get("application") else None
        if self._gateway:
            self._gateway.session_id = data.get("session_id")
            self._gateway.resume_url = data.get("resume_gateway_url")
        for guild_data in data.get("guilds", []):
            from .models.guild import Guild
            if not guild_data.get("unavailable", False):
                guild = Guild._from_data(guild_data, self._http)
                self._cache.store_guild(guild)
        self._ready.set()
        logger.info(f"Ready! Logged in as {self._user.tag} (id={self._user.id})")
        return self._user

    async def _process_guild_create(self, data: dict[str, Any]) -> Any:
        from .models.guild import Guild
        guild = Guild._from_data(data, self._http)
        self._cache.store_guild(guild)
        for channel in guild.channels:
            self._cache.store_channel(channel)
        for member in guild.members:
            self._cache.store_member(member)
        for role in guild.roles:
            self._cache.store_role(role)
        for emoji in guild.emojis:
            self._cache.store_emoji(emoji)
        return guild

    async def _process_guild_update(self, data: dict[str, Any]) -> Any:
        from .models.guild import Guild
        guild = Guild._from_data(data, self._http)
        self._cache.store_guild(guild)
        return guild

    async def _process_guild_delete(self, data: dict[str, Any]) -> Any:
        guild_id = int(data["id"])
        guild = self._cache.get_guild(guild_id)
        self._cache.delete_guild(guild_id)
        return guild or data

    async def _process_channel_create(self, data: dict[str, Any]) -> Any:
        from .models.channel import _channel_from_data
        channel = _channel_from_data(data, self._http)
        self._cache.store_channel(channel)
        return channel

    async def _process_channel_update(self, data: dict[str, Any]) -> Any:
        from .models.channel import _channel_from_data
        channel = _channel_from_data(data, self._http)
        self._cache.store_channel(channel)
        return channel

    async def _process_channel_delete(self, data: dict[str, Any]) -> Any:
        from .models.channel import _channel_from_data
        channel_id = int(data["id"])
        cached = self._cache.get_channel(channel_id)
        self._cache.delete_channel(channel_id)
        return cached or _channel_from_data(data, self._http)

    async def _process_message_create(self, data: dict[str, Any]) -> Any:
        from .models.message import Message
        message = Message._from_data(data, self._http)
        channel = self._cache.get_channel(message.channel_id)
        if channel:
            message.channel = channel
        self._cache.store_message(message)
        if self._prefix_handler:
            await self._prefix_handler.process(message, self, self._http)
        return message

    async def _process_message_update(self, data: dict[str, Any]) -> Any:
        from .models.message import Message
        message = Message._from_data(data, self._http)
        self._cache.store_message(message)
        return message

    async def _process_message_delete(self, data: dict[str, Any]) -> Any:
        message_id = int(data["id"])
        cached = self._cache.get_message(message_id)
        self._cache.delete_message(message_id)
        if cached:
            return cached
        return data

    async def _process_guild_member_add(self, data: dict[str, Any]) -> Any:
        from .models.member import Member
        guild_id = int(data["guild_id"]) if data.get("guild_id") else 0
        member = Member._from_data(data, self._http, guild_id)
        self._cache.store_member(member)
        guild = self._cache.get_guild(guild_id)
        if guild:
            guild._members[member.id] = member
            guild.member_count += 1
        return member

    async def _process_guild_member_remove(self, data: dict[str, Any]) -> Any:
        from .models.user import User
        guild_id = int(data["guild_id"]) if data.get("guild_id") else 0
        user_data = data.get("user", {})
        user = User._from_data(user_data, self._http)
        cached_member = self._cache.get_member(guild_id, user.id)
        self._cache.delete_member(guild_id, user.id)
        guild = self._cache.get_guild(guild_id)
        if guild:
            guild._members.pop(user.id, None)
            guild.member_count = max(0, guild.member_count - 1)
        return cached_member or user

    async def _process_guild_member_update(self, data: dict[str, Any]) -> Any:
        from .models.member import Member
        guild_id = int(data["guild_id"]) if data.get("guild_id") else 0
        member = Member._from_data(data, self._http, guild_id)
        self._cache.store_member(member)
        guild = self._cache.get_guild(guild_id)
        if guild:
            guild._members[member.id] = member
        return member

    async def _process_guild_role_create(self, data: dict[str, Any]) -> Any:
        from .models.role import Role
        guild_id = int(data["guild_id"]) if data.get("guild_id") else 0
        role = Role._from_data(data.get("role", data), self._http, guild_id)
        self._cache.store_role(role)
        guild = self._cache.get_guild(guild_id)
        if guild:
            guild._roles[role.id] = role
        return role

    async def _process_guild_role_update(self, data: dict[str, Any]) -> Any:
        from .models.role import Role
        guild_id = int(data["guild_id"]) if data.get("guild_id") else 0
        role = Role._from_data(data.get("role", data), self._http, guild_id)
        self._cache.store_role(role)
        guild = self._cache.get_guild(guild_id)
        if guild:
            guild._roles[role.id] = role
        return role

    async def _process_guild_role_delete(self, data: dict[str, Any]) -> Any:
        guild_id = int(data["guild_id"]) if data.get("guild_id") else 0
        role_id = int(data["role_id"]) if data.get("role_id") else 0
        cached = self._cache.get_role(role_id)
        self._cache.delete_role(role_id)
        guild = self._cache.get_guild(guild_id)
        if guild:
            guild._roles.pop(role_id, None)
        return cached or data

    async def _process_guild_emojis_update(self, data: dict[str, Any]) -> Any:
        from .models.emoji import Emoji
        guild_id = int(data["guild_id"]) if data.get("guild_id") else 0
        emojis = [Emoji._from_data(e, self._http, guild_id) for e in data.get("emojis", [])]
        guild = self._cache.get_guild(guild_id)
        if guild:
            guild._emojis = {e.id: e for e in emojis}
        for emoji in emojis:
            self._cache.store_emoji(emoji)
        return emojis

    async def _process_interaction_create(self, data: dict[str, Any]) -> Any:
        from .models.interaction import Interaction
        from .commands.context import SlashContext, ComponentContext, ModalContext

        interaction = Interaction._from_data(data, self._http)
        await self._dispatcher.dispatch(EventType.INTERACTION_CREATE, interaction)

        match interaction.type:
            case InteractionType.APPLICATION_COMMAND:
                await self._dispatch_application_command(interaction)
            case InteractionType.MESSAGE_COMPONENT:
                await self._dispatch_component(interaction)
            case InteractionType.MODAL_SUBMIT:
                await self._dispatch_modal(interaction)
            case InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE:
                await self._dispatch_autocomplete(interaction)
            case _:
                pass

        return None

    async def _dispatch_application_command(self, interaction: Any) -> None:
        from .commands.context import SlashContext
        if interaction.data is None:
            return
        name = interaction.data.name
        cmd = self._slash_commands.get(name)
        if cmd is None:
            return
        ctx = SlashContext(interaction=interaction, bot=self, command_name=name, http=self._http)

        async def _auto_defer() -> None:
            await asyncio.sleep(2.0)
            if not interaction._responded and not interaction._deferred:
                try:
                    await interaction.defer()
                except Exception:
                    pass

        defer_task = asyncio.create_task(_auto_defer(), name=f"veloxcord-defer-{interaction.id}")
        try:
            await cmd.invoke(ctx)
        except Exception as exc:
            logger.exception(f"Error in slash command {name!r}: {exc}")
            await self._dispatcher.dispatch("COMMAND_ERROR", exc, ctx)
        finally:
            defer_task.cancel()

    async def _dispatch_component(self, interaction: Any) -> None:
        from .commands.context import ComponentContext
        if interaction.data is None:
            return
        custom_id = interaction.data.custom_id or ""
        handler = self._find_component_handler(custom_id)
        if handler is None:
            return
        ctx = ComponentContext(interaction=interaction, bot=self, custom_id=custom_id, http=self._http)
        try:
            await handler(ctx)
        except Exception as exc:
            logger.exception(f"Error in component handler {custom_id!r}: {exc}")

    async def _dispatch_modal(self, interaction: Any) -> None:
        from .commands.context import ModalContext
        if interaction.data is None:
            return
        custom_id = interaction.data.custom_id or ""
        handler = self._modal_handlers.get(custom_id)
        if handler is None:
            return
        ctx = ModalContext(interaction=interaction, bot=self, custom_id=custom_id, http=self._http)
        try:
            await handler(ctx)
        except Exception as exc:
            logger.exception(f"Error in modal handler {custom_id!r}: {exc}")

    async def _dispatch_autocomplete(self, interaction: Any) -> None:
        if interaction.data is None:
            return
        name = interaction.data.name
        cmd = self._slash_commands.get(name)
        if cmd is None or not hasattr(cmd, "_autocomplete_handlers"):
            return
        focused_option = next(
            (o for o in interaction.data.options if isinstance(o, dict) and o.get("focused")),
            None,
        )
        if focused_option is None:
            return
        option_name = focused_option.get("name", "")
        current_value = str(focused_option.get("value", ""))
        handler = cmd._autocomplete_handlers.get(option_name)
        if handler is None:
            return
        from .commands.context import SlashContext
        ctx = SlashContext(interaction=interaction, bot=self, command_name=name, http=self._http)
        try:
            choices = await handler(ctx, current_value)
            if choices:
                from .enums import InteractionCallbackType
                payload = {
                    "type": InteractionCallbackType.APPLICATION_COMMAND_AUTOCOMPLETE_RESULT.value,
                    "data": {"choices": choices},
                }
                await self._http.create_interaction_response(interaction.id, interaction.token, payload)
        except Exception as exc:
            logger.exception(f"Error in autocomplete handler: {exc}")

    def _find_component_handler(
        self, custom_id: str
    ) -> Optional[Callable[..., Coroutine[Any, Any, None]]]:
        if custom_id in self._component_handlers:
            return self._component_handlers[custom_id]
        for pattern, handler in self._component_handlers.items():
            try:
                if re.fullmatch(pattern, custom_id):
                    return handler
            except re.error:
                pass
        return None

    async def _start(self, token: str) -> None:
        self._http = HTTPClient(token)
        gateway_data = await self._http.get_gateway_bot()
        gateway_url = gateway_data.get("url", "wss://gateway.discord.gg")
        recommended_shards = gateway_data.get("shards", 1)
        session_start_limit = gateway_data.get("session_start_limit", {})
        max_concurrency = session_start_limit.get("max_concurrency", 1)

        logger.info(f"Gateway URL: {gateway_url}, recommended shards: {recommended_shards}")

        shard_count = recommended_shards
        self._gateway = GatewayConnection(self, 0, shard_count)

        if shard_count > 1:
            self._shard_manager = ShardManager(self, shard_count, max_concurrency)
            for shard_id in range(shard_count):
                shard = GatewayConnection(self, shard_id, shard_count)
                self._shard_manager._shards[shard_id] = shard
            tasks = [
                asyncio.create_task(shard.connect(), name=f"veloxcord-shard-{sid}")
                for sid, shard in self._shard_manager._shards.items()
            ]
            await asyncio.gather(*tasks)
        else:
            await self._gateway.connect()

    async def close(self) -> None:
        self._closed = True
        if self._shard_manager:
            await self._shard_manager.disconnect_all()
        elif self._gateway:
            await self._gateway.disconnect()
        if self._http:
            await self._http.close()
        logger.info("Client closed")

    def run(self, token: str, *, log_level: int = logging.INFO) -> None:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

        async def _runner() -> None:
            try:
                await self._start(token)
            except KeyboardInterrupt:
                pass
            finally:
                if not self._closed:
                    await self.close()

        try:
            asyncio.run(_runner())
        except KeyboardInterrupt:
            pass

    async def start(self, token: str) -> None:
        await self._start(token)
