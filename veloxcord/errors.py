from __future__ import annotations
from typing import Any, Optional


class VeloxException(Exception):
    __slots__ = ("message",)

    def __init__(self, message: str = "") -> None:
        self.message = message
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"


class HTTPException(VeloxException):
    __slots__ = ("status", "code", "message", "response_data")

    def __init__(
        self,
        status: int,
        message: str = "",
        code: int = 0,
        response_data: Optional[dict[str, Any]] = None,
    ) -> None:
        self.status = status
        self.code = code
        self.response_data = response_data or {}
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(status={self.status}, code={self.code}, message={self.message!r})"


class NotFound(HTTPException):
    __slots__ = ()

    def __init__(
        self,
        message: str = "Not found",
        code: int = 0,
        response_data: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(404, message, code, response_data)


class Forbidden(HTTPException):
    __slots__ = ()

    def __init__(
        self,
        message: str = "Forbidden",
        code: int = 0,
        response_data: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(403, message, code, response_data)


class Unauthorized(HTTPException):
    __slots__ = ()

    def __init__(
        self,
        message: str = "Unauthorized",
        code: int = 0,
        response_data: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(401, message, code, response_data)


class BadRequest(HTTPException):
    __slots__ = ()

    def __init__(
        self,
        message: str = "Bad request",
        code: int = 0,
        response_data: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(400, message, code, response_data)


class RateLimited(HTTPException):
    __slots__ = ("retry_after", "is_global")

    def __init__(
        self,
        retry_after: float,
        is_global: bool = False,
        message: str = "Rate limited",
    ) -> None:
        self.retry_after = retry_after
        self.is_global = is_global
        super().__init__(429, message, 0, {})

    def __repr__(self) -> str:
        return f"RateLimited(retry_after={self.retry_after}, is_global={self.is_global})"


class ServerError(HTTPException):
    __slots__ = ()

    def __init__(
        self,
        status: int,
        message: str = "Internal server error",
        code: int = 0,
        response_data: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(status, message, code, response_data)


class GatewayException(VeloxException):
    __slots__ = ("code",)

    def __init__(self, message: str = "", code: Optional[int] = None) -> None:
        self.code = code
        super().__init__(message)

    def __repr__(self) -> str:
        return f"GatewayException(code={self.code}, message={self.message!r})"


class AuthenticationFailed(GatewayException):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("Authentication failed — invalid token", 4004)


class DisallowedIntents(GatewayException):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("Disallowed intents — enable them in the developer portal", 4014)


class ShardingRequired(GatewayException):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("Sharding is required for this bot", 4011)


class InvalidShard(GatewayException):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("Invalid shard", 4010)


class CommandException(VeloxException):
    __slots__ = ()


class CommandNotFound(CommandException):
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Command '{name}' not found")


class CommandOnCooldown(CommandException):
    __slots__ = ("retry_after",)

    def __init__(self, retry_after: float) -> None:
        self.retry_after = retry_after
        super().__init__(f"Command on cooldown. Retry after {retry_after:.2f}s")


class MissingPermissions(CommandException):
    __slots__ = ("missing",)

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(f"Missing permissions: {', '.join(missing)}")


class BotMissingPermissions(CommandException):
    __slots__ = ("missing",)

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(f"Bot missing permissions: {', '.join(missing)}")


class CheckFailure(CommandException):
    __slots__ = ()


class InvalidArgument(CommandException):
    __slots__ = ()


class CacheException(VeloxException):
    __slots__ = ()


def _map_http_status(
    status: int,
    message: str,
    code: int,
    response_data: dict[str, Any],
) -> HTTPException:
    match status:
        case 400:
            return BadRequest(message, code, response_data)
        case 401:
            return Unauthorized(message, code, response_data)
        case 403:
            return Forbidden(message, code, response_data)
        case 404:
            return NotFound(message, code, response_data)
        case 429:
            retry_after = float(response_data.get("retry_after", 1.0))
            is_global = bool(response_data.get("global", False))
            return RateLimited(retry_after, is_global, message)
        case _ if status >= 500:
            return ServerError(status, message, code, response_data)
        case _:
            return HTTPException(status, message, code, response_data)
