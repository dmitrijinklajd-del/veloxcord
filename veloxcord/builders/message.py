from __future__ import annotations
from typing import Any, Optional

from ..models.embed import Embed
from ..models.attachment import File
from ..flags import MessageFlags


class MessageBuilder:
    __slots__ = (
        "_content",
        "_tts",
        "_embeds",
        "_components",
        "_files",
        "_flags",
        "_reference_id",
        "_mention_reply",
        "_allowed_mentions",
    )

    def __init__(self) -> None:
        self._content: Optional[str] = None
        self._tts: bool = False
        self._embeds: list[Embed] = []
        self._components: list[Any] = []
        self._files: list[File] = []
        self._flags: int = 0
        self._reference_id: Optional[int] = None
        self._mention_reply: bool = True
        self._allowed_mentions: dict[str, Any] = {}

    def __repr__(self) -> str:
        return f"<MessageBuilder content={self._content!r} embeds={len(self._embeds)}>"

    def content(self, text: str) -> "MessageBuilder":
        self._content = text
        return self

    def tts(self, value: bool = True) -> "MessageBuilder":
        self._tts = value
        return self

    def embed(self, embed: Embed) -> "MessageBuilder":
        self._embeds.append(embed)
        return self

    def embeds(self, *embeds: Embed) -> "MessageBuilder":
        self._embeds.extend(embeds)
        return self

    def component(self, row: Any) -> "MessageBuilder":
        self._components.append(row)
        return self

    def components(self, *rows: Any) -> "MessageBuilder":
        self._components.extend(rows)
        return self

    def file(self, fp: Any, filename: Optional[str] = None, *, spoiler: bool = False) -> "MessageBuilder":
        self._files.append(File(fp, filename, spoiler=spoiler))
        return self

    def ephemeral(self) -> "MessageBuilder":
        self._flags |= 64
        return self

    def suppress_embeds(self) -> "MessageBuilder":
        self._flags |= 4
        return self

    def suppress_notifications(self) -> "MessageBuilder":
        self._flags |= 4096
        return self

    def reply_to(self, message_id: int, *, mention: bool = True) -> "MessageBuilder":
        self._reference_id = message_id
        self._mention_reply = mention
        return self

    def allowed_mentions(
        self,
        *,
        everyone: bool = True,
        roles: bool = True,
        users: bool = True,
        replied_user: bool = True,
    ) -> "MessageBuilder":
        self._allowed_mentions = {
            "parse": (
                (["everyone"] if everyone else [])
                + (["roles"] if roles else [])
                + (["users"] if users else [])
            ),
            "replied_user": replied_user,
        }
        return self

    def build(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self._content is not None:
            payload["content"] = self._content
        if self._tts:
            payload["tts"] = self._tts
        if self._embeds:
            payload["embeds"] = [e.to_dict() for e in self._embeds]
        if self._components:
            payload["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in self._components]
        if self._flags:
            payload["flags"] = self._flags
        if self._reference_id:
            payload["message_reference"] = {
                "message_id": str(self._reference_id),
                "fail_if_not_exists": False,
            }
            if not self._mention_reply:
                payload["allowed_mentions"] = {"replied_user": False}
        if self._allowed_mentions:
            payload["allowed_mentions"] = self._allowed_mentions
        return payload

    @property
    def files(self) -> list[File]:
        return self._files
