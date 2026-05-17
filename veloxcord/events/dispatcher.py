from __future__ import annotations
import asyncio
import logging
from typing import Any, Callable, Coroutine, Optional

from .middleware import MiddlewareChain

logger = logging.getLogger("veloxcord.events.dispatcher")

ListenerFunc = Callable[..., Coroutine[Any, Any, None]]


class EventListener:
    __slots__ = ("func", "priority", "once", "event_name")

    def __init__(
        self,
        func: ListenerFunc,
        event_name: str,
        priority: int = 0,
        once: bool = False,
    ) -> None:
        self.func = func
        self.event_name = event_name
        self.priority = priority
        self.once = once

    def __repr__(self) -> str:
        return f"<EventListener event={self.event_name!r} priority={self.priority} once={self.once}>"

    def __lt__(self, other: "EventListener") -> bool:
        return self.priority > other.priority


class EventDispatcher:
    __slots__ = (
        "_listeners",
        "_wildcard_listeners",
        "_middleware",
        "_error_handler",
    )

    def __init__(self) -> None:
        self._listeners: dict[str, list[EventListener]] = {}
        self._wildcard_listeners: list[EventListener] = []
        self._middleware: MiddlewareChain = MiddlewareChain()
        self._error_handler: Optional[Callable[[Exception, EventListener], Coroutine[Any, Any, None]]] = None

    def __repr__(self) -> str:
        total = sum(len(v) for v in self._listeners.values()) + len(self._wildcard_listeners)
        return f"<EventDispatcher listeners={total}>"

    def add_middleware(self, middleware: Any) -> None:
        self._middleware.add(middleware)

    def remove_middleware(self, middleware: Any) -> None:
        self._middleware.remove(middleware)

    def set_error_handler(
        self,
        handler: Callable[[Exception, EventListener], Coroutine[Any, Any, None]],
    ) -> None:
        self._error_handler = handler

    def register(
        self,
        event_name: str,
        func: ListenerFunc,
        *,
        priority: int = 0,
        once: bool = False,
    ) -> EventListener:
        listener = EventListener(func, event_name, priority=priority, once=once)
        if event_name == "*":
            self._wildcard_listeners.append(listener)
            self._wildcard_listeners.sort()
        else:
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            self._listeners[event_name].append(listener)
            self._listeners[event_name].sort()
        return listener

    def unregister(self, listener: EventListener) -> bool:
        if listener.event_name == "*":
            try:
                self._wildcard_listeners.remove(listener)
                return True
            except ValueError:
                return False
        listeners = self._listeners.get(listener.event_name, [])
        try:
            listeners.remove(listener)
            return True
        except ValueError:
            return False

    def unregister_all(self, event_name: str) -> int:
        if event_name == "*":
            count = len(self._wildcard_listeners)
            self._wildcard_listeners.clear()
            return count
        listeners = self._listeners.pop(event_name, [])
        return len(listeners)

    def listeners_for(self, event_name: str) -> list[EventListener]:
        return list(self._listeners.get(event_name, []))

    async def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        listeners = list(self._listeners.get(event_name, []))
        wildcard = list(self._wildcard_listeners)

        async def _fire_all() -> None:
            to_remove: list[EventListener] = []
            all_listeners = sorted(listeners + wildcard)

            async def _invoke(listener: EventListener) -> None:
                try:
                    if listener.event_name == "*":
                        await listener.func(event_name, *args, **kwargs)
                    else:
                        await listener.func(*args, **kwargs)
                except Exception as exc:
                    if self._error_handler:
                        try:
                            await self._error_handler(exc, listener)
                        except Exception:
                            logger.exception(f"Error in error handler for event {event_name!r}")
                    else:
                        logger.exception(f"Unhandled error in listener for {event_name!r}: {exc}")

            tasks = []
            for listener in all_listeners:
                if listener.once:
                    to_remove.append(listener)
                tasks.append(_invoke(listener))

            if tasks:
                await asyncio.gather(*tasks)

            for listener in to_remove:
                self.unregister(listener)

        await self._middleware.run(event_name, args[0] if args else None, _fire_all)

    def on(
        self,
        event_name: str,
        *,
        priority: int = 0,
    ) -> Callable[[ListenerFunc], ListenerFunc]:
        def decorator(func: ListenerFunc) -> ListenerFunc:
            self.register(event_name, func, priority=priority, once=False)
            return func
        return decorator

    def once(
        self,
        event_name: str,
        *,
        priority: int = 0,
    ) -> Callable[[ListenerFunc], ListenerFunc]:
        def decorator(func: ListenerFunc) -> ListenerFunc:
            self.register(event_name, func, priority=priority, once=True)
            return func
        return decorator

    def wildcard(
        self, func: ListenerFunc
    ) -> ListenerFunc:
        self.register("*", func)
        return func

    def wait_for(
        self,
        event_name: str,
        *,
        check: Optional[Callable[..., bool]] = None,
        timeout: Optional[float] = None,
    ) -> asyncio.Future[Any]:
        future: asyncio.Future[Any] = asyncio.get_event_loop().create_future()

        async def _predicate(*args: Any, **kwargs: Any) -> None:
            if future.done():
                return
            value = args[0] if args else None
            if check is None or check(value):
                future.set_result(value)

        listener = self.register(event_name, _predicate, once=True)

        if timeout is not None:
            async def _cancel_on_timeout() -> None:
                await asyncio.sleep(timeout)
                if not future.done():
                    future.set_exception(asyncio.TimeoutError())
                    self.unregister(listener)
            asyncio.create_task(_cancel_on_timeout())

        return future
