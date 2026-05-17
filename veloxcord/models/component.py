from __future__ import annotations
from typing import Any, Optional

from ..enums import ComponentType, ButtonStyle, TextInputStyle
from .emoji import PartialEmoji


class ActionRow:
    __slots__ = ("type", "components")

    def __init__(self, components: Optional[list[Any]] = None) -> None:
        self.type = ComponentType.ACTION_ROW
        self.components: list[Any] = components or []

    def __repr__(self) -> str:
        return f"<ActionRow components={len(self.components)}>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "components": [c.to_dict() for c in self.components],
        }

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "ActionRow":
        row = cls()
        for comp_data in data.get("components", []):
            row.components.append(_component_from_data(comp_data))
        return row


class Button:
    __slots__ = (
        "type",
        "style",
        "label",
        "emoji",
        "custom_id",
        "url",
        "disabled",
    )

    def __init__(
        self,
        style: ButtonStyle,
        label: Optional[str] = None,
        emoji: Optional[PartialEmoji] = None,
        custom_id: Optional[str] = None,
        url: Optional[str] = None,
        disabled: bool = False,
    ) -> None:
        self.type = ComponentType.BUTTON
        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.url = url
        self.disabled = disabled

    def __repr__(self) -> str:
        return f"<Button label={self.label!r} style={self.style}>"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"type": self.type.value, "style": self.style.value}
        if self.label:
            payload["label"] = self.label
        if self.emoji:
            payload["emoji"] = self.emoji.to_dict()
        if self.custom_id:
            payload["custom_id"] = self.custom_id
        if self.url:
            payload["url"] = self.url
        if self.disabled:
            payload["disabled"] = self.disabled
        return payload

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "Button":
        emoji_data = data.get("emoji")
        return cls(
            style=ButtonStyle(data["style"]),
            label=data.get("label"),
            emoji=PartialEmoji._from_data(emoji_data) if emoji_data else None,
            custom_id=data.get("custom_id"),
            url=data.get("url"),
            disabled=data.get("disabled", False),
        )


class SelectOption:
    __slots__ = ("label", "value", "description", "emoji", "default")

    def __init__(
        self,
        label: str,
        value: str,
        description: Optional[str] = None,
        emoji: Optional[PartialEmoji] = None,
        default: bool = False,
    ) -> None:
        self.label = label
        self.value = value
        self.description = description
        self.emoji = emoji
        self.default = default

    def __repr__(self) -> str:
        return f"<SelectOption label={self.label!r} value={self.value!r}>"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"label": self.label, "value": self.value}
        if self.description:
            payload["description"] = self.description
        if self.emoji:
            payload["emoji"] = self.emoji.to_dict()
        if self.default:
            payload["default"] = self.default
        return payload

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "SelectOption":
        emoji_data = data.get("emoji")
        return cls(
            label=data["label"],
            value=data["value"],
            description=data.get("description"),
            emoji=PartialEmoji._from_data(emoji_data) if emoji_data else None,
            default=data.get("default", False),
        )


class SelectMenu:
    __slots__ = (
        "type",
        "custom_id",
        "options",
        "channel_types",
        "placeholder",
        "default_values",
        "min_values",
        "max_values",
        "disabled",
    )

    def __init__(
        self,
        type: ComponentType,
        custom_id: str,
        options: Optional[list[SelectOption]] = None,
        channel_types: Optional[list[int]] = None,
        placeholder: Optional[str] = None,
        default_values: Optional[list[dict[str, Any]]] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
    ) -> None:
        self.type = type
        self.custom_id = custom_id
        self.options: list[SelectOption] = options or []
        self.channel_types = channel_types or []
        self.placeholder = placeholder
        self.default_values = default_values or []
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled

    def __repr__(self) -> str:
        return f"<SelectMenu custom_id={self.custom_id!r} type={self.type}>"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "type": self.type.value,
            "custom_id": self.custom_id,
            "min_values": self.min_values,
            "max_values": self.max_values,
        }
        if self.options:
            payload["options"] = [o.to_dict() for o in self.options]
        if self.channel_types:
            payload["channel_types"] = self.channel_types
        if self.placeholder:
            payload["placeholder"] = self.placeholder
        if self.default_values:
            payload["default_values"] = self.default_values
        if self.disabled:
            payload["disabled"] = self.disabled
        return payload

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "SelectMenu":
        return cls(
            type=ComponentType(data["type"]),
            custom_id=data["custom_id"],
            options=[SelectOption._from_data(o) for o in data.get("options", [])],
            channel_types=data.get("channel_types"),
            placeholder=data.get("placeholder"),
            default_values=data.get("default_values"),
            min_values=data.get("min_values", 1),
            max_values=data.get("max_values", 1),
            disabled=data.get("disabled", False),
        )


class TextInput:
    __slots__ = (
        "type",
        "custom_id",
        "style",
        "label",
        "min_length",
        "max_length",
        "required",
        "value",
        "placeholder",
    )

    def __init__(
        self,
        custom_id: str,
        style: TextInputStyle,
        label: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        required: bool = True,
        value: Optional[str] = None,
        placeholder: Optional[str] = None,
    ) -> None:
        self.type = ComponentType.TEXT_INPUT
        self.custom_id = custom_id
        self.style = style
        self.label = label
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.value = value
        self.placeholder = placeholder

    def __repr__(self) -> str:
        return f"<TextInput custom_id={self.custom_id!r} label={self.label!r}>"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "type": self.type.value,
            "custom_id": self.custom_id,
            "style": self.style.value,
            "label": self.label,
            "required": self.required,
        }
        if self.min_length is not None:
            payload["min_length"] = self.min_length
        if self.max_length is not None:
            payload["max_length"] = self.max_length
        if self.value is not None:
            payload["value"] = self.value
        if self.placeholder is not None:
            payload["placeholder"] = self.placeholder
        return payload

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "TextInput":
        return cls(
            custom_id=data["custom_id"],
            style=TextInputStyle(data.get("style", 1)),
            label=data.get("label", ""),
            min_length=data.get("min_length"),
            max_length=data.get("max_length"),
            required=data.get("required", True),
            value=data.get("value"),
            placeholder=data.get("placeholder"),
        )


def _component_from_data(data: dict[str, Any]) -> Any:
    comp_type = ComponentType(data["type"])
    match comp_type:
        case ComponentType.ACTION_ROW:
            return ActionRow._from_data(data)
        case ComponentType.BUTTON:
            return Button._from_data(data)
        case ComponentType.TEXT_INPUT:
            return TextInput._from_data(data)
        case _:
            return SelectMenu._from_data(data)
