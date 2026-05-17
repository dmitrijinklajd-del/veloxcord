from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from .base import Snowflake

if TYPE_CHECKING:
    pass


class Attachment(Snowflake):
    __slots__ = (
        "id",
        "filename",
        "description",
        "content_type",
        "size",
        "url",
        "proxy_url",
        "height",
        "width",
        "ephemeral",
        "duration_secs",
        "waveform",
        "flags",
    )

    def __init__(
        self,
        id: int,
        filename: str,
        description: Optional[str],
        content_type: Optional[str],
        size: int,
        url: str,
        proxy_url: str,
        height: Optional[int],
        width: Optional[int],
        ephemeral: bool,
        duration_secs: Optional[float],
        waveform: Optional[str],
        flags: int,
    ) -> None:
        super().__init__(id)
        self.filename = filename
        self.description = description
        self.content_type = content_type
        self.size = size
        self.url = url
        self.proxy_url = proxy_url
        self.height = height
        self.width = width
        self.ephemeral = ephemeral
        self.duration_secs = duration_secs
        self.waveform = waveform
        self.flags = flags

    def __repr__(self) -> str:
        return f"<Attachment id={self.id} filename={self.filename!r} size={self.size}>"

    @property
    def is_image(self) -> bool:
        return self.content_type is not None and self.content_type.startswith("image/")

    @property
    def is_voice_message(self) -> bool:
        return self.duration_secs is not None

    @property
    def is_spoiler(self) -> bool:
        return self.filename.startswith("SPOILER_")

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "Attachment":
        return cls(
            id=int(data["id"]),
            filename=data["filename"],
            description=data.get("description"),
            content_type=data.get("content_type"),
            size=data.get("size", 0),
            url=data.get("url", ""),
            proxy_url=data.get("proxy_url", ""),
            height=data.get("height"),
            width=data.get("width"),
            ephemeral=data.get("ephemeral", False),
            duration_secs=data.get("duration_secs"),
            waveform=data.get("waveform"),
            flags=data.get("flags", 0),
        )


class File:
    __slots__ = ("fp", "filename", "description", "spoiler")

    def __init__(
        self,
        fp: Any,
        filename: Optional[str] = None,
        *,
        description: Optional[str] = None,
        spoiler: bool = False,
    ) -> None:
        self.fp = fp
        self.filename = filename or getattr(fp, "name", "unknown")
        self.description = description
        self.spoiler = spoiler
        if self.spoiler and not self.filename.startswith("SPOILER_"):
            self.filename = f"SPOILER_{self.filename}"

    def __repr__(self) -> str:
        return f"<File filename={self.filename!r}>"

    def read(self) -> bytes:
        if hasattr(self.fp, "read"):
            return self.fp.read()
        return self.fp
