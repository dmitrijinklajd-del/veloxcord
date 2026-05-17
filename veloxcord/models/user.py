from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from .base import DiscordModel
from ..flags import UserFlags
from ..utils import MISSING

if TYPE_CHECKING:
    from ..http.client import HTTPClient


class User(DiscordModel):
    __slots__ = (
        "id",
        "_http",
        "name",
        "discriminator",
        "global_name",
        "_avatar",
        "_banner",
        "accent_color",
        "bot",
        "system",
        "mfa_enabled",
        "locale",
        "verified",
        "email",
        "flags",
        "premium_type",
        "public_flags",
        "avatar_decoration",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        name: str,
        discriminator: str,
        global_name: Optional[str],
        avatar: Optional[str],
        banner: Optional[str],
        accent_color: Optional[int],
        bot: bool,
        system: bool,
        mfa_enabled: bool,
        locale: Optional[str],
        verified: Optional[bool],
        email: Optional[str],
        flags: int,
        premium_type: int,
        public_flags: int,
        avatar_decoration: Optional[str],
    ) -> None:
        super().__init__(id, http)
        self.name = name
        self.discriminator = discriminator
        self.global_name = global_name
        self._avatar = avatar
        self._banner = banner
        self.accent_color = accent_color
        self.bot = bot
        self.system = system
        self.mfa_enabled = mfa_enabled
        self.locale = locale
        self.verified = verified
        self.email = email
        self.flags = UserFlags(flags)
        self.premium_type = premium_type
        self.public_flags = UserFlags(public_flags)
        self.avatar_decoration = avatar_decoration

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name!r} bot={self.bot}>"

    @property
    def display_name(self) -> str:
        return self.global_name or self.name

    @property
    def mention(self) -> str:
        return f"<@{self.id}>"

    @property
    def tag(self) -> str:
        if self.discriminator == "0":
            return self.name
        return f"{self.name}#{self.discriminator}"

    @property
    def avatar_url(self) -> Optional[str]:
        if self._avatar is None:
            return self.default_avatar_url
        ext = "gif" if self._avatar.startswith("a_") else "png"
        return f"https://cdn.discordapp.com/avatars/{self.id}/{self._avatar}.{ext}?size=1024"

    @property
    def default_avatar_url(self) -> str:
        if self.discriminator == "0":
            index = (self.id >> 22) % 6
        else:
            index = int(self.discriminator) % 5
        return f"https://cdn.discordapp.com/embed/avatars/{index}.png"

    @property
    def banner_url(self) -> Optional[str]:
        if self._banner is None:
            return None
        ext = "gif" if self._banner.startswith("a_") else "png"
        return f"https://cdn.discordapp.com/banners/{self.id}/{self._banner}.{ext}?size=512"

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "User":
        return cls(
            id=int(data["id"]),
            http=http,
            name=data["username"],
            discriminator=data.get("discriminator", "0"),
            global_name=data.get("global_name"),
            avatar=data.get("avatar"),
            banner=data.get("banner"),
            accent_color=data.get("accent_color"),
            bot=data.get("bot", False),
            system=data.get("system", False),
            mfa_enabled=data.get("mfa_enabled", False),
            locale=data.get("locale"),
            verified=data.get("verified"),
            email=data.get("email"),
            flags=data.get("flags", 0),
            premium_type=data.get("premium_type", 0),
            public_flags=data.get("public_flags", 0),
            avatar_decoration=data.get("avatar_decoration"),
        )

    async def send(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[list[Any]] = None,
        components: Optional[list[Any]] = None,
        files: Optional[list[Any]] = None,
        tts: bool = False,
        ephemeral: bool = False,
        suppress_embeds: bool = False,
    ) -> "Any":
        from .message import Message
        channel_data = await self._http.create_dm(self.id)
        channel_id = int(channel_data["id"])
        payload: dict[str, Any] = {}
        if content is not None:
            payload["content"] = content
        if tts:
            payload["tts"] = tts
        if embeds:
            payload["embeds"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in embeds]
        if components:
            payload["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in components]
        flags = 0
        if ephemeral:
            flags |= 64
        if suppress_embeds:
            flags |= 4
        if flags:
            payload["flags"] = flags
        data = await self._http.create_message(channel_id, payload)
        return Message._from_data(data, self._http)

    async def fetch(self) -> "User":
        data = await self._http.get_user(self.id)
        return User._from_data(data, self._http)
