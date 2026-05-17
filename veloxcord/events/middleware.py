from __future__ import annotations
import asyncio
from typing import Any, Awaitable, Callable, Optional

MiddlewareFunc = Callable[[str, Any, Callable[[], Awaitable[None]]], Awaitable[None]]


class MiddlewareChain:
    __slots__ = ("_middlewares",)

    def __init__(self) -> None:
        self._middlewares: list[MiddlewareFunc] = []

    def __repr__(self) -> str:
        return f"<MiddlewareChain count={len(self._middlewares)}>"

    def add(self, middleware: MiddlewareFunc) -> None:
        self._middlewares.append(middleware)

    def remove(self, middleware: MiddlewareFunc) -> None:
        try:
            self._middlewares.remove(middleware)
        except ValueError:
            pass

    async def run(
        self,
        event_name: str,
        payload: Any,
        final: Callable[[], Awaitable[None]],
    ) -> None:
        if not self._middlewares:
            await final()
            return

        index = 0
        middlewares = self._middlewares[:]

        async def next_middleware() -> None:
            nonlocal index
            if index < len(middlewares):
                current = middlewares[index]
                index += 1
                await current(event_name, payload, next_middleware)
            else:
                await final()

        await next_middleware()


class LoggingMiddleware:
    __slots__ = ("_logger",)

    def __init__(self) -> None:
        import logging
        self._logger = logging.getLogger("veloxcord.events.middleware")

    async def __call__(
        self,
        event_name: str,
        payload: Any,
        next_func: Callable[[], Awaitable[None]],
    ) -> None:
        self._logger.debug(f"Event middleware: {event_name}")
        await next_func()


class FilterMiddleware:
    __slots__ = ("_predicate",)

    def __init__(self, predicate: Callable[[str, Any], bool]) -> None:
        self._predicate = predicate

    async def __call__(
        self,
        event_name: str,
        payload: Any,
        next_func: Callable[[], Awaitable[None]],
    ) -> None:
        if self._predicate(event_name, payload):
            await next_func()
