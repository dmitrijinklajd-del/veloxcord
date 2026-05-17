from __future__ import annotations
import datetime
from typing import Any, Optional


class EmbedFooter:
    __slots__ = ("text", "icon_url", "proxy_icon_url")

    def __init__(
        self,
        text: str,
        icon_url: Optional[str] = None,
        proxy_icon_url: Optional[str] = None,
    ) -> None:
        self.text = text
        self.icon_url = icon_url
        self.proxy_icon_url = proxy_icon_url

    def __repr__(self) -> str:
        return f"<EmbedFooter text={self.text!r}>"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"text": self.text}
        if self.icon_url:
            payload["icon_url"] = self.icon_url
        return payload

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "EmbedFooter":
        return cls(
            text=data["text"],
            icon_url=data.get("icon_url"),
            proxy_icon_url=data.get("proxy_icon_url"),
        )


class EmbedMedia:
    __slots__ = ("url", "proxy_url", "height", "width")

    def __init__(
        self,
        url: str,
        proxy_url: Optional[str] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
    ) -> None:
        self.url = url
        self.proxy_url = proxy_url
        self.height = height
        self.width = width

    def __repr__(self) -> str:
        return f"<EmbedMedia url={self.url!r}>"

    def to_dict(self) -> dict[str, Any]:
        return {"url": self.url}

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "EmbedMedia":
        return cls(
            url=data["url"],
            proxy_url=data.get("proxy_url"),
            height=data.get("height"),
            width=data.get("width"),
        )


class EmbedAuthor:
    __slots__ = ("name", "url", "icon_url", "proxy_icon_url")

    def __init__(
        self,
        name: str,
        url: Optional[str] = None,
        icon_url: Optional[str] = None,
        proxy_icon_url: Optional[str] = None,
    ) -> None:
        self.name = name
        self.url = url
        self.icon_url = icon_url
        self.proxy_icon_url = proxy_icon_url

    def __repr__(self) -> str:
        return f"<EmbedAuthor name={self.name!r}>"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": self.name}
        if self.url:
            payload["url"] = self.url
        if self.icon_url:
            payload["icon_url"] = self.icon_url
        return payload

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "EmbedAuthor":
        return cls(
            name=data["name"],
            url=data.get("url"),
            icon_url=data.get("icon_url"),
            proxy_icon_url=data.get("proxy_icon_url"),
        )


class EmbedField:
    __slots__ = ("name", "value", "inline")

    def __init__(self, name: str, value: str, inline: bool = False) -> None:
        self.name = name
        self.value = value
        self.inline = inline

    def __repr__(self) -> str:
        return f"<EmbedField name={self.name!r} inline={self.inline}>"

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "value": self.value, "inline": self.inline}

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "EmbedField":
        return cls(
            name=data["name"],
            value=data["value"],
            inline=data.get("inline", False),
        )


class Embed:
    __slots__ = (
        "title",
        "description",
        "url",
        "timestamp",
        "color",
        "footer",
        "image",
        "thumbnail",
        "video",
        "provider",
        "author",
        "fields",
        "type",
    )

    def __init__(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        color: Optional[int] = None,
        footer: Optional[EmbedFooter] = None,
        image: Optional[EmbedMedia] = None,
        thumbnail: Optional[EmbedMedia] = None,
        author: Optional[EmbedAuthor] = None,
        fields: Optional[list[EmbedField]] = None,
        type: str = "rich",
    ) -> None:
        self.title = title
        self.description = description
        self.url = url
        self.timestamp = timestamp
        self.color = color
        self.footer = footer
        self.image = image
        self.thumbnail = thumbnail
        self.video: Optional[EmbedMedia] = None
        self.provider: Optional[dict[str, Any]] = None
        self.author = author
        self.fields: list[EmbedField] = fields or []
        self.type = type

    def __repr__(self) -> str:
        return f"<Embed title={self.title!r} fields={len(self.fields)}>"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"type": self.type}
        if self.title:
            payload["title"] = self.title
        if self.description:
            payload["description"] = self.description
        if self.url:
            payload["url"] = self.url
        if self.timestamp:
            payload["timestamp"] = self.timestamp.isoformat()
        if self.color is not None:
            payload["color"] = self.color
        if self.footer:
            payload["footer"] = self.footer.to_dict()
        if self.image:
            payload["image"] = self.image.to_dict()
        if self.thumbnail:
            payload["thumbnail"] = self.thumbnail.to_dict()
        if self.author:
            payload["author"] = self.author.to_dict()
        if self.fields:
            payload["fields"] = [f.to_dict() for f in self.fields]
        return payload

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "Embed":
        embed = cls(
            title=data.get("title"),
            description=data.get("description"),
            url=data.get("url"),
            color=data.get("color"),
            type=data.get("type", "rich"),
        )
        if ts := data.get("timestamp"):
            embed.timestamp = datetime.datetime.fromisoformat(ts)
        if footer := data.get("footer"):
            embed.footer = EmbedFooter._from_data(footer)
        if image := data.get("image"):
            embed.image = EmbedMedia._from_data(image)
        if thumbnail := data.get("thumbnail"):
            embed.thumbnail = EmbedMedia._from_data(thumbnail)
        if video := data.get("video"):
            embed.video = EmbedMedia._from_data(video)
        if author := data.get("author"):
            embed.author = EmbedAuthor._from_data(author)
        embed.fields = [EmbedField._from_data(f) for f in data.get("fields", [])]
        return embed
