from __future__ import annotations
import datetime
from typing import TYPE_CHECKING, Any, Optional

from .base import DiscordModel
from ..enums import (
    VerificationLevel,
    DefaultMessageNotificationLevel,
    ExplicitContentFilterLevel,
    MFALevel,
    PremiumTier,
    NSFWLevel,
)
from ..flags import SystemChannelFlags
from ..utils import parse_timestamp, MISSING

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from .channel import TextChannel, VoiceChannel
    from .member import Member
    from .role import Role
    from .emoji import Emoji
    from .sticker import Sticker


class WelcomeScreenChannel:
    __slots__ = ("channel_id", "description", "emoji_id", "emoji_name")

    def __init__(
        self,
        channel_id: int,
        description: str,
        emoji_id: Optional[int],
        emoji_name: Optional[str],
    ) -> None:
        self.channel_id = channel_id
        self.description = description
        self.emoji_id = emoji_id
        self.emoji_name = emoji_name

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "WelcomeScreenChannel":
        return cls(
            channel_id=int(data["channel_id"]),
            description=data["description"],
            emoji_id=int(data["emoji_id"]) if data.get("emoji_id") else None,
            emoji_name=data.get("emoji_name"),
        )


class WelcomeScreen:
    __slots__ = ("description", "welcome_channels")

    def __init__(self, description: Optional[str], welcome_channels: list[WelcomeScreenChannel]) -> None:
        self.description = description
        self.welcome_channels = welcome_channels

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "WelcomeScreen":
        return cls(
            description=data.get("description"),
            welcome_channels=[WelcomeScreenChannel._from_data(c) for c in data.get("welcome_channels", [])],
        )


class Guild(DiscordModel):
    __slots__ = (
        "id",
        "_http",
        "name",
        "_icon",
        "_splash",
        "_discovery_splash",
        "owner_id",
        "_afk_channel_id",
        "afk_timeout",
        "widget_enabled",
        "widget_channel_id",
        "verification_level",
        "default_message_notifications",
        "explicit_content_filter",
        "_roles",
        "_emojis",
        "features",
        "mfa_level",
        "application_id",
        "system_channel_id",
        "system_channel_flags",
        "rules_channel_id",
        "max_presences",
        "max_members",
        "vanity_url_code",
        "description",
        "_banner",
        "premium_tier",
        "premium_subscription_count",
        "preferred_locale",
        "public_updates_channel_id",
        "max_video_channel_users",
        "max_stage_video_channel_users",
        "approximate_member_count",
        "approximate_presence_count",
        "welcome_screen",
        "nsfw_level",
        "_stickers",
        "premium_progress_bar_enabled",
        "safety_alerts_channel_id",
        "_channels",
        "_members",
        "member_count",
        "large",
        "unavailable",
        "joined_at",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        name: str,
        icon: Optional[str],
        splash: Optional[str],
        discovery_splash: Optional[str],
        owner_id: int,
        afk_channel_id: Optional[int],
        afk_timeout: int,
        widget_enabled: bool,
        widget_channel_id: Optional[int],
        verification_level: VerificationLevel,
        default_message_notifications: DefaultMessageNotificationLevel,
        explicit_content_filter: ExplicitContentFilterLevel,
        roles: dict[int, Any],
        emojis: dict[int, Any],
        features: list[str],
        mfa_level: MFALevel,
        application_id: Optional[int],
        system_channel_id: Optional[int],
        system_channel_flags: SystemChannelFlags,
        rules_channel_id: Optional[int],
        max_presences: Optional[int],
        max_members: Optional[int],
        vanity_url_code: Optional[str],
        description: Optional[str],
        banner: Optional[str],
        premium_tier: PremiumTier,
        premium_subscription_count: int,
        preferred_locale: str,
        public_updates_channel_id: Optional[int],
        max_video_channel_users: Optional[int],
        max_stage_video_channel_users: Optional[int],
        approximate_member_count: Optional[int],
        approximate_presence_count: Optional[int],
        welcome_screen: Optional[WelcomeScreen],
        nsfw_level: NSFWLevel,
        stickers: dict[int, Any],
        premium_progress_bar_enabled: bool,
        safety_alerts_channel_id: Optional[int],
        channels: dict[int, Any],
        members: dict[int, Any],
        member_count: int,
        large: bool,
        unavailable: bool,
        joined_at: Optional[datetime.datetime],
    ) -> None:
        super().__init__(id, http)
        self.name = name
        self._icon = icon
        self._splash = splash
        self._discovery_splash = discovery_splash
        self.owner_id = owner_id
        self._afk_channel_id = afk_channel_id
        self.afk_timeout = afk_timeout
        self.widget_enabled = widget_enabled
        self.widget_channel_id = widget_channel_id
        self.verification_level = verification_level
        self.default_message_notifications = default_message_notifications
        self.explicit_content_filter = explicit_content_filter
        self._roles = roles
        self._emojis = emojis
        self.features = features
        self.mfa_level = mfa_level
        self.application_id = application_id
        self.system_channel_id = system_channel_id
        self.system_channel_flags = system_channel_flags
        self.rules_channel_id = rules_channel_id
        self.max_presences = max_presences
        self.max_members = max_members
        self.vanity_url_code = vanity_url_code
        self.description = description
        self._banner = banner
        self.premium_tier = premium_tier
        self.premium_subscription_count = premium_subscription_count
        self.preferred_locale = preferred_locale
        self.public_updates_channel_id = public_updates_channel_id
        self.max_video_channel_users = max_video_channel_users
        self.max_stage_video_channel_users = max_stage_video_channel_users
        self.approximate_member_count = approximate_member_count
        self.approximate_presence_count = approximate_presence_count
        self.welcome_screen = welcome_screen
        self.nsfw_level = nsfw_level
        self._stickers = stickers
        self.premium_progress_bar_enabled = premium_progress_bar_enabled
        self.safety_alerts_channel_id = safety_alerts_channel_id
        self._channels = channels
        self._members = members
        self.member_count = member_count
        self.large = large
        self.unavailable = unavailable
        self.joined_at = joined_at

    def __repr__(self) -> str:
        return f"<Guild id={self.id} name={self.name!r} members={self.member_count}>"

    @property
    def icon_url(self) -> Optional[str]:
        if self._icon is None:
            return None
        ext = "gif" if self._icon.startswith("a_") else "png"
        return f"https://cdn.discordapp.com/icons/{self.id}/{self._icon}.{ext}?size=1024"

    @property
    def splash_url(self) -> Optional[str]:
        if self._splash is None:
            return None
        return f"https://cdn.discordapp.com/splashes/{self.id}/{self._splash}.png?size=2048"

    @property
    def banner_url(self) -> Optional[str]:
        if self._banner is None:
            return None
        ext = "gif" if self._banner.startswith("a_") else "png"
        return f"https://cdn.discordapp.com/banners/{self.id}/{self._banner}.{ext}?size=1024"

    @property
    def roles(self) -> list[Any]:
        return list(self._roles.values())

    @property
    def emojis(self) -> list[Any]:
        return list(self._emojis.values())

    @property
    def channels(self) -> list[Any]:
        return list(self._channels.values())

    @property
    def members(self) -> list[Any]:
        return list(self._members.values())

    @property
    def stickers(self) -> list[Any]:
        return list(self._stickers.values())

    def get_role(self, role_id: int) -> Optional[Any]:
        return self._roles.get(role_id)

    def get_channel(self, channel_id: int) -> Optional[Any]:
        return self._channels.get(channel_id)

    def get_member(self, member_id: int) -> Optional[Any]:
        return self._members.get(member_id)

    def get_emoji(self, emoji_id: int) -> Optional[Any]:
        return self._emojis.get(emoji_id)

    @property
    def default_role(self) -> Optional[Any]:
        return self._roles.get(self.id)

    @property
    def me(self) -> Optional[Any]:
        return None

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "Guild":
        from .role import Role
        from .emoji import Emoji
        from .sticker import Sticker
        from .channel import _channel_from_data
        from .member import Member

        roles = {int(r["id"]): Role._from_data(r, http, int(data["id"])) for r in data.get("roles", [])}
        emojis = {int(e["id"]): Emoji._from_data(e, http, int(data["id"])) for e in data.get("emojis", []) if e.get("id")}
        stickers = {int(s["id"]): Sticker._from_data(s, http) for s in data.get("stickers", [])}
        channels = {}
        for c in data.get("channels", []):
            c_obj = _channel_from_data({**c, "guild_id": data["id"]}, http)
            channels[c_obj.id] = c_obj
        members = {}
        for m in data.get("members", []):
            member = Member._from_data(m, http, int(data["id"]))
            members[member.id] = member

        welcome_data = data.get("welcome_screen")

        return cls(
            id=int(data["id"]),
            http=http,
            name=data["name"],
            icon=data.get("icon"),
            splash=data.get("splash"),
            discovery_splash=data.get("discovery_splash"),
            owner_id=int(data["owner_id"]) if data.get("owner_id") else 0,
            afk_channel_id=int(data["afk_channel_id"]) if data.get("afk_channel_id") else None,
            afk_timeout=data.get("afk_timeout", 300),
            widget_enabled=data.get("widget_enabled", False),
            widget_channel_id=int(data["widget_channel_id"]) if data.get("widget_channel_id") else None,
            verification_level=VerificationLevel(data.get("verification_level", 0)),
            default_message_notifications=DefaultMessageNotificationLevel(data.get("default_message_notifications", 0)),
            explicit_content_filter=ExplicitContentFilterLevel(data.get("explicit_content_filter", 0)),
            roles=roles,
            emojis=emojis,
            features=data.get("features", []),
            mfa_level=MFALevel(data.get("mfa_level", 0)),
            application_id=int(data["application_id"]) if data.get("application_id") else None,
            system_channel_id=int(data["system_channel_id"]) if data.get("system_channel_id") else None,
            system_channel_flags=SystemChannelFlags(data.get("system_channel_flags", 0)),
            rules_channel_id=int(data["rules_channel_id"]) if data.get("rules_channel_id") else None,
            max_presences=data.get("max_presences"),
            max_members=data.get("max_members"),
            vanity_url_code=data.get("vanity_url_code"),
            description=data.get("description"),
            banner=data.get("banner"),
            premium_tier=PremiumTier(data.get("premium_tier", 0)),
            premium_subscription_count=data.get("premium_subscription_count", 0),
            preferred_locale=data.get("preferred_locale", "en-US"),
            public_updates_channel_id=int(data["public_updates_channel_id"]) if data.get("public_updates_channel_id") else None,
            max_video_channel_users=data.get("max_video_channel_users"),
            max_stage_video_channel_users=data.get("max_stage_video_channel_users"),
            approximate_member_count=data.get("approximate_member_count"),
            approximate_presence_count=data.get("approximate_presence_count"),
            welcome_screen=WelcomeScreen._from_data(welcome_data) if welcome_data else None,
            nsfw_level=NSFWLevel(data.get("nsfw_level", 0)),
            stickers=stickers,
            premium_progress_bar_enabled=data.get("premium_progress_bar_enabled", False),
            safety_alerts_channel_id=int(data["safety_alerts_channel_id"]) if data.get("safety_alerts_channel_id") else None,
            channels=channels,
            members=members,
            member_count=data.get("member_count", 0),
            large=data.get("large", False),
            unavailable=data.get("unavailable", False),
            joined_at=parse_timestamp(data.get("joined_at")),
        )

    async def ban(
        self,
        user_id: int,
        *,
        delete_message_seconds: int = 0,
        reason: Optional[str] = None,
    ) -> None:
        await self._http.create_guild_ban(self.id, user_id, delete_message_seconds=delete_message_seconds, reason=reason)

    async def unban(self, user_id: int, *, reason: Optional[str] = None) -> None:
        await self._http.remove_guild_ban(self.id, user_id, reason=reason)

    async def kick(self, user_id: int, *, reason: Optional[str] = None) -> None:
        await self._http.remove_guild_member(self.id, user_id, reason=reason)

    async def fetch_member(self, user_id: int) -> Any:
        from .member import Member
        data = await self._http.get_guild_member(self.id, user_id)
        return Member._from_data(data, self._http, self.id)

    async def fetch_members(self, *, limit: int = 1000, after: int = 0) -> list[Any]:
        from .member import Member
        data_list = await self._http.list_guild_members(self.id, limit=limit, after=after)
        return [Member._from_data(d, self._http, self.id) for d in data_list]

    async def fetch_channels(self) -> list[Any]:
        from .channel import _channel_from_data
        data_list = await self._http.get_guild_channels(self.id)
        return [_channel_from_data({**d, "guild_id": str(self.id)}, self._http) for d in data_list]

    async def fetch_roles(self) -> list[Any]:
        from .role import Role
        data_list = await self._http.get_guild_roles(self.id)
        return [Role._from_data(d, self._http, self.id) for d in data_list]

    async def create_role(
        self,
        *,
        name: str = "new role",
        permissions: int = 0,
        color: int = 0,
        hoist: bool = False,
        mentionable: bool = False,
        reason: Optional[str] = None,
    ) -> Any:
        from .role import Role
        payload = {
            "name": name,
            "permissions": str(permissions),
            "color": color,
            "hoist": hoist,
            "mentionable": mentionable,
        }
        data = await self._http.create_guild_role(self.id, payload, reason=reason)
        return Role._from_data(data, self._http, self.id)

    async def create_text_channel(
        self,
        name: str,
        *,
        topic: Optional[str] = None,
        position: Optional[int] = None,
        nsfw: bool = False,
        category_id: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Any:
        from .channel import _channel_from_data
        payload: dict[str, Any] = {"name": name, "type": 0, "nsfw": nsfw}
        if topic:
            payload["topic"] = topic
        if position is not None:
            payload["position"] = position
        if category_id:
            payload["parent_id"] = str(category_id)
        data = await self._http.create_guild_channel(self.id, payload, reason=reason)
        return _channel_from_data({**data, "guild_id": str(self.id)}, self._http)

    async def edit(
        self,
        *,
        name: str = MISSING,
        verification_level: Optional[VerificationLevel] = MISSING,
        default_message_notifications: Optional[DefaultMessageNotificationLevel] = MISSING,
        explicit_content_filter: Optional[ExplicitContentFilterLevel] = MISSING,
        description: Optional[str] = MISSING,
        preferred_locale: str = MISSING,
        reason: Optional[str] = None,
    ) -> "Guild":
        payload: dict[str, Any] = {}
        if name is not MISSING:
            payload["name"] = name
        if verification_level is not MISSING:
            payload["verification_level"] = verification_level.value if verification_level else None
        if default_message_notifications is not MISSING:
            payload["default_message_notifications"] = default_message_notifications.value if default_message_notifications else None
        if explicit_content_filter is not MISSING:
            payload["explicit_content_filter"] = explicit_content_filter.value if explicit_content_filter else None
        if description is not MISSING:
            payload["description"] = description
        if preferred_locale is not MISSING:
            payload["preferred_locale"] = preferred_locale
        data = await self._http.edit_guild(self.id, payload, reason=reason)
        return Guild._from_data(data, self._http)

    async def leave(self) -> None:
        await self._http.leave_guild(self.id)

    async def delete(self) -> None:
        await self._http.delete_guild(self.id)
