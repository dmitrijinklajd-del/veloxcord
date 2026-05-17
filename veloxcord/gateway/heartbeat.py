from __future__ import annotations
import asyncio
import logging
import time
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .connection import GatewayConnection

logger = logging.getLogger("veloxcord.gateway.heartbeat")


class HeartbeatManager:
    __slots__ = (
        "_connection",
        "_interval",
        "_task",
        "_last_sent",
        "_last_ack",
        "_latency",
        "_missed_acks",
        "_running",
    )

    def __init__(self, connection: "GatewayConnection", interval: float) -> None:
        self._connection = connection
        self._interval = interval
        self._task: Optional[asyncio.Task[None]] = None
        self._last_sent: float = 0.0
        self._last_ack: float = 0.0
        self._latency: float = float("inf")
        self._missed_acks: int = 0
        self._running = False

    def __repr__(self) -> str:
        return f"<HeartbeatManager interval={self._interval} latency={self._latency:.2f}ms>"

    @property
    def latency(self) -> float:
        return self._latency

    @property
    def missed_acks(self) -> int:
        return self._missed_acks

    def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run(), name="veloxcord-heartbeat")

    def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()

    def ack(self) -> None:
        self._last_ack = time.monotonic()
        self._latency = (self._last_ack - self._last_sent) * 1000
        self._missed_acks = 0
        logger.debug(f"Heartbeat ACK received. Latency: {self._latency:.2f}ms")

    async def _run(self) -> None:
        import random
        jitter = random.random()
        await asyncio.sleep(self._interval * jitter)

        while self._running:
            if self._last_sent > 0 and self._last_ack < self._last_sent:
                self._missed_acks += 1
                logger.warning(f"Missed heartbeat ACK #{self._missed_acks}")
                if self._missed_acks >= 3:
                    logger.error("Too many missed ACKs — reconnecting")
                    asyncio.create_task(self._connection.reconnect())
                    return

            await self._send()
            await asyncio.sleep(self._interval)

    async def _send(self) -> None:
        self._last_sent = time.monotonic()
        seq = self._connection.sequence
        logger.debug(f"Sending heartbeat (seq={seq})")
        await self._connection.send_heartbeat(seq)
