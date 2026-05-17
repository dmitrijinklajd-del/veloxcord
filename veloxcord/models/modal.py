from __future__ import annotations
from typing import Any, Optional

from .component import ActionRow, TextInput


class Modal:
    __slots__ = ("custom_id", "title", "components")

    def __init__(
        self,
        custom_id: str,
        title: str,
        components: Optional[list[ActionRow]] = None,
    ) -> None:
        self.custom_id = custom_id
        self.title = title
        self.components: list[ActionRow] = components or []

    def __repr__(self) -> str:
        return f"<Modal custom_id={self.custom_id!r} title={self.title!r}>"

    def add_text_input(
        self,
        custom_id: str,
        label: str,
        *,
        style: int = 1,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        required: bool = True,
        value: Optional[str] = None,
        placeholder: Optional[str] = None,
    ) -> "Modal":
        from ..enums import TextInputStyle
        text_input = TextInput(
            custom_id=custom_id,
            style=TextInputStyle(style),
            label=label,
            min_length=min_length,
            max_length=max_length,
            required=required,
            value=value,
            placeholder=placeholder,
        )
        row = ActionRow([text_input])
        self.components.append(row)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "custom_id": self.custom_id,
            "title": self.title,
            "components": [c.to_dict() for c in self.components],
        }

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "Modal":
        rows = [ActionRow._from_data(c) for c in data.get("components", [])]
        return cls(
            custom_id=data["custom_id"],
            title=data["title"],
            components=rows,
        )

    def get_value(self, custom_id: str) -> Optional[str]:
        for row in self.components:
            for component in row.components:
                if hasattr(component, "custom_id") and component.custom_id == custom_id:
                    if hasattr(component, "value"):
                        return component.value
        return None
