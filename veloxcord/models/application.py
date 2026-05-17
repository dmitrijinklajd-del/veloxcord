from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from .base import DiscordModel

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from .user import User


class ApplicationInstallParams:
    __slots__ = ("scopes", "permissions")

    def __init__(self, scopes: list[str], permissions: int) -> None:
        self.scopes = scopes
        self.permissions = permissions

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "ApplicationInstallParams":
        return cls(scopes=data.get("scopes", []), permissions=int(data.get("permissions", 0)))


class Application(DiscordModel):
    __slots__ = (
        "id",
        "_http",
        "name",
        "_icon",
        "description",
        "rpc_origins",
        "bot_public",
        "bot_require_code_grant",
        "bot",
        "terms_of_service_url",
        "privacy_policy_url",
        "owner",
        "verify_key",
        "team",
        "guild_id",
        "primary_sku_id",
        "slug",
        "_cover_image",
        "flags",
        "approximate_guild_count",
        "redirect_uris",
        "interactions_endpoint_url",
        "role_connections_verification_url",
        "tags",
        "install_params",
        "custom_install_url",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        name: str,
        icon: Optional[str],
        description: str,
        rpc_origins: list[str],
        bot_public: bool,
        bot_require_code_grant: bool,
        bot: Optional["User"],
        terms_of_service_url: Optional[str],
        privacy_policy_url: Optional[str],
        owner: Optional["User"],
        verify_key: str,
        team: Optional[Any],
        guild_id: Optional[int],
        primary_sku_id: Optional[int],
        slug: Optional[str],
        cover_image: Optional[str],
        flags: int,
        approximate_guild_count: Optional[int],
        redirect_uris: list[str],
        interactions_endpoint_url: Optional[str],
        role_connections_verification_url: Optional[str],
        tags: list[str],
        install_params: Optional[ApplicationInstallParams],
        custom_install_url: Optional[str],
    ) -> None:
        super().__init__(id, http)
        self.name = name
        self._icon = icon
        self.description = description
        self.rpc_origins = rpc_origins
        self.bot_public = bot_public
        self.bot_require_code_grant = bot_require_code_grant
        self.bot = bot
        self.terms_of_service_url = terms_of_service_url
        self.privacy_policy_url = privacy_policy_url
        self.owner = owner
        self.verify_key = verify_key
        self.team = team
        self.guild_id = guild_id
        self.primary_sku_id = primary_sku_id
        self.slug = slug
        self._cover_image = cover_image
        self.flags = flags
        self.approximate_guild_count = approximate_guild_count
        self.redirect_uris = redirect_uris
        self.interactions_endpoint_url = interactions_endpoint_url
        self.role_connections_verification_url = role_connections_verification_url
        self.tags = tags
        self.install_params = install_params
        self.custom_install_url = custom_install_url

    def __repr__(self) -> str:
        return f"<Application id={self.id} name={self.name!r}>"

    @property
    def icon_url(self) -> Optional[str]:
        if self._icon is None:
            return None
        return f"https://cdn.discordapp.com/app-icons/{self.id}/{self._icon}.png?size=1024"

    @property
    def cover_image_url(self) -> Optional[str]:
        if self._cover_image is None:
            return None
        return f"https://cdn.discordapp.com/app-icons/{self.id}/{self._cover_image}.png?size=1024"

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "Application":
        from .user import User
        bot_data = data.get("bot")
        owner_data = data.get("owner")
        install_params_data = data.get("install_params")
        return cls(
            id=int(data["id"]),
            http=http,
            name=data["name"],
            icon=data.get("icon"),
            description=data.get("description", ""),
            rpc_origins=data.get("rpc_origins", []),
            bot_public=data.get("bot_public", False),
            bot_require_code_grant=data.get("bot_require_code_grant", False),
            bot=User._from_data(bot_data, http) if bot_data else None,
            terms_of_service_url=data.get("terms_of_service_url"),
            privacy_policy_url=data.get("privacy_policy_url"),
            owner=User._from_data(owner_data, http) if owner_data else None,
            verify_key=data.get("verify_key", ""),
            team=data.get("team"),
            guild_id=int(data["guild_id"]) if data.get("guild_id") else None,
            primary_sku_id=int(data["primary_sku_id"]) if data.get("primary_sku_id") else None,
            slug=data.get("slug"),
            cover_image=data.get("cover_image"),
            flags=data.get("flags", 0),
            approximate_guild_count=data.get("approximate_guild_count"),
            redirect_uris=data.get("redirect_uris", []),
            interactions_endpoint_url=data.get("interactions_endpoint_url"),
            role_connections_verification_url=data.get("role_connections_verification_url"),
            tags=data.get("tags", []),
            install_params=ApplicationInstallParams._from_data(install_params_data) if install_params_data else None,
            custom_install_url=data.get("custom_install_url"),
        )
