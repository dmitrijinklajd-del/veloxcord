from __future__ import annotations
import asyncio
import json
import logging
import random
from typing import TYPE_CHECKING, Any, Optional

import aiohttp

from .heartbeat import HeartbeatManager
from ..enums import OpCode
from ..errors import AuthenticationFailed, DisallowedIntents, ShardingRequired, InvalidShard, GatewayException

if TYPE_CHECKING:
    from ..client import Client

logger = logging.getLogger("veloxcord.gateway")

GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
CLOSE_CODES_RECONNECT = {4000, 4001, 4002, 4003, 4005, 4007, 4008, 4009}
CLOSE_CODES_FATAL = {4004, 4010, 4011, 4012, 4013, 4014}


class GatewayConnection:
    __slots__ = (
        "_client",
        "_ws",
        "_session",
        "_heartbeat",
        "sequence",
        "session_id",
        "resume_url",
        "_shard_id",
        "_shard_count",
        "_reconnect_attempt",
        "_running",
        "_identified",
    )

    def __init__(
        self,
        client: "Client",
        shard_id: int = 0,
        shard_count: int = 1,
    ) -> None:
        self._client = client
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._heartbeat: Optional[HeartbeatManager] = None
        self.sequence: Optional[int] = None
        self.session_id: Optional[str] = None
        self.resume_url: Optional[str] = None
        self._shard_id = shard_id
        self._shard_count = shard_count
        self._reconnect_attempt = 0
        self._running = False
        self._identified = False

    def __repr__(self) -> str:
        return f"<GatewayConnection shard={self._shard_id}/{self._shard_count} session={self.session_id!r}>"

    @property
    def latency(self) -> float:
        if self._heartbeat is None:
            return float("inf")
        return self._heartbeat.latency

    async def connect(self, *, resume: bool = False) -> None:
        self._running = True
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

        url = self.resume_url if (resume and self.resume_url) else GATEWAY_URL
        logger.info(f"Shard {self._shard_id}: Connecting to gateway at {url}")

        try:
            self._ws = await self._session.ws_connect(
                url,
                compress=0,
                heartbeat=None,
                max_msg_size=0,
            )
            self._reconnect_attempt = 0
            await self._run_loop(resume=resume)
        except aiohttp.ClientConnectorError as exc:
            logger.error(f"Shard {self._shard_id}: Failed to connect: {exc}")
            await self._schedule_reconnect()

    async def _run_loop(self, *, resume: bool = False) -> None:
        if resume and self.session_id and self.sequence is not None:
            await self._send_resume()
        async for message in self._ws:
            if message.type == aiohttp.WSMsgType.TEXT:
                await self._handle_raw(message.data)
            elif message.type == aiohttp.WSMsgType.BINARY:
                await self._handle_raw(message.data.decode("utf-8"))
            elif message.type == aiohttp.WSMsgType.CLOSE:
                code = self._ws.close_code
                logger.warning(f"Shard {self._shard_id}: WebSocket closed with code {code}")
                await self._handle_close(code)
                return
            elif message.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSED):
                logger.error(f"Shard {self._shard_id}: WebSocket error: {message.data}")
                await self._schedule_reconnect()
                return

    async def _handle_raw(self, data: str) -> None:
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            logger.error(f"Shard {self._shard_id}: Failed to decode gateway payload")
            return
        await self._handle_payload(payload)

    async def _handle_payload(self, payload: dict[str, Any]) -> None:
        op = OpCode(payload["op"])
        sequence = payload.get("s")
        if sequence is not None:
            self.sequence = sequence

        match op:
            case OpCode.DISPATCH:
                event_name = payload.get("t")
                event_data = payload.get("d", {})
                logger.debug(f"Shard {self._shard_id}: DISPATCH {event_name}")
                await self._client._handle_event(event_name, event_data)

            case OpCode.HEARTBEAT:
                logger.debug(f"Shard {self._shard_id}: Server requested heartbeat")
                await self.send_heartbeat(self.sequence)

            case OpCode.RECONNECT:
                logger.info(f"Shard {self._shard_id}: Server requested reconnect")
                await self.reconnect()

            case OpCode.INVALID_SESSION:
                resumable = payload.get("d", False)
                logger.warning(f"Shard {self._shard_id}: Invalid session (resumable={resumable})")
                if not resumable:
                    self.session_id = None
                    self.sequence = None
                    self.resume_url = None
                wait = random.uniform(1.0, 5.0)
                await asyncio.sleep(wait)
                await self.connect(resume=resumable)

            case OpCode.HELLO:
                heartbeat_interval = payload["d"]["heartbeat_interval"] / 1000.0
                logger.info(f"Shard {self._shard_id}: Hello received, interval={heartbeat_interval}s")
                if self._heartbeat:
                    self._heartbeat.stop()
                self._heartbeat = HeartbeatManager(self, heartbeat_interval)
                self._heartbeat.start()
                if self.session_id is None:
                    await self._send_identify()

            case OpCode.HEARTBEAT_ACK:
                if self._heartbeat:
                    self._heartbeat.ack()

            case _:
                logger.debug(f"Shard {self._shard_id}: Unhandled opcode: {op}")

    async def _handle_close(self, code: Optional[int]) -> None:
        if self._heartbeat:
            self._heartbeat.stop()

        if code is None:
            await self._schedule_reconnect()
            return

        match code:
            case 4004:
                raise AuthenticationFailed()
            case 4010:
                raise InvalidShard()
            case 4011:
                raise ShardingRequired()
            case 4014:
                raise DisallowedIntents()
            case _ if code in CLOSE_CODES_FATAL:
                raise GatewayException(f"Fatal gateway close code: {code}", code)
            case _:
                await self._schedule_reconnect(resume=code not in (1000, 1001))

    async def _schedule_reconnect(self, *, resume: bool = True) -> None:
        if not self._running:
            return
        self._reconnect_attempt += 1
        base = min(2 ** (self._reconnect_attempt - 1), 32)
        jitter = random.uniform(0, base * 0.1)
        wait = base + jitter
        logger.info(f"Shard {self._shard_id}: Reconnecting in {wait:.2f}s (attempt {self._reconnect_attempt})")
        await asyncio.sleep(wait)
        await self.connect(resume=resume)

    async def reconnect(self) -> None:
        if self._ws and not self._ws.closed:
            await self._ws.close(code=4000)
        await self._schedule_reconnect(resume=True)

    async def disconnect(self) -> None:
        self._running = False
        if self._heartbeat:
            self._heartbeat.stop()
        if self._ws and not self._ws.closed:
            await self._ws.close(code=1000)
        if self._session and not self._session.closed:
            await self._session.close()

    async def send(self, payload: dict[str, Any]) -> None:
        if self._ws is None or self._ws.closed:
            logger.warning(f"Shard {self._shard_id}: Cannot send — WebSocket not connected")
            return
        await self._ws.send_str(json.dumps(payload))

    async def send_heartbeat(self, sequence: Optional[int]) -> None:
        await self.send({"op": OpCode.HEARTBEAT.value, "d": sequence})

    async def _send_identify(self) -> None:
        intents = self._client.intents.value
        payload = {
            "op": OpCode.IDENTIFY.value,
            "d": {
                "token": self._client._http._token,
                "intents": intents,
                "properties": {
                    "os": "linux",
                    "browser": "veloxcord",
                    "device": "veloxcord",
                },
                "compress": False,
                "large_threshold": 250,
                "shard": [self._shard_id, self._shard_count],
                "presence": self._client._presence_payload(),
            },
        }
        logger.info(f"Shard {self._shard_id}: Identifying with intents={intents}")
        await self.send(payload)
        self._identified = True

    async def _send_resume(self) -> None:
        payload = {
            "op": OpCode.RESUME.value,
            "d": {
                "token": self._client._http._token,
                "session_id": self.session_id,
                "seq": self.sequence,
            },
        }
        logger.info(f"Shard {self._shard_id}: Resuming session {self.session_id}")
        await self.send(payload)

    async def update_presence(self, presence: dict[str, Any]) -> None:
        await self.send({"op": OpCode.PRESENCE_UPDATE.value, "d": presence})

    async def request_guild_members(
        self,
        guild_id: int,
        *,
        query: str = "",
        limit: int = 0,
        presences: bool = False,
        user_ids: Optional[list[int]] = None,
    ) -> None:
        payload: dict[str, Any] = {
            "guild_id": str(guild_id),
            "query": query,
            "limit": limit,
            "presences": presences,
        }
        if user_ids:
            payload["user_ids"] = [str(uid) for uid in user_ids]
        await self.send({"op": OpCode.REQUEST_GUILD_MEMBERS.value, "d": payload})
