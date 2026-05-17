from __future__ import annotations
from typing import Any, Callable, Optional, TypeVar

from .lru import LRUCache

T = TypeVar("T")


class CacheConfig:
    __slots__ = (
        "guild_max_size",
        "channel_max_size",
        "member_max_size",
        "message_max_size",
        "user_max_size",
        "role_max_size",
        "emoji_max_size",
        "guild_ttl",
        "channel_ttl",
        "member_ttl",
        "message_ttl",
        "user_ttl",
        "role_ttl",
        "emoji_ttl",
        "disable_guild_cache",
        "disable_channel_cache",
        "disable_member_cache",
        "disable_message_cache",
        "disable_user_cache",
        "disable_role_cache",
        "disable_emoji_cache",
    )

    def __init__(
        self,
        guild_max_size: int = 1024,
        channel_max_size: int = 4096,
        member_max_size: int = 65536,
        message_max_size: int = 1024,
        user_max_size: int = 65536,
        role_max_size: int = 4096,
        emoji_max_size: int = 4096,
        guild_ttl: Optional[float] = None,
        channel_ttl: Optional[float] = None,
        member_ttl: Optional[float] = 3600.0,
        message_ttl: Optional[float] = 1800.0,
        user_ttl: Optional[float] = 3600.0,
        role_ttl: Optional[float] = None,
        emoji_ttl: Optional[float] = None,
        disable_guild_cache: bool = False,
        disable_channel_cache: bool = False,
        disable_member_cache: bool = False,
        disable_message_cache: bool = False,
        disable_user_cache: bool = False,
        disable_role_cache: bool = False,
        disable_emoji_cache: bool = False,
    ) -> None:
        self.guild_max_size = guild_max_size
        self.channel_max_size = channel_max_size
        self.member_max_size = member_max_size
        self.message_max_size = message_max_size
        self.user_max_size = user_max_size
        self.role_max_size = role_max_size
        self.emoji_max_size = emoji_max_size
        self.guild_ttl = guild_ttl
        self.channel_ttl = channel_ttl
        self.member_ttl = member_ttl
        self.message_ttl = message_ttl
        self.user_ttl = user_ttl
        self.role_ttl = role_ttl
        self.emoji_ttl = emoji_ttl
        self.disable_guild_cache = disable_guild_cache
        self.disable_channel_cache = disable_channel_cache
        self.disable_member_cache = disable_member_cache
        self.disable_message_cache = disable_message_cache
        self.disable_user_cache = disable_user_cache
        self.disable_role_cache = disable_role_cache
        self.disable_emoji_cache = disable_emoji_cache


class CacheStore:
    __slots__ = (
        "config",
        "guilds",
        "channels",
        "members",
        "messages",
        "users",
        "roles",
        "emojis",
        "_guild_members",
        "_guild_channels",
        "_guild_roles",
        "_guild_emojis",
    )

    def __init__(self, config: Optional[CacheConfig] = None) -> None:
        self.config = config or CacheConfig()
        self.guilds: LRUCache[int, Any] = LRUCache(
            self.config.guild_max_size, self.config.guild_ttl
        )
        self.channels: LRUCache[int, Any] = LRUCache(
            self.config.channel_max_size, self.config.channel_ttl
        )
        self.members: LRUCache[tuple[int, int], Any] = LRUCache(
            self.config.member_max_size, self.config.member_ttl
        )
        self.messages: LRUCache[int, Any] = LRUCache(
            self.config.message_max_size, self.config.message_ttl
        )
        self.users: LRUCache[int, Any] = LRUCache(
            self.config.user_max_size, self.config.user_ttl
        )
        self.roles: LRUCache[int, Any] = LRUCache(
            self.config.role_max_size, self.config.role_ttl
        )
        self.emojis: LRUCache[int, Any] = LRUCache(
            self.config.emoji_max_size, self.config.emoji_ttl
        )
        self._guild_members: dict[int, set[int]] = {}
        self._guild_channels: dict[int, set[int]] = {}
        self._guild_roles: dict[int, set[int]] = {}
        self._guild_emojis: dict[int, set[int]] = {}

    def store_guild(self, guild: Any) -> None:
        if self.config.disable_guild_cache:
            return
        self.guilds.set(guild.id, guild)

    def get_guild(self, guild_id: int) -> Optional[Any]:
        if self.config.disable_guild_cache:
            return None
        return self.guilds.get(guild_id)

    def delete_guild(self, guild_id: int) -> None:
        self.guilds.delete(guild_id)
        for member_id in self._guild_members.pop(guild_id, set()):
            self.members.delete((guild_id, member_id))
        for channel_id in self._guild_channels.pop(guild_id, set()):
            self.channels.delete(channel_id)
        for role_id in self._guild_roles.pop(guild_id, set()):
            self.roles.delete(role_id)
        for emoji_id in self._guild_emojis.pop(guild_id, set()):
            self.emojis.delete(emoji_id)

    def store_channel(self, channel: Any) -> None:
        if self.config.disable_channel_cache:
            return
        self.channels.set(channel.id, channel)
        guild_id = getattr(channel, "guild_id", None)
        if guild_id:
            self._guild_channels.setdefault(guild_id, set()).add(channel.id)

    def get_channel(self, channel_id: int) -> Optional[Any]:
        if self.config.disable_channel_cache:
            return None
        return self.channels.get(channel_id)

    def delete_channel(self, channel_id: int) -> None:
        channel = self.channels.get(channel_id)
        if channel:
            guild_id = getattr(channel, "guild_id", None)
            if guild_id:
                self._guild_channels.get(guild_id, set()).discard(channel_id)
        self.channels.delete(channel_id)

    def store_member(self, member: Any) -> None:
        if self.config.disable_member_cache:
            return
        key = (member.guild_id, member.id)
        self.members.set(key, member)
        self._guild_members.setdefault(member.guild_id, set()).add(member.id)
        self.store_user(member.user)

    def get_member(self, guild_id: int, user_id: int) -> Optional[Any]:
        if self.config.disable_member_cache:
            return None
        return self.members.get((guild_id, user_id))

    def delete_member(self, guild_id: int, user_id: int) -> None:
        self.members.delete((guild_id, user_id))
        self._guild_members.get(guild_id, set()).discard(user_id)

    def get_guild_members(self, guild_id: int) -> list[Any]:
        if self.config.disable_member_cache:
            return []
        member_ids = self._guild_members.get(guild_id, set())
        result = []
        for uid in member_ids:
            m = self.members.get((guild_id, uid))
            if m is not None:
                result.append(m)
        return result

    def store_message(self, message: Any) -> None:
        if self.config.disable_message_cache:
            return
        self.messages.set(message.id, message)

    def get_message(self, message_id: int) -> Optional[Any]:
        if self.config.disable_message_cache:
            return None
        return self.messages.get(message_id)

    def delete_message(self, message_id: int) -> None:
        self.messages.delete(message_id)

    def store_user(self, user: Any) -> None:
        if self.config.disable_user_cache:
            return
        self.users.set(user.id, user)

    def get_user(self, user_id: int) -> Optional[Any]:
        if self.config.disable_user_cache:
            return None
        return self.users.get(user_id)

    def store_role(self, role: Any) -> None:
        if self.config.disable_role_cache:
            return
        self.roles.set(role.id, role)
        self._guild_roles.setdefault(role.guild_id, set()).add(role.id)

    def get_role(self, role_id: int) -> Optional[Any]:
        if self.config.disable_role_cache:
            return None
        return self.roles.get(role_id)

    def delete_role(self, role_id: int) -> None:
        role = self.roles.get(role_id)
        if role:
            self._guild_roles.get(role.guild_id, set()).discard(role_id)
        self.roles.delete(role_id)

    def store_emoji(self, emoji: Any) -> None:
        if self.config.disable_emoji_cache:
            return
        if emoji.id:
            self.emojis.set(emoji.id, emoji)
            self._guild_emojis.setdefault(emoji.guild_id, set()).add(emoji.id)

    def get_emoji(self, emoji_id: int) -> Optional[Any]:
        if self.config.disable_emoji_cache:
            return None
        return self.emojis.get(emoji_id)

    def clear(self) -> None:
        self.guilds.clear()
        self.channels.clear()
        self.members.clear()
        self.messages.clear()
        self.users.clear()
        self.roles.clear()
        self.emojis.clear()
        self._guild_members.clear()
        self._guild_channels.clear()
        self._guild_roles.clear()
        self._guild_emojis.clear()

    def stats(self) -> dict[str, int]:
        return {
            "guilds": len(self.guilds),
            "channels": len(self.channels),
            "members": len(self.members),
            "messages": len(self.messages),
            "users": len(self.users),
            "roles": len(self.roles),
            "emojis": len(self.emojis),
        }
