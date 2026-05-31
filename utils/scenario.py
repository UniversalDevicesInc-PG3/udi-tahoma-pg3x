"""TaHoma scenario (action group) parsing helpers.

TaHoma app scenes are discovered from the local actionGroups API. Running them
from ISY usually requires optional Somfy cloud credentials — see POLYGLOT_CONFIG.md.
"""

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


_RTS_COMMANDS_WITHOUT_DURATION = frozenset(
    {
        "identify",
        "off",
        "on",
        "onwithtimer",
        "test",
        "tiltpositive",
        "tiltnegative",
    }
)


def extract_action_group_actions(group: Any) -> list[Any]:
    """Return the actions list from an actionGroup record (several API shapes)."""
    if not isinstance(group, Mapping):
        return []

    for key in ("actions", "Actions"):
        value = group.get(key)
        if isinstance(value, list):
            return value

    nested = group.get("actionGroup") or group.get("ActionGroup")
    if isinstance(nested, Mapping):
        return extract_action_group_actions(nested)

    return []


def _normalize_command(device_url: str, cmd: Any) -> dict[str, Any] | None:
    if isinstance(cmd, Mapping):
        name = cmd.get("name")
        if not name:
            return None
        parameters = list(cmd.get("parameters") or [])
    elif isinstance(cmd, str) and cmd:
        name = cmd
        parameters = []
    else:
        return None

    if (
        str(device_url).startswith("rts://")
        and str(name).lower() not in _RTS_COMMANDS_WITHOUT_DURATION
        and (not parameters or parameters[-1] != 0)
    ):
        parameters = [*parameters, 0]

    return {"name": str(name), "parameters": parameters}


def action_group_exec_payload(
    label: str, actions: Any
) -> dict[str, Any] | None:
    """Build a local API exec/apply payload from a persisted actionGroup.

    TaHoma Developer Mode local API runs scenes via POST exec/apply, not exec/{oid}.
    """
    if not isinstance(actions, list):
        return None

    normalized_actions: list[dict[str, Any]] = []
    for action in actions:
        if not isinstance(action, Mapping):
            continue
        device_url = action.get("deviceURL") or action.get("device_url")
        raw_commands = action.get("commands") or action.get("Commands") or []
        if not device_url or not raw_commands:
            continue

        commands: list[dict[str, Any]] = []
        for cmd in raw_commands:
            normalized = _normalize_command(str(device_url), cmd)
            if normalized:
                commands.append(normalized)

        if commands:
            normalized_actions.append(
                {"deviceURL": str(device_url), "commands": commands}
            )

    if not normalized_actions:
        return None

    return {"label": label or "Polyglot Scene", "actions": normalized_actions}


def scenario_oid_to_address(scenario_oid: str) -> str:
    """Convert a TaHoma scenario OID to a valid Polyglot node address.

    Polyglot node addresses are limited to 14 alphanumeric/underscore characters.
    """
    hex_id = "".join(c for c in str(scenario_oid).lower() if c.isalnum())
    suffix = hex_id[:10] if hex_id else "0"
    return f"sc{suffix}"[:14]
