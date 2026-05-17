from __future__ import annotations
from typing import Any, Optional

from ..models.component import SelectMenu, SelectOption
from ..models.emoji import PartialEmoji
from ..enums import ComponentType


class SelectMenuBuilder:
    __slots__ = (
        "_type",
        "_custom_id",
        "_options",
        "_placeholder",
        "_min_values",
        "_max_values",
        "_disabled",
        "_channel_types",
    )

    def __init__(self, type: ComponentType = ComponentType.STRING_SELECT) -> None:
        self._type = type
        self._custom_id: str = ""
        self._options: list[SelectOption] = []
        self._placeholder: Optional[str] = None
        self._min_values: int = 1
        self._max_values: int = 1
        self._disabled: bool = False
        self._channel_types: list[int] = []

    def __repr__(self) -> str:
        return f"<SelectMenuBuilder custom_id={self._custom_id!r} options={len(self._options)}>"

    def custom_id(self, value: str) -> "SelectMenuBuilder":
        self._custom_id = value
        return self

    def placeholder(self, text: str) -> "SelectMenuBuilder":
        self._placeholder = text
        return self

    def min_values(self, value: int) -> "SelectMenuBuilder":
        self._min_values = value
        return self

    def max_values(self, value: int) -> "SelectMenuBuilder":
        self._max_values = value
        return self

    def disabled(self, value: bool = True) -> "SelectMenuBuilder":
        self._disabled = value
        return self

    def channel_types(self, *types: int) -> "SelectMenuBuilder":
        self._channel_types = list(types)
        return self

    def option(
        self,
        label: str,
        value: str,
        *,
        description: Optional[str] = None,
        emoji_name: Optional[str] = None,
        emoji_id: Optional[int] = None,
        default: bool = False,
    ) -> "SelectMenuBuilder":
        emoji = PartialEmoji(id=emoji_id, name=emoji_name) if (emoji_name or emoji_id) else None
        self._options.append(
            SelectOption(
                label=label,
                value=value,
                description=description,
                emoji=emoji,
                default=default,
            )
        )
        return self

    def add_option(self, option: SelectOption) -> "SelectMenuBuilder":
        self._options.append(option)
        return self

    def build(self) -> SelectMenu:
        return SelectMenu(
            type=self._type,
            custom_id=self._custom_id,
            options=self._options if self._type == ComponentType.STRING_SELECT else [],
            channel_types=self._channel_types if self._type == ComponentType.CHANNEL_SELECT else [],
            placeholder=self._placeholder,
            min_values=self._min_values,
            max_values=self._max_values,
            disabled=self._disabled,
        )
