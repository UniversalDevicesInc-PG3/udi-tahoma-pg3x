"""TaHoma scenario (action group) parsing helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class TaHomaScenario:
    """Minimal scenario record from the TaHoma actionGroups API."""

    oid: str
    label: str


def _extract_oid(data: Mapping[str, Any]) -> str | None:
    oid = data.get("oid") or data.get("OID") or data.get("id")
    if oid is None:
        return None
    return str(oid)


def _extract_label(data: Mapping[str, Any]) -> str | None:
    for key in ("label", "Label", "name", "Name"):
        value = data.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def has_user_label(label: str, oid: str) -> bool:
    """Return True when label is a user-visible TaHoma scenario name."""
    if not label or not label.strip():
        return False
    label = label.strip()
    if label == oid:
        return False
    if _UUID_RE.match(label):
        return False
    return True


def parse_action_group(data: Any) -> TaHomaScenario | None:
    """Parse one actionGroups entry into a TaHomaScenario.

    Returns None for orphan/internal action groups with no user-facing label.
    TaHoma often keeps deleted or system actionGroups in the API with blank labels.
    """
    if not isinstance(data, Mapping):
        return None

    oid = _extract_oid(data)
    if oid is None:
        return None

    label = _extract_label(data)
    if label is None or not has_user_label(label, oid):
        return None

    return TaHomaScenario(oid=oid, label=label)


def scenario_oid_to_address(scenario_oid: str) -> str:
    """Convert a TaHoma scenario OID to a valid Polyglot node address.

    Polyglot node addresses are limited to 14 alphanumeric/underscore characters.
    """
    hex_id = "".join(c for c in str(scenario_oid).lower() if c.isalnum())
    suffix = hex_id[:10] if hex_id else "0"
    return f"sc{suffix}"[:14]
