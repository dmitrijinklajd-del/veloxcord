from __future__ import annotations
from typing import Any, Optional

from ..models.component import ActionRow, Button, SelectMenu, TextInput


class ActionRowBuilder:
    __slots__ = ("_components",)

    def __init__(self) -> None:
        self._components: list[Any] = []

    def __repr__(self) -> str:
        return f"<ActionRowBuilder components={len(self._components)}>"

    def add_button(self, button: Button) -> "ActionRowBuilder":
        self._components.append(button)
        return self

    def add_select(self, select: SelectMenu) -> "ActionRowBuilder":
        self._components.append(select)
        return self

    def add_component(self, component: Any) -> "ActionRowBuilder":
        self._components.append(component)
        return self

    def build(self) -> ActionRow:
        return ActionRow(components=list(self._components))
