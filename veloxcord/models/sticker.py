from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from .base import DiscordModel
from ..enums import StickerType, StickerFormatType

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from .user import User


class Sticker(DiscordModel):
    __slots__ = (
        "id",
        "_http",
        "pack_id",
        "name",
        "description",
        "tags",
        "type",
        "format_type",
        "available",
        "guild_id",
        "user",
        "sort_value",
    )

    def __init__(
        self,
        id: int,
        http: "HTTPClient",
        pack_id: Optional[int],
        name: str,
        description: Optional[str],
        tags: str,
        type: StickerType,
        format_type: StickerFormatType,
        available: bool,
        guild_id: Optional[int],
        user: Optional["User"],
        sort_value: Optional[int],
    ) -> None:
        super().__init__(id, http)
        self.pack_id = pack_id
        self.name = name
        self.description = description
        self.tags = tags
        self.type = type
        self.format_type = format_type
        self.available = available
        self.guild_id = guild_id
        self.user = user
        self.sort_value = sort_value

    def __repr__(self) -> str:
        return f"<Sticker id={self.id} name={self.name!r}>"

    @property
    def url(self) -> str:
        match self.format_type:
            case StickerFormatType.LOTTIE:
                return f"https://cdn.discordapp.com/stickers/{self.id}.json"
            case StickerFormatType.GIF:
                return f"https://cdn.discordapp.com/stickers/{self.id}.gif"
            case _:
                return f"https://cdn.discordapp.com/stickers/{self.id}.png"

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "Sticker":
        from .user import User
        user_data = data.get("user")
        return cls(
            id=int(data["id"]),
            http=http,
            pack_id=int(data["pack_id"]) if data.get("pack_id") else None,
            name=data["name"],
            description=data.get("description"),
            tags=data.get("tags", ""),
            type=StickerType(data.get("type", 1)),
            format_type=StickerFormatType(data.get("format_type", 1)),
            available=data.get("available", True),
            guild_id=int(data["guild_id"]) if data.get("guild_id") else None,
            user=User._from_data(user_data, http) if user_data else None,
            sort_value=data.get("sort_value"),
        )


class StickerItem:
    __slots__ = ("id", "name", "format_type")

    def __init__(self, id: int, name: str, format_type: StickerFormatType) -> None:
        self.id = id
        self.name = name
        self.format_type = format_type

    def __repr__(self) -> str:
        return f"<StickerItem id={self.id} name={self.name!r}>"

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "StickerItem":
        return cls(
            id=int(data["id"]),
            name=data["name"],
            format_type=StickerFormatType(data["format_type"]),
        )
