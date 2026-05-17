from __future__ import annotations
from typing import Optional

from ..models.modal import Modal
from ..enums import TextInputStyle


class ModalBuilder:
    __slots__ = ("_custom_id", "_title", "_modal")

    def __init__(self) -> None:
        self._custom_id: str = ""
        self._title: str = ""
        self._modal: Optional[Modal] = None

    def __repr__(self) -> str:
        return f"<ModalBuilder title={self._title!r}>"

    def custom_id(self, value: str) -> "ModalBuilder":
        self._custom_id = value
        return self

    def title(self, value: str) -> "ModalBuilder":
        self._title = value
        return self

    def short_text(
        self,
        custom_id: str,
        label: str,
        *,
        placeholder: Optional[str] = None,
        required: bool = True,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        value: Optional[str] = None,
    ) -> "ModalBuilder":
        if self._modal is None:
            self._modal = Modal(self._custom_id, self._title)
        self._modal.add_text_input(
            custom_id=custom_id,
            label=label,
            style=TextInputStyle.SHORT,
            placeholder=placeholder,
            required=required,
            min_length=min_length,
            max_length=max_length,
            value=value,
        )
        return self

    def paragraph_text(
        self,
        custom_id: str,
        label: str,
        *,
        placeholder: Optional[str] = None,
        required: bool = True,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        value: Optional[str] = None,
    ) -> "ModalBuilder":
        if self._modal is None:
            self._modal = Modal(self._custom_id, self._title)
        self._modal.add_text_input(
            custom_id=custom_id,
            label=label,
            style=TextInputStyle.PARAGRAPH,
            placeholder=placeholder,
            required=required,
            min_length=min_length,
            max_length=max_length,
            value=value,
        )
        return self

    def build(self) -> Modal:
        if self._modal is None:
            self._modal = Modal(self._custom_id, self._title)
        else:
            self._modal.custom_id = self._custom_id
            self._modal.title = self._title
        return self._modal
