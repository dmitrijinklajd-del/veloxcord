from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ..http.client import HTTPClient


class VoiceClient:
    __slots__ = (
        "guild_id",
        "channel_id",
        "_http",
        "_ws",
        "_connected",
        "_endpoint",
        "_session_id",
        "_token",
    )

    def __init__(self, guild_id: int, channel_id: int, http: "HTTPClient") -> None:
        self.guild_id = guild_id
        self.channel_id = channel_id
        self._http = http
        self._ws: Optional[Any] = None
        self._connected = False
        self._endpoint: Optional[str] = None
        self._session_id: Optional[str] = None
        self._token: Optional[str] = None

    def __repr__(self) -> str:
        return f"<VoiceClient guild_id={self.guild_id} channel_id={self.channel_id} connected={self._connected}>"

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def latency(self) -> float:
        return float("inf")

    async def connect(self, *, timeout: float = 30.0, self_deaf: bool = False, self_mute: bool = False) -> None:
        raise NotImplementedError(
            "Voice is a stub in this version. "
            "Extend VoiceClient with an opus encoder and UDP transport to implement full voice support."
        )

    async def disconnect(self, *, force: bool = False) -> None:
        self._connected = False

    async def move_to(self, channel_id: int) -> None:
        self.channel_id = channel_id

    async def send_audio(self, data: bytes) -> None:
        raise NotImplementedError("Voice audio sending is a stub.")

    def _on_voice_state_update(self, session_id: str) -> None:
        self._session_id = session_id

    def _on_voice_server_update(self, token: str, endpoint: str) -> None:
        self._token = token
        self._endpoint = endpoint
