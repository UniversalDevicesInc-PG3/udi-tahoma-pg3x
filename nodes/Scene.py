"""Somfy TaHoma Scenario node for Polyglot v3.

TaHoma **app scenes** (Morning, All Close, etc.) appear as Scenario nodes with
Activate and Last Command (GV7). This is **optional**: shade control works
without Somfy cloud credentials.

On most gateways the local Developer Mode API does not include scene device
commands, so **Activate uses Somfy cloud** when you set tahoma_cloud_email and
tahoma_cloud_password in Polyglot. Leave those fields empty to skip cloud
entirely — scene nodes may still appear at discovery but Activate is a no-op.

(C) 2025 Stephen Jenkins
"""

import asyncio

import udi_interface

from utils.exec_status import (
    LAST_CMD_COMPLETED,
    LAST_CMD_FAILED,
    LAST_CMD_NONE,
    LAST_CMD_PENDING,
)

LOGGER = udi_interface.LOGGER

SCENE_DRIVERS = [
    {"driver": "GV0", "value": 0, "uom": 107, "name": "Scene Id"},
    {"driver": "GV7", "value": LAST_CMD_NONE, "uom": 25, "name": "Last Command"},
]


class Scene(udi_interface.Node):
    """TaHoma app scene node: optional Activate via Somfy cloud; Last Command (GV7)."""

    id = "sceneid"

    def __init__(self, poly, primary, address, name, sid=None):
        super().__init__(poly, primary, address, name)
        self.poly = poly
        self.primary = primary
        self.controller = poly.getNode(self.primary)
        self.address = address
        self.name = name
        self.sid = sid
        self.lpfx = f"{address}:{name}"

        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)

    def start(self):
        oid_key = f"scenario_oid_{self.address}"
        if oid_key in self.controller.Data:
            self.sid = self.controller.Data[oid_key]
            LOGGER.info(f"{self.lpfx}: Restored scenario OID: {self.sid}")
        elif self.sid:
            self.controller.Data[oid_key] = self.sid
        else:
            LOGGER.error(
                f"{self.lpfx}: Could not recover scenario OID - not in custom data"
            )

        if self.sid:
            scenario_id_num = abs(hash(self.sid)) % 9999999
            self.setDriver("GV0", scenario_id_num)

        self.controller.ready_event.wait()
        self._sync_label_from_controller()

    def poll(self, flag):
        if not self.controller.ready_event.is_set():
            return
        if "shortPoll" in flag:
            LOGGER.debug(f"shortPoll scene {self.lpfx}")

    def _sync_label_from_controller(self):
        entry = self.controller.scenarios_map.get(self.sid)
        if not entry:
            return
        label = entry.get("label") or entry.get("name")
        if label and self.name != label:
            LOGGER.info(f"Scene rename {self.sid}: {self.name!r} -> {label!r}")
            self.rename(label)

    def set_last_command(self, status: int):
        """Update GV7 Last Command driver (EXECSTAT uom 25)."""
        self.setDriver("GV7", status, report=True, force=False, uom=25)

    def cmdActivate(self, command=None):
        LOGGER.info(f"cmdActivate {self.lpfx}, {command}")
        try:
            exec_id = asyncio.run_coroutine_threadsafe(
                self.controller.tahoma_client.execute_scenario(self.sid),
                self.controller.mainloop,
            ).result(timeout=30)

            if exec_id:
                self.set_last_command(LAST_CMD_PENDING)
                if self.controller.tahoma_client.last_scenario_via_cloud:
                    self.controller.track_cloud_scenario(self.address)
                else:
                    self.controller.track_execution(exec_id, self.address)
                LOGGER.info(
                    f"TaHoma scenario {self.name} activated (exec: {exec_id})"
                )
            elif self.controller.tahoma_client.cloud_scenes_configured:
                self.set_last_command(LAST_CMD_FAILED)
                LOGGER.warning(f"TaHoma scenario {self.name} activation failed")
            else:
                LOGGER.info(
                    f"Scene {self.name}: Activate skipped — Somfy cloud credentials "
                    "not configured (optional; shade control is unaffected)"
                )
        except Exception as e:
            self.set_last_command(LAST_CMD_FAILED)
            LOGGER.error(
                f"Error activating TaHoma scenario {self.name}: {e}",
                exc_info=True,
            )

        self.reportCmd("ACTIVATE", 2)

    def query(self, command=None):
        LOGGER.info(f"cmd Query {self.lpfx}, {command}")
        self._sync_label_from_controller()
        self.reportDrivers()

    drivers = SCENE_DRIVERS

    commands = {
        "ACTIVATE": cmdActivate,
        "QUERY": query,
    }
