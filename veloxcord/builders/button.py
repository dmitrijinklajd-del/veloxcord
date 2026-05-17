from __future__ import annotations
from typing import Optional

from ..models.component import Button
from ..models.emoji import PartialEmoji
from ..enums import ButtonStyle


class ButtonBuilder:
    __slots__ = (
        "_style",
        "_label",
        "_emoji",
        "_custom_id",
        "_url",
        "_disabled",
    )

    def __init__(self) -> None:
        self._style: ButtonStyle = ButtonStyle.PRIMARY
        self._label: Optional[str] = None
        self._emoji: Optional[PartialEmoji] = None
        self._custom_id: Optional[str] = None
        self._url: Optional[str] = None
        self._disabled: bool = False

    def __repr__(self) -> str:
        return f"<ButtonBuilder label={self._label!r} style={self._style}>"

    def style(self, style: ButtonStyle) -> "ButtonBuilder":
        self._style = style
        return self

    def primary(self) -> "ButtonBuilder":
        self._style = ButtonStyle.PRIMARY
        return self

    def secondary(self) -> "ButtonBuilder":
        self._style = ButtonStyle.SECONDARY
        return self

    def success(self) -> "ButtonBuilder":
        self._style = ButtonStyle.SUCCESS
        return self

    def danger(self) -> "ButtonBuilder":
        self._style = ButtonStyle.DANGER
        return self

    def link(self) -> "ButtonBuilder":
        self._style = ButtonStyle.LINK
        return self

    def label(self, text: str) -> "ButtonBuilder":
        self._label = text
        return self

    def emoji(
        self,
        name: Optional[str] = None,
        *,
        id: Optional[int] = None,
        animated: bool = False,
    ) -> "ButtonBuilder":
        self._emoji = PartialEmoji(id=id, name=name, animated=animated)
        return self

    def custom_id(self, value: str) -> "ButtonBuilder":
        self._custom_id = value
        return self

    def url(self, value: str) -> "ButtonBuilder":
        self._url = value
        return self

    def disabled(self, value: bool = True) -> "ButtonBuilder":
        self._disabled = value
        return self

    def build(self) -> Button:
        return Button(
            style=self._style,
            label=self._label,
            emoji=self._emoji,
            custom_id=self._custom_id,
            url=self._url,
            disabled=self._disabled,
        )
