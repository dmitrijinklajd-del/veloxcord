from __future__ import annotations
import asyncio
import logging
from typing import TYPE_CHECKING, Optional

from .connection import GatewayConnection

if TYPE_CHECKING:
    from ..client import Client

logger = logging.getLogger("veloxcord.gateway.sharding")


class ShardManager:
    __slots__ = ("_client", "_shards", "_shard_count", "_max_concurrency")

    def __init__(
        self,
        client: "Client",
        shard_count: int = 1,
        max_concurrency: int = 1,
    ) -> None:
        self._client = client
        self._shards: dict[int, GatewayConnection] = {}
        self._shard_count = shard_count
        self._max_concurrency = max_concurrency

    def __repr__(self) -> str:
        return f"<ShardManager shards={len(self._shards)}/{self._shard_count}>"

    @property
    def shards(self) -> dict[int, GatewayConnection]:
        return self._shards

    @property
    def latency(self) -> float:
        if not self._shards:
            return float("inf")
        latencies = [s.latency for s in self._shards.values() if s.latency != float("inf")]
        return sum(latencies) / len(latencies) if latencies else float("inf")

    def get_shard(self, shard_id: int) -> Optional[GatewayConnection]:
        return self._shards.get(shard_id)

    def get_shard_for_guild(self, guild_id: int) -> Optional[GatewayConnection]:
        shard_id = (guild_id >> 22) % self._shard_count
        return self._shards.get(shard_id)

    async def launch_shards(self) -> None:
        logger.info(f"Launching {self._shard_count} shard(s) with concurrency {self._max_concurrency}")
        shard_ids = list(range(self._shard_count))
        batches = [
            shard_ids[i : i + self._max_concurrency]
            for i in range(0, len(shard_ids), self._max_concurrency)
        ]
        for batch in batches:
            tasks = []
            for shard_id in batch:
                shard = GatewayConnection(self._client, shard_id, self._shard_count)
                self._shards[shard_id] = shard
                tasks.append(asyncio.create_task(shard.connect(), name=f"veloxcord-shard-{shard_id}"))
            if len(batches) > 1:
                await asyncio.sleep(5.0)

    async def disconnect_all(self) -> None:
        tasks = [shard.disconnect() for shard in self._shards.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
        self._shards.clear()

    async def reconnect_shard(self, shard_id: int) -> None:
        shard = self._shards.get(shard_id)
        if shard:
            await shard.reconnect()
