from __future__ import annotations
import asyncio
import json
import logging
import sys
from typing import Any, Optional

import aiohttp

from .endpoints import Route, Endpoints
from .ratelimit import RateLimitManager
from ..errors import _map_http_status, RateLimited

logger = logging.getLogger("veloxcord.http")

_LIBRARY_VERSION = "1.0.0"


class HTTPClient:
    __slots__ = (
        "_token",
        "_session",
        "_rate_limiter",
        "_user_agent",
        "_connector",
    )

    def __init__(self, token: str) -> None:
        self._token = token
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limiter = RateLimitManager()
        self._user_agent = (
            f"DiscordBot (VeloxCord {_LIBRARY_VERSION}) "
            f"Python/{sys.version_info.major}.{sys.version_info.minor} "
            f"aiohttp/{aiohttp.__version__}"
        )
        self._connector: Optional[aiohttp.TCPConnector] = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._connector = aiohttp.TCPConnector(
                enable_cleanup_closed=True,
                force_close=False,
                limit=100,
            )
            self._session = aiohttp.ClientSession(
                connector=self._connector,
                headers={
                    "Authorization": f"Bot {self._token}",
                    "User-Agent": self._user_agent,
                    "X-RateLimit-Precision": "millisecond",
                },
                json_serialize=json.dumps,
            )
        return self._session

    async def request(
        self,
        route: Route,
        *,
        json_body: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        files: Optional[list[Any]] = None,
        reason: Optional[str] = None,
        retries: int = 5,
    ) -> Any:
        session = await self._ensure_session()
        headers: dict[str, str] = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason

        await self._rate_limiter.acquire(route.bucket_key)

        for attempt in range(retries):
            try:
                kwargs: dict[str, Any] = {"headers": headers, "params": params}
                if files:
                    form = aiohttp.FormData()
                    if json_body:
                        form.add_field("payload_json", json.dumps(json_body), content_type="application/json")
                    for idx, file in enumerate(files):
                        file_bytes = file.read() if hasattr(file, "read") else file.fp
                        form.add_field(
                            f"files[{idx}]",
                            file_bytes,
                            filename=getattr(file, "filename", f"file{idx}"),
                        )
                    kwargs["data"] = form
                elif json_body is not None:
                    kwargs["json"] = json_body

                async with session.request(route.method, route.url, **kwargs) as response:
                    bucket_hash = response.headers.get("X-RateLimit-Bucket")
                    limit = response.headers.get("X-RateLimit-Limit")
                    remaining = response.headers.get("X-RateLimit-Remaining")
                    reset = response.headers.get("X-RateLimit-Reset")
                    reset_after = response.headers.get("X-RateLimit-Reset-After")

                    self._rate_limiter.update_bucket(
                        route.bucket_key, bucket_hash, limit, remaining, reset, reset_after
                    )

                    if response.status == 429:
                        data = await response.json()
                        retry_after = float(data.get("retry_after", 1.0))
                        is_global = data.get("global", False)
                        if is_global:
                            logger.warning(f"Global rate limit hit. Retry after {retry_after}s")
                            self._rate_limiter.trigger_global(retry_after)
                        else:
                            logger.warning(f"Route rate limit hit: {route.bucket_key}. Retry after {retry_after}s")
                        if attempt < retries - 1:
                            await asyncio.sleep(retry_after + 0.1)
                            continue
                        raise RateLimited(retry_after, is_global)

                    if response.status == 204:
                        return None

                    if response.status >= 500 and attempt < retries - 1:
                        wait = (2 ** attempt) * 0.5
                        logger.warning(f"Server error {response.status} on {route.method} {route.path}. Retry in {wait}s")
                        await asyncio.sleep(wait)
                        continue

                    data = None
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        data = await response.json()
                    elif response.status != 204:
                        data = await response.text()

                    if response.ok:
                        return data

                    if isinstance(data, dict):
                        message = data.get("message", str(response.status))
                        code = data.get("code", 0)
                    else:
                        message = str(data or response.status)
                        code = 0
                        data = {}

                    raise _map_http_status(response.status, message, code, data if isinstance(data, dict) else {})

            except (aiohttp.ClientConnectorError, aiohttp.ServerDisconnectedError, asyncio.TimeoutError) as exc:
                if attempt < retries - 1:
                    wait = (2 ** attempt) * 0.5
                    logger.warning(f"Connection error on attempt {attempt + 1}: {exc}. Retry in {wait}s")
                    await asyncio.sleep(wait)
                    continue
                raise

        raise RuntimeError(f"Max retries ({retries}) exhausted for {route.method} {route.path}")

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
        if self._connector:
            await self._connector.close()

    async def get_gateway(self) -> dict[str, Any]:
        return await self.request(Endpoints.get_gateway())

    async def get_gateway_bot(self) -> dict[str, Any]:
        return await self.request(Endpoints.get_gateway_bot())

    async def get_current_user(self) -> dict[str, Any]:
        return await self.request(Endpoints.get_current_user())

    async def get_user(self, user_id: int) -> dict[str, Any]:
        return await self.request(Endpoints.get_user(user_id))

    async def edit_current_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request(Endpoints.edit_current_user(), json_body=payload)

    async def get_current_user_guilds(self, params: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        return await self.request(Endpoints.get_current_user_guilds(), params=params)

    async def leave_guild(self, guild_id: int) -> None:
        await self.request(Endpoints.leave_guild(guild_id))

    async def create_dm(self, recipient_id: int) -> dict[str, Any]:
        return await self.request(Endpoints.create_dm(), json_body={"recipient_id": str(recipient_id)})

    async def get_guild(self, guild_id: int) -> dict[str, Any]:
        return await self.request(Endpoints.get_guild(guild_id), params={"with_counts": "true"})

    async def edit_guild(
        self, guild_id: int, payload: dict[str, Any], *, reason: Optional[str] = None
    ) -> dict[str, Any]:
        return await self.request(Endpoints.edit_guild(guild_id), json_body=payload, reason=reason)

    async def delete_guild(self, guild_id: int) -> None:
        await self.request(Endpoints.delete_guild(guild_id))

    async def get_guild_channels(self, guild_id: int) -> list[dict[str, Any]]:
        return await self.request(Endpoints.get_guild_channels(guild_id))

    async def create_guild_channel(
        self, guild_id: int, payload: dict[str, Any], *, reason: Optional[str] = None
    ) -> dict[str, Any]:
        return await self.request(Endpoints.create_guild_channel(guild_id), json_body=payload, reason=reason)

    async def get_guild_member(self, guild_id: int, user_id: int) -> dict[str, Any]:
        return await self.request(Endpoints.get_guild_member(guild_id, user_id))

    async def list_guild_members(
        self, guild_id: int, *, limit: int = 1000, after: int = 0
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": limit}
        if after:
            params["after"] = after
        return await self.request(Endpoints.list_guild_members(guild_id), params=params)

    async def search_guild_members(
        self, guild_id: int, query: str, *, limit: int = 1
    ) -> list[dict[str, Any]]:
        return await self.request(Endpoints.search_guild_members(guild_id), params={"query": query, "limit": limit})

    async def edit_guild_member(
        self, guild_id: int, user_id: int, payload: dict[str, Any], *, reason: Optional[str] = None
    ) -> dict[str, Any]:
        return await self.request(Endpoints.edit_guild_member(guild_id, user_id), json_body=payload, reason=reason)

    async def remove_guild_member(
        self, guild_id: int, user_id: int, *, reason: Optional[str] = None
    ) -> None:
        await self.request(Endpoints.remove_guild_member(guild_id, user_id), reason=reason)

    async def add_guild_member_role(
        self, guild_id: int, user_id: int, role_id: int, *, reason: Optional[str] = None
    ) -> None:
        await self.request(Endpoints.add_guild_member_role(guild_id, user_id, role_id), reason=reason)

    async def remove_guild_member_role(
        self, guild_id: int, user_id: int, role_id: int, *, reason: Optional[str] = None
    ) -> None:
        await self.request(Endpoints.remove_guild_member_role(guild_id, user_id, role_id), reason=reason)

    async def create_guild_ban(
        self, guild_id: int, user_id: int, *, delete_message_seconds: int = 0, reason: Optional[str] = None
    ) -> None:
        payload: dict[str, Any] = {"delete_message_seconds": delete_message_seconds}
        await self.request(Endpoints.create_guild_ban(guild_id, user_id), json_body=payload, reason=reason)

    async def remove_guild_ban(
        self, guild_id: int, user_id: int, *, reason: Optional[str] = None
    ) -> None:
        await self.request(Endpoints.remove_guild_ban(guild_id, user_id), reason=reason)

    async def get_guild_roles(self, guild_id: int) -> list[dict[str, Any]]:
        return await self.request(Endpoints.get_guild_roles(guild_id))

    async def create_guild_role(
        self, guild_id: int, payload: dict[str, Any], *, reason: Optional[str] = None
    ) -> dict[str, Any]:
        return await self.request(Endpoints.create_guild_role(guild_id), json_body=payload, reason=reason)

    async def edit_guild_role(
        self, guild_id: int, role_id: int, payload: dict[str, Any], *, reason: Optional[str] = None
    ) -> dict[str, Any]:
        return await self.request(Endpoints.edit_guild_role(guild_id, role_id), json_body=payload, reason=reason)

    async def delete_guild_role(
        self, guild_id: int, role_id: int, *, reason: Optional[str] = None
    ) -> None:
        await self.request(Endpoints.delete_guild_role(guild_id, role_id), reason=reason)

    async def get_guild_emojis(self, guild_id: int) -> list[dict[str, Any]]:
        return await self.request(Endpoints.get_guild_emojis(guild_id))

    async def edit_guild_emoji(
        self, guild_id: int, emoji_id: int, payload: dict[str, Any], *, reason: Optional[str] = None
    ) -> dict[str, Any]:
        return await self.request(Endpoints.edit_guild_emoji(guild_id, emoji_id), json_body=payload, reason=reason)

    async def delete_guild_emoji(
        self, guild_id: int, emoji_id: int, *, reason: Optional[str] = None
    ) -> None:
        await self.request(Endpoints.delete_guild_emoji(guild_id, emoji_id), reason=reason)

    async def get_channel(self, channel_id: int) -> dict[str, Any]:
        return await self.request(Endpoints.get_channel(channel_id))

    async def edit_channel(
        self, channel_id: int, payload: dict[str, Any], *, reason: Optional[str] = None
    ) -> dict[str, Any]:
        return await self.request(Endpoints.edit_channel(channel_id), json_body=payload, reason=reason)

    async def delete_channel(
        self, channel_id: int, *, reason: Optional[str] = None
    ) -> dict[str, Any]:
        return await self.request(Endpoints.delete_channel(channel_id), reason=reason)

    async def get_channel_messages(
        self, channel_id: int, params: Optional[dict[str, Any]] = None
    ) -> list[dict[str, Any]]:
        return await self.request(Endpoints.get_channel_messages(channel_id), params=params)

    async def get_channel_message(self, channel_id: int, message_id: int) -> dict[str, Any]:
        return await self.request(Endpoints.get_channel_message(channel_id, message_id))

    async def create_message(
        self,
        channel_id: int,
        payload: dict[str, Any],
        *,
        files: Optional[list[Any]] = None,
    ) -> dict[str, Any]:
        return await self.request(
            Endpoints.create_message(channel_id), json_body=payload, files=files
        )

    async def edit_message(
        self, channel_id: int, message_id: int, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return await self.request(Endpoints.edit_message(channel_id, message_id), json_body=payload)

    async def delete_message(
        self, channel_id: int, message_id: int, *, reason: Optional[str] = None
    ) -> None:
        await self.request(Endpoints.delete_message(channel_id, message_id), reason=reason)

    async def bulk_delete_messages(
        self, channel_id: int, message_ids: list[int], *, reason: Optional[str] = None
    ) -> None:
        await self.request(
            Endpoints.bulk_delete_messages(channel_id),
            json_body={"messages": [str(mid) for mid in message_ids]},
            reason=reason,
        )

    async def crosspost_message(self, channel_id: int, message_id: int) -> dict[str, Any]:
        return await self.request(Endpoints.crosspost_message(channel_id, message_id))

    async def create_reaction(self, channel_id: int, message_id: int, emoji: str) -> None:
        await self.request(Endpoints.create_reaction(channel_id, message_id, emoji))

    async def delete_own_reaction(self, channel_id: int, message_id: int, emoji: str) -> None:
        await self.request(Endpoints.delete_own_reaction(channel_id, message_id, emoji))

    async def delete_user_reaction(
        self, channel_id: int, message_id: int, emoji: str, user_id: int
    ) -> None:
        await self.request(Endpoints.delete_user_reaction(channel_id, message_id, emoji, user_id))

    async def delete_all_reactions(self, channel_id: int, message_id: int) -> None:
        await self.request(Endpoints.delete_all_reactions(channel_id, message_id))

    async def get_pinned_messages(self, channel_id: int) -> list[dict[str, Any]]:
        return await self.request(Endpoints.get_pinned_messages(channel_id))

    async def pin_message(
        self, channel_id: int, message_id: int, *, reason: Optional[str] = None
    ) -> None:
        await self.request(Endpoints.pin_message(channel_id, message_id), reason=reason)

    async def unpin_message(
        self, channel_id: int, message_id: int, *, reason: Optional[str] = None
    ) -> None:
        await self.request(Endpoints.unpin_message(channel_id, message_id), reason=reason)

    async def trigger_typing_indicator(self, channel_id: int) -> None:
        await self.request(Endpoints.trigger_typing_indicator(channel_id))

    async def create_channel_invite(
        self, channel_id: int, payload: dict[str, Any], *, reason: Optional[str] = None
    ) -> dict[str, Any]:
        return await self.request(Endpoints.create_channel_invite(channel_id), json_body=payload, reason=reason)

    async def delete_invite(self, code: str, *, reason: Optional[str] = None) -> None:
        await self.request(Endpoints.delete_invite(code), reason=reason)

    async def execute_webhook(
        self,
        webhook_id: int,
        token: str,
        payload: dict[str, Any],
        *,
        params: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        return await self.request(
            Endpoints.execute_webhook(webhook_id, token), json_body=payload, params=params
        )

    async def edit_webhook(
        self,
        webhook_id: int,
        payload: dict[str, Any],
        *,
        token: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> dict[str, Any]:
        route = (
            Endpoints.edit_webhook_with_token(webhook_id, token)
            if token
            else Endpoints.edit_webhook(webhook_id)
        )
        return await self.request(route, json_body=payload, reason=reason)

    async def delete_webhook(
        self,
        webhook_id: int,
        *,
        token: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        route = (
            Endpoints.delete_webhook_with_token(webhook_id, token)
            if token
            else Endpoints.delete_webhook(webhook_id)
        )
        await self.request(route, reason=reason)

    async def create_interaction_response(
        self, interaction_id: int, token: str, payload: dict[str, Any]
    ) -> None:
        await self.request(
            Endpoints.create_interaction_response(interaction_id, token), json_body=payload
        )

    async def edit_original_interaction_response(
        self, application_id: int, token: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return await self.request(
            Endpoints.edit_original_interaction_response(application_id, token), json_body=payload
        )

    async def delete_original_interaction_response(
        self, application_id: int, token: str
    ) -> None:
        await self.request(Endpoints.delete_original_interaction_response(application_id, token))

    async def create_followup_message(
        self, application_id: int, token: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return await self.request(
            Endpoints.create_followup_message(application_id, token), json_body=payload
        )

    async def get_global_application_commands(
        self, application_id: int
    ) -> list[dict[str, Any]]:
        return await self.request(Endpoints.get_global_application_commands(application_id))

    async def create_global_application_command(
        self, application_id: int, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return await self.request(
            Endpoints.create_global_application_command(application_id), json_body=payload
        )

    async def bulk_overwrite_global_application_commands(
        self, application_id: int, commands: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        return await self.request(
            Endpoints.bulk_overwrite_global_application_commands(application_id), json_body=commands
        )

    async def bulk_overwrite_guild_application_commands(
        self, application_id: int, guild_id: int, commands: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        return await self.request(
            Endpoints.bulk_overwrite_guild_application_commands(application_id, guild_id),
            json_body=commands,
        )

    async def get_current_application(self) -> dict[str, Any]:
        return await self.request(Endpoints.get_current_application())

    async def edit_guild_scheduled_event(
        self, guild_id: int, event_id: int, payload: dict[str, Any], *, reason: Optional[str] = None
    ) -> dict[str, Any]:
        return await self.request(
            Endpoints.edit_guild_scheduled_event(guild_id, event_id), json_body=payload, reason=reason
        )

    async def delete_guild_scheduled_event(self, guild_id: int, event_id: int) -> None:
        await self.request(Endpoints.delete_guild_scheduled_event(guild_id, event_id))

    async def edit_stage_instance(
        self, channel_id: int, payload: dict[str, Any], *, reason: Optional[str] = None
    ) -> dict[str, Any]:
        return await self.request(Endpoints.edit_stage_instance(channel_id), json_body=payload, reason=reason)

    async def delete_stage_instance(
        self, channel_id: int, *, reason: Optional[str] = None
    ) -> None:
        await self.request(Endpoints.delete_stage_instance(channel_id), reason=reason)

    async def join_thread(self, channel_id: int) -> None:
        await self.request(Endpoints.join_thread(channel_id))

    async def leave_thread(self, channel_id: int) -> None:
        await self.request(Endpoints.leave_thread(channel_id))

    async def add_thread_member(self, channel_id: int, user_id: int) -> None:
        await self.request(Endpoints.add_thread_member(channel_id, user_id))

    async def remove_thread_member(self, channel_id: int, user_id: int) -> None:
        await self.request(Endpoints.remove_thread_member(channel_id, user_id))

    async def list_thread_members(self, channel_id: int) -> list[dict[str, Any]]:
        return await self.request(Endpoints.list_thread_members(channel_id))
