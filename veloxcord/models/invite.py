from __future__ import annotations
import datetime
from typing import TYPE_CHECKING, Any, Optional

from ..enums import InviteTargetType
from ..utils import parse_timestamp

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from .user import User
    from .guild import Guild
    from .channel import TextChannel


class InviteGuild:
    __slots__ = (
        "id",
        "name",
        "splash",
        "banner",
        "description",
        "icon",
        "features",
        "verification_level",
        "vanity_url_code",
        "nsfw_level",
        "premium_subscription_count",
    )

    def __init__(
        self,
        id: int,
        name: str,
        splash: Optional[str],
        banner: Optional[str],
        description: Optional[str],
        icon: Optional[str],
        features: list[str],
        verification_level: int,
        vanity_url_code: Optional[str],
        nsfw_level: int,
        premium_subscription_count: int,
    ) -> None:
        self.id = id
        self.name = name
        self.splash = splash
        self.banner = banner
        self.description = description
        self.icon = icon
        self.features = features
        self.verification_level = verification_level
        self.vanity_url_code = vanity_url_code
        self.nsfw_level = nsfw_level
        self.premium_subscription_count = premium_subscription_count

    def __repr__(self) -> str:
        return f"<InviteGuild id={self.id} name={self.name!r}>"

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "InviteGuild":
        return cls(
            id=int(data["id"]),
            name=data["name"],
            splash=data.get("splash"),
            banner=data.get("banner"),
            description=data.get("description"),
            icon=data.get("icon"),
            features=data.get("features", []),
            verification_level=data.get("verification_level", 0),
            vanity_url_code=data.get("vanity_url_code"),
            nsfw_level=data.get("nsfw_level", 0),
            premium_subscription_count=data.get("premium_subscription_count", 0),
        )


class Invite:
    __slots__ = (
        "_http",
        "code",
        "guild",
        "channel",
        "inviter",
        "target_type",
        "target_user",
        "approximate_member_count",
        "approximate_presence_count",
        "expires_at",
        "uses",
        "max_uses",
        "max_age",
        "temporary",
        "created_at",
    )

    def __init__(
        self,
        http: "HTTPClient",
        code: str,
        guild: Optional[InviteGuild],
        channel: Optional[Any],
        inviter: Optional["User"],
        target_type: Optional[InviteTargetType],
        target_user: Optional["User"],
        approximate_member_count: Optional[int],
        approximate_presence_count: Optional[int],
        expires_at: Optional[datetime.datetime],
        uses: int,
        max_uses: int,
        max_age: int,
        temporary: bool,
        created_at: Optional[datetime.datetime],
    ) -> None:
        self._http = http
        self.code = code
        self.guild = guild
        self.channel = channel
        self.inviter = inviter
        self.target_type = target_type
        self.target_user = target_user
        self.approximate_member_count = approximate_member_count
        self.approximate_presence_count = approximate_presence_count
        self.expires_at = expires_at
        self.uses = uses
        self.max_uses = max_uses
        self.max_age = max_age
        self.temporary = temporary
        self.created_at = created_at

    def __repr__(self) -> str:
        return f"<Invite code={self.code!r} guild={self.guild!r}>"

    def __str__(self) -> str:
        return self.url

    @property
    def url(self) -> str:
        return f"https://discord.gg/{self.code}"

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        from ..utils import utcnow
        return utcnow() > self.expires_at

    async def delete(self, *, reason: Optional[str] = None) -> None:
        await self._http.delete_invite(self.code, reason=reason)

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "Invite":
        from .user import User
        from .channel import _channel_from_data

        guild_data = data.get("guild")
        channel_data = data.get("channel")
        inviter_data = data.get("inviter")
        target_user_data = data.get("target_user")
        target_type_raw = data.get("target_type")

        return cls(
            http=http,
            code=data["code"],
            guild=InviteGuild._from_data(guild_data) if guild_data else None,
            channel=_channel_from_data(channel_data, http) if channel_data else None,
            inviter=User._from_data(inviter_data, http) if inviter_data else None,
            target_type=InviteTargetType(target_type_raw) if target_type_raw else None,
            target_user=User._from_data(target_user_data, http) if target_user_data else None,
            approximate_member_count=data.get("approximate_member_count"),
            approximate_presence_count=data.get("approximate_presence_count"),
            expires_at=parse_timestamp(data.get("expires_at")),
            uses=data.get("uses", 0),
            max_uses=data.get("max_uses", 0),
            max_age=data.get("max_age", 0),
            temporary=data.get("temporary", False),
            created_at=parse_timestamp(data.get("created_at")),
        )
