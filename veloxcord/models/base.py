from __future__ import annotations
import datetime
from typing import TYPE_CHECKING, Any, Optional

from ..utils import snowflake_time

if TYPE_CHECKING:
    from ..http.client import HTTPClient


class Snowflake:
    __slots__ = ("id",)

    def __init__(self, id: int) -> None:
        self.id = id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def created_at(self) -> datetime.datetime:
        return snowflake_time(self.id)


class DiscordModel(Snowflake):
    __slots__ = ("_http",)

    def __init__(self, id: int, http: "HTTPClient") -> None:
        super().__init__(id)
        self._http = http

    @classmethod
    def _from_data(cls, data: dict[str, Any], http: "HTTPClient") -> "DiscordModel":
        raise NotImplementedError


class Object(Snowflake):
    __slots__ = ()

    def __init__(self, id: int) -> None:
        super().__init__(id)

    @classmethod
    def from_snowflake(cls, snowflake: int) -> "Object":
        return cls(snowflake)
