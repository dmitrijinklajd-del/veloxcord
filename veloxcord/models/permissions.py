from __future__ import annotations
from typing import Any

from ..flags import Permissions
from ..enums import OverwriteType


class PermissionOverwrite:
    __slots__ = ("id", "type", "allow", "deny")

    def __init__(
        self,
        id: int,
        type: OverwriteType,
        allow: Permissions,
        deny: Permissions,
    ) -> None:
        self.id = id
        self.type = type
        self.allow = allow
        self.deny = deny

    def __repr__(self) -> str:
        return f"<PermissionOverwrite id={self.id} type={self.type} allow={self.allow.value} deny={self.deny.value}>"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PermissionOverwrite):
            return (
                self.id == other.id
                and self.type == other.type
                and self.allow.value == other.allow.value
                and self.deny.value == other.deny.value
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.id, self.type))

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> "PermissionOverwrite":
        return cls(
            id=int(data["id"]),
            type=OverwriteType(data["type"]),
            allow=Permissions(int(data.get("allow", 0))),
            deny=Permissions(int(data.get("deny", 0))),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "type": self.type.value,
            "allow": str(self.allow.value),
            "deny": str(self.deny.value),
        }


def resolve_permissions(
    base: Permissions,
    overwrites: list[PermissionOverwrite],
    role_ids: list[int],
    member_id: int,
) -> Permissions:
    if base.administrator:
        return Permissions.all()

    permissions = Permissions(base.value)

    everyone_overwrite = next((o for o in overwrites if o.id == member_id and o.type == OverwriteType.ROLE), None)
    if everyone_overwrite is None:
        for overwrite in overwrites:
            if overwrite.type == OverwriteType.ROLE and overwrite.id not in role_ids and overwrite.id != member_id:
                continue
    role_allow = Permissions(0)
    role_deny = Permissions(0)
    for overwrite in overwrites:
        if overwrite.type == OverwriteType.ROLE and overwrite.id in role_ids:
            role_allow.add(overwrite.allow)
            role_deny.add(overwrite.deny)

    permissions.remove(role_deny)
    permissions.add(role_allow)

    for overwrite in overwrites:
        if overwrite.type == OverwriteType.MEMBER and overwrite.id == member_id:
            permissions.remove(overwrite.deny)
            permissions.add(overwrite.allow)
            break

    return permissions
