"""TaHoma scenario (action group) parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class TaHomaScenario:
    """Minimal scenario record from the TaHoma actionGroups API."""

    oid: str
    label: str


def parse_action_group(data: Any) -> TaHomaScenario | None:
    """Parse one actionGroups entry into a TaHomaScenario."""
    if not isinstance(data, Mapping):
        return None

    oid = data.get("oid") or data.get("OID") or data.get("id")
    if oid is None:
        return None

    label = (
        data.get("label")
        or data.get("Label")
        or data.get("name")
        or data.get("Name")
        or str(oid)
    )

    return TaHomaScenario(oid=str(oid), label=str(label).strip() or str(oid))
