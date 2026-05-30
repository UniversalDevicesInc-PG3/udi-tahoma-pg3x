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


def scenario_oid_to_address(scenario_oid: str) -> str:
    """Convert a TaHoma scenario OID to a valid Polyglot node address.

    Polyglot node addresses are limited to 14 alphanumeric/underscore characters.
    """
    hex_id = "".join(c for c in str(scenario_oid).lower() if c.isalnum())
    suffix = hex_id[:10] if hex_id else "0"
    return f"sc{suffix}"[:14]
