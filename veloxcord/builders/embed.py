from __future__ import annotations
import datetime
from typing import Optional

from ..models.embed import (
    Embed,
    EmbedField,
    EmbedFooter,
    EmbedAuthor,
    EmbedMedia,
)


class EmbedBuilder:
    __slots__ = ("_embed",)

    def __init__(self) -> None:
        self._embed = Embed()

    def __repr__(self) -> str:
        return f"<EmbedBuilder title={self._embed.title!r} fields={len(self._embed.fields)}>"

    def title(self, text: str) -> "EmbedBuilder":
        self._embed.title = text
        return self

    def description(self, text: str) -> "EmbedBuilder":
        self._embed.description = text
        return self

    def url(self, url: str) -> "EmbedBuilder":
        self._embed.url = url
        return self

    def color(self, value: int) -> "EmbedBuilder":
        self._embed.color = value
        return self

    def colour(self, value: int) -> "EmbedBuilder":
        return self.color(value)

    def timestamp(self, dt: Optional[datetime.datetime] = None) -> "EmbedBuilder":
        self._embed.timestamp = dt or datetime.datetime.now(tz=datetime.timezone.utc)
        return self

    def footer(
        self,
        text: str,
        *,
        icon_url: Optional[str] = None,
    ) -> "EmbedBuilder":
        self._embed.footer = EmbedFooter(text=text, icon_url=icon_url)
        return self

    def image(self, url: str) -> "EmbedBuilder":
        self._embed.image = EmbedMedia(url=url)
        return self

    def thumbnail(self, url: str) -> "EmbedBuilder":
        self._embed.thumbnail = EmbedMedia(url=url)
        return self

    def author(
        self,
        name: str,
        *,
        url: Optional[str] = None,
        icon_url: Optional[str] = None,
    ) -> "EmbedBuilder":
        self._embed.author = EmbedAuthor(name=name, url=url, icon_url=icon_url)
        return self

    def field(
        self,
        name: str,
        value: str,
        *,
        inline: bool = False,
    ) -> "EmbedBuilder":
        self._embed.fields.append(EmbedField(name=name, value=value, inline=inline))
        return self

    def clear_fields(self) -> "EmbedBuilder":
        self._embed.fields.clear()
        return self

    def remove_field(self, index: int) -> "EmbedBuilder":
        try:
            del self._embed.fields[index]
        except IndexError:
            pass
        return self

    def set_field_at(
        self,
        index: int,
        name: str,
        value: str,
        *,
        inline: bool = False,
    ) -> "EmbedBuilder":
        try:
            self._embed.fields[index] = EmbedField(name=name, value=value, inline=inline)
        except IndexError:
            pass
        return self

    def build(self) -> Embed:
        return self._embed

    def to_dict(self) -> dict:
        return self._embed.to_dict()
