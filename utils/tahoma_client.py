"""TaHoma API client wrapper for Polyglot integration.

This module provides a wrapper around the pyoverkiz library to integrate
Somfy TaHoma API with the Universal Devices Polyglot NodeServer framework.

(C) 2025 Stephen Jenkins
"""

import asyncio
import ssl
from typing import Optional, List, Any

from pyoverkiz.client import OverkizClient
from pyoverkiz.const import OverkizServer, SUPPORTED_SERVERS  # type: ignore[attr-defined]
from pyoverkiz.models import Command, Device, Event
from pyoverkiz.exceptions import (
    NotAuthenticatedException,
    InvalidTokenException,
    TooManyRequestsException,
    InvalidEventListenerIdException,
    NoRegisteredEventListenerException,
    ExecutionQueueFullException,
)
from udi_interface import LOGGER
import aiohttp

from utils.scenario import (
    TaHomaScenario,
    action_group_exec_payload,
    extract_action_group_actions,
    parse_action_group,
)

# pyoverkiz SUPPORTED_SERVERS keys (somfy_america, etc.) plus legacy display names.
CLOUD_REGION_ALIASES = {
    "somfy_america": "somfy_america",
    "somfy (north america)": "somfy_america",
    "somfy north america": "somfy_america",
    "north america": "somfy_america",
    "somfy_europe": "somfy_europe",
    "somfy (europe)": "somfy_europe",
    "somfy europe": "somfy_europe",
    "europe": "somfy_europe",
    "somfy_oceania": "somfy_oceania",
    "somfy (oceania)": "somfy_oceania",
    "somfy oceania": "somfy_oceania",
    "oceania": "somfy_oceania",
}

SOMFY_CLOUD_REGIONS = ("somfy_america", "somfy_europe", "somfy_oceania")


def resolve_cloud_server_key(region: str) -> Optional[str]:
    """Map Polyglot region setting to a pyoverkiz SUPPORTED_SERVERS key."""
    normalized = (region or "somfy_america").strip()
    if not normalized:
        normalized = "somfy_america"

    alias = CLOUD_REGION_ALIASES.get(normalized.lower())
    if alias is not None:
        return alias

    if normalized in SUPPORTED_SERVERS:
        return normalized

    return None


def cloud_server_label(server_key: str) -> str:
    """Return a human-readable label for logs."""
    server = SUPPORTED_SERVERS.get(server_key)
    if server is not None and getattr(server, "name", None):
        return str(server.name)
    return server_key


class TaHomaSSLVerificationError(Exception):
    """TaHoma HTTPS certificate could not be verified."""

    USER_MESSAGE = (
        "TaHoma SSL certificate verification failed (verify_ssl is true). "
        "TaHoma uses a self-signed certificate. Set verify_ssl to false in "
        "Polyglot configuration (recommended), or install the Somfy root CA "
        "on your EISY/Polisy. See POLYGLOT_CONFIG.md."
    )


class TaHomaAuthenticationError(Exception):
    """TaHoma rejected the configured bearer token."""

    USER_MESSAGE = (
        "TaHoma authentication failed. Verify gateway_pin and tahoma_token "
        "match your TaHoma Developer Mode settings. Paste the token only (no "
        "'Bearer ' prefix). Generate a new token in the TaHoma app if needed."
    )


class TaHomaConnectionError(Exception):
    """TaHoma gateway could not be reached on the network."""


_SSL_ERROR_MARKERS = (
    "certificate verify failed",
    "self signed certificate",
    "self-signed certificate",
    "unable to get local issuer certificate",
    "certificate_verify_failed",
)


def is_transient_connection_error(exc: BaseException) -> bool:
    """Return True if exc looks like a recoverable network/gateway outage."""
    if isinstance(exc, TaHomaConnectionError):
        return True
    if isinstance(
        exc,
        (
            asyncio.TimeoutError,
            TimeoutError,
            aiohttp.ClientConnectorError,
            aiohttp.ConnectionTimeoutError,
            aiohttp.ServerConnectionError,
        ),
    ):
        return True
    message = str(exc).lower()
    return "timeout" in message or "connection" in message


def is_ssl_verification_error(exc: BaseException) -> bool:
    """Return True if exc (or its cause chain) is an SSL verification failure."""
    current: BaseException | None = exc
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, (ssl.SSLCertVerificationError, aiohttp.ClientConnectorCertificateError)):
            return True
        message = str(current).lower()
        if any(marker in message for marker in _SSL_ERROR_MARKERS):
            return True
        current = current.__cause__ or current.__context__
    return False


class TaHomaClient:
    """Wrapper around pyoverkiz for Somfy TaHoma integration.

    This class provides a simplified interface to the TaHoma API,
    handling authentication, event listening, and device control
    in a way that integrates well with Polyglot's architecture.
    """

    def __init__(
        self,
        token: str,
        gateway_pin: str,
        verify_ssl: bool = False,
        gateway_ip: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
        cloud_email: str = "",
        cloud_password: str = "",
        cloud_region: str = "somfy_america",
    ):
        """Initialize TaHoma client.

        Args:
            token: Bearer token from TaHoma app Developer Mode
            gateway_pin: Gateway PIN (e.g., "2001-0001-1891")
            verify_ssl: Whether to verify SSL certificates
            gateway_ip: Optional IP address of gateway (e.g., "192.168.1.100")
            session: Optional aiohttp session (created if None)
            cloud_email: Optional Somfy TaHoma cloud account email (for scenes)
            cloud_password: Optional Somfy TaHoma cloud account password (for scenes)
            cloud_region: Somfy cloud hub key or name (default somfy_america)
        """
        self.token = token
        self.gateway_pin = gateway_pin
        self.verify_ssl = verify_ssl
        self.gateway_ip = gateway_ip
        self.cloud_email = (cloud_email or "").strip()
        self.cloud_password = cloud_password or ""
        self.cloud_region = (cloud_region or "somfy_america").strip() or "somfy_america"
        self._session = session
        self._own_session = session is None
        self.last_scenario_via_cloud = False

        self.client: Optional[OverkizClient] = None
        self._cloud_client: Optional[OverkizClient] = None
        self._cloud_session: Optional[aiohttp.ClientSession] = None
        self.event_listener_id: Optional[str] = None
        self._connected = False
        self._action_groups_by_oid: dict[str, dict] = {}

        # Build server config for local API
        if gateway_ip:
            endpoint = f"https://{gateway_ip}:8443/enduser-mobile-web/1/enduserAPI/"
        else:
            endpoint = f"https://gateway-{gateway_pin}.local:8443/enduser-mobile-web/1/enduserAPI/"

        self.server = OverkizServer(
            name="Somfy TaHoma (local)",
            endpoint=endpoint,
            manufacturer="Somfy",
            configuration_url=None,
        )

    @property
    def cloud_scenes_configured(self) -> bool:
        """True when optional Somfy cloud credentials are set for scene Activate."""
        return bool(self.cloud_email and self.cloud_password)

    @property
    def gateway_target(self) -> str:
        """Human-readable gateway host used for connection attempts."""
        if self.gateway_ip:
            return self.gateway_ip
        return f"gateway-{self.gateway_pin}.local"

    async def connect(self) -> bool:
        """Initialize connection to TaHoma gateway.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create session if needed (or replace a closed session after reconnect)
            if self._own_session and (
                self._session is None or self._session.closed
            ):
                ssl_context = ssl.create_default_context()
                if not self.verify_ssl:
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE

                # Set reasonable timeouts for local API connections
                timeout = aiohttp.ClientTimeout(total=60, connect=10, sock_read=30)
                connector = aiohttp.TCPConnector(ssl=ssl_context)
                self._session = aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout
                )

            # Create OverkizClient with v1 API
            self.client = OverkizClient(
                username="",  # Not needed for local API
                password="",  # Not needed for local API
                token=self.token,
                session=self._session,
                verify_ssl=self.verify_ssl,
                server=self.server,
            )

            # Login (validates token) - don't register event listener yet
            # to avoid timeout issues during initial connection
            await self.client.login(register_event_listener=False)

            LOGGER.info(f"Connected to TaHoma gateway: {self.gateway_pin}")
            self._connected = True
            if self.cloud_email and self.cloud_password:
                LOGGER.info(
                    "Optional Somfy cloud credentials configured for scene Activate (%s)",
                    cloud_server_label(
                        resolve_cloud_server_key(self.cloud_region) or self.cloud_region
                    ),
                )
            
            # Register event listener separately with better error handling
            # This allows connection to succeed even if event listener fails
            try:
                listener_id = await self.client.register_event_listener()
                self.event_listener_id = listener_id
                LOGGER.info(f"Event listener registered successfully: {listener_id}")
            except Exception as e:
                LOGGER.warning(f"Failed to register event listener during connect: {e}")
                LOGGER.info("Connection successful - event listener can be retried later")
            
            return True

        except InvalidTokenException as e:
            LOGGER.error(TaHomaAuthenticationError.USER_MESSAGE)
            LOGGER.debug("TaHoma invalid token details", exc_info=True)
            raise TaHomaAuthenticationError(
                TaHomaAuthenticationError.USER_MESSAGE
            ) from e
        except NotAuthenticatedException as e:
            LOGGER.error(TaHomaAuthenticationError.USER_MESSAGE)
            LOGGER.debug("TaHoma authentication failure details", exc_info=True)
            raise TaHomaAuthenticationError(
                TaHomaAuthenticationError.USER_MESSAGE
            ) from e
        except (
            asyncio.TimeoutError,
            TimeoutError,
            aiohttp.ClientConnectorError,
            aiohttp.ConnectionTimeoutError,
            aiohttp.ServerConnectionError,
        ) as e:
            message = (
                f"Cannot reach TaHoma gateway at {self.gateway_target}. "
                "The gateway may be offline or still starting. Verify it is "
                "powered on and reachable on the network, then restart the NodeServer."
            )
            LOGGER.error(message)
            LOGGER.debug("TaHoma connection failure details", exc_info=True)
            raise TaHomaConnectionError(message) from e
        except Exception as e:
            if self.verify_ssl and is_ssl_verification_error(e):
                LOGGER.error(TaHomaSSLVerificationError.USER_MESSAGE)
                LOGGER.debug("TaHoma SSL verification failure details", exc_info=True)
                raise TaHomaSSLVerificationError(
                    TaHomaSSLVerificationError.USER_MESSAGE
                ) from e
            LOGGER.error(f"Failed to connect to TaHoma: {e}", exc_info=True)
            return False

    async def disconnect(self):
        """Disconnect from TaHoma and cleanup resources."""
        if self.event_listener_id:
            try:
                await self.unregister_event_listener()
            except Exception as e:
                LOGGER.warning(f"Error unregistering event listener: {e}")

        if self._own_session and self._session and not self._session.closed:
            await self._session.close()

        if self._cloud_session and not self._cloud_session.closed:
            await self._cloud_session.close()

        self.client = None
        self._cloud_client = None
        self._session = None
        self._cloud_session = None
        self._connected = False
        LOGGER.info("Disconnected from TaHoma")

    async def check_health(self) -> bool:
        """Return True if the gateway local API responds."""
        if not self._connected or not self.client:
            return False

        try:
            version = await self.client.get_api_version()
            LOGGER.debug(f"TaHoma health OK (apiVersion={version})")
            return True
        except Exception as e:
            if is_transient_connection_error(e):
                LOGGER.warning(f"TaHoma health check failed: {e}")
            else:
                LOGGER.error(f"TaHoma health check failed: {e}", exc_info=True)
            return False

    async def reconnect(self) -> bool:
        """Disconnect and establish a fresh session to the gateway."""
        await self.disconnect()
        return await self.connect()

    async def get_devices(self) -> List[Device]:
        """Get all devices from TaHoma.

        Returns:
            List of Device objects
        """
        if not self._connected or not self.client:
            raise RuntimeError("Not connected to TaHoma")

        try:
            devices = await self.client.get_devices()
            LOGGER.info(f"Retrieved {len(devices)} devices from TaHoma")
            return devices
        except Exception as e:
            LOGGER.error(f"Failed to get devices: {e}", exc_info=True)
            raise

    async def get_device(self, device_url: str) -> Optional[Device]:
        """Get a specific device by URL.

        Args:
            device_url: Device URL (e.g., "io://1234-5678-9012/12345678")

        Returns:
            Device object or None if not found
        """
        if not self._connected or not self.client:
            raise RuntimeError("Not connected to TaHoma")

        try:
            device = await self.client.get_device(device_url)  # type: ignore[attr-defined]
            return device
        except Exception as e:
            LOGGER.error(f"Failed to get device {device_url}: {e}")
            return None

    async def get_scenarios(self) -> List[TaHomaScenario]:
        """Get all scenarios (scenes) from TaHoma actionGroups API.

        Returns:
            List of TaHomaScenario records
        """
        if not self._connected or not self.client:
            raise RuntimeError("Not connected to TaHoma")

        try:
            raw_groups = await self._fetch_action_groups()
            scenarios: list[TaHomaScenario] = []
            skipped: list[str] = []
            self._action_groups_by_oid = {}
            for item in raw_groups:
                oid = None
                if isinstance(item, dict):
                    oid = item.get("oid") or item.get("OID") or item.get("id")
                    if oid is not None:
                        self._action_groups_by_oid[str(oid)] = item
                scenario = parse_action_group(item)
                if scenario:
                    scenarios.append(scenario)
                elif oid is not None:
                    skipped.append(str(oid))
            if skipped:
                LOGGER.info(
                    "Skipped %d unnamed actionGroups (orphan/system records): %s",
                    len(skipped),
                    ", ".join(skipped),
                )
            local_action_count = 0
            cloud_only_count = 0
            for scenario in scenarios:
                group = self._action_groups_by_oid.get(scenario.oid, {})
                action_count = len(extract_action_group_actions(group))
                if action_count:
                    local_action_count += 1
                    LOGGER.debug(
                        "Scenario %s: %d device action(s) available locally",
                        scenario.label,
                        action_count,
                    )
                else:
                    cloud_only_count += 1
                    LOGGER.debug(
                        "Scenario %s: no local actions (Activate uses Somfy cloud when configured)",
                        scenario.label,
                    )
            if scenarios:
                if self.cloud_scenes_configured:
                    region_label = cloud_server_label(
                        resolve_cloud_server_key(self.cloud_region)
                        or self.cloud_region
                    )
                    LOGGER.info(
                        "Discovered %d TaHoma app scene(s): %d runnable locally, "
                        "%d via Somfy cloud (%s) when you Activate",
                        len(scenarios),
                        local_action_count,
                        cloud_only_count,
                        region_label,
                    )
                else:
                    LOGGER.info(
                        "Discovered %d TaHoma app scene node(s). Scene Activate is "
                        "optional and cloud-only — leave tahoma_cloud_email/password "
                        "empty to use shade control only (no Somfy cloud contact)",
                        len(scenarios),
                    )
            LOGGER.info(f"Retrieved {len(scenarios)} scenarios from TaHoma")
            return scenarios
        except Exception as e:
            LOGGER.error(f"Failed to get scenarios: {e}", exc_info=True)
            raise

    async def _fetch_action_groups(self) -> list:
        """Fetch raw actionGroups JSON from the gateway."""
        if not self.client:
            raise RuntimeError("Not connected to TaHoma")

        fetch = getattr(self.client, "_OverkizClient__get", None)
        if fetch is None:
            raise RuntimeError("pyoverkiz client cannot fetch actionGroups")

        result = await fetch("actionGroups")
        if isinstance(result, list):
            return result
        return []

    async def _fetch_action_group_by_oid(self, scenario_oid: str) -> Optional[dict]:
        """Fetch one actionGroup by OID (list endpoint often omits actions)."""
        if not self.client:
            raise RuntimeError("Not connected to TaHoma")

        fetch = getattr(self.client, "_OverkizClient__get", None)
        if fetch is None:
            return None

        try:
            result = await fetch(f"actionGroups/{scenario_oid}")
        except Exception as exc:
            LOGGER.debug(
                "GET actionGroups/%s failed: %s",
                scenario_oid,
                exc,
            )
            return None

        if isinstance(result, dict):
            return result
        return None

    async def _find_action_group(self, scenario_oid: str) -> Optional[dict]:
        """Return raw actionGroup JSON for a scenario OID."""
        oid = str(scenario_oid)
        cached = self._action_groups_by_oid.get(oid)
        if cached and extract_action_group_actions(cached):
            return cached

        detail = await self._fetch_action_group_by_oid(oid)
        if detail:
            self._action_groups_by_oid[oid] = detail
            if extract_action_group_actions(detail):
                return detail

        for item in await self._fetch_action_groups():
            if not isinstance(item, dict):
                continue
            item_oid = item.get("oid") or item.get("OID") or item.get("id")
            if item_oid is not None and str(item_oid) == oid:
                self._action_groups_by_oid[oid] = item
                return item
        return cached or detail

    async def _exec_apply(self, payload: dict) -> str:
        """POST exec/apply — the local Developer Mode API for action groups."""
        if not self.client:
            raise RuntimeError("Not connected to TaHoma")

        post = getattr(self.client, "_OverkizClient__post", None)
        if post is None:
            raise RuntimeError("pyoverkiz client cannot post exec/apply")

        response = await post("exec/apply", payload)
        return str(response["execId"])

    async def _get_cloud_client(self) -> Optional[OverkizClient]:
        """Lazy Somfy cloud client for TaHoma app scene execution."""
        if not self.cloud_email or not self.cloud_password:
            return None
        if self._cloud_client is not None:
            return self._cloud_client

        if self._cloud_session is None or self._cloud_session.closed:
            ssl_context = ssl.create_default_context()
            if not self.verify_ssl:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            timeout = aiohttp.ClientTimeout(total=60, connect=10, sock_read=30)
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self._cloud_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
            )

        server_key = resolve_cloud_server_key(self.cloud_region)
        if server_key is None:
            LOGGER.error(
                "Unknown Somfy cloud region %r (use one of %s, or legacy names like "
                "'Somfy (North America)')",
                self.cloud_region,
                ", ".join(SOMFY_CLOUD_REGIONS),
            )
            return None

        cloud_server = SUPPORTED_SERVERS.get(server_key)
        if cloud_server is None:
            LOGGER.error(
                "Somfy cloud server %r missing from pyoverkiz SUPPORTED_SERVERS",
                server_key,
            )
            return None

        self._cloud_client = OverkizClient(
            username=self.cloud_email,
            password=self.cloud_password,
            session=self._cloud_session,
            server=cloud_server,
        )
        try:
            await self._cloud_client.login(register_event_listener=False)
        except Exception:
            self._cloud_client = None
            raise

        LOGGER.info(
            "Connected to Somfy TaHoma cloud API (%s) for scene execution",
            cloud_server_label(server_key),
        )
        return self._cloud_client

    async def _execute_scenario_via_cloud(self, scenario_oid: str) -> Optional[str]:
        """Run a TaHoma app scene via Somfy cloud exec/{oid} (optional cloud path)."""
        if not self.cloud_scenes_configured:
            LOGGER.info(
                "Scenario %s not activated — Somfy cloud credentials not configured "
                "(optional; shade control is unaffected)",
                scenario_oid,
            )
            return None

        try:
            cloud = await self._get_cloud_client()
            if not cloud:
                LOGGER.error(
                    "Scenario %s cannot activate — check tahoma_cloud_region "
                    "(default somfy_america) and cloud login credentials",
                    scenario_oid,
                )
                return None

            exec_id = await cloud.execute_scenario(scenario_oid)
            LOGGER.info(
                "Executed scenario %s via Somfy cloud (exec: %s)",
                scenario_oid,
                exec_id,
            )
            return exec_id
        except Exception as e:
            LOGGER.error(
                "Somfy cloud scene execution failed for %s: %s",
                scenario_oid,
                e,
                exc_info=True,
            )
            return None

    async def execute_scenario(self, scenario_oid: str) -> Optional[str]:
        """Execute a TaHoma app scene (optional; cloud fallback when needed).

        Shade commands always use the local Developer Mode API. TaHoma **app scenes**
        are usually stored server-side: the local API lists names but not device
        actions. When local actions exist, run exec/apply. Otherwise use Somfy
        cloud exec/{oid} only if tahoma_cloud_email/password are configured.

        Args:
            scenario_oid: Scenario OID

        Returns:
            Execution ID or None on failure
        """
        if not self._connected or not self.client:
            raise RuntimeError("Not connected to TaHoma")

        self.last_scenario_via_cloud = False

        try:
            group = await self._find_action_group(scenario_oid)
            if not group:
                LOGGER.error("Scenario %s not found in actionGroups", scenario_oid)
                return None

            label = (
                str(group.get("label") or group.get("Label") or "Polyglot Scene").strip()
                or "Polyglot Scene"
            )
            actions = extract_action_group_actions(group)
            payload = action_group_exec_payload(label, actions)
            if payload:
                exec_id = await self._exec_apply(payload)
                LOGGER.info(
                    "Executed scenario %s via exec/apply (exec: %s, %d actions)",
                    scenario_oid,
                    exec_id,
                    len(payload["actions"]),
                )
                return exec_id

            LOGGER.warning(
                "Scenario %s (%s) has no local action details; trying Somfy cloud",
                scenario_oid,
                label,
            )
            exec_id = await self._execute_scenario_via_cloud(scenario_oid)
            if exec_id:
                self.last_scenario_via_cloud = True
            return exec_id
        except ExecutionQueueFullException:
            LOGGER.warning("Execution queue full - try again later")
            return None
        except Exception as e:
            LOGGER.error(f"Failed to execute scenario: {e}", exc_info=True)
            return None

    async def execute_command(
        self,
        device_url: str,
        command_name: str,
        parameters: List[Any],
        label: str = "Polyglot Control",
    ) -> Optional[str]:
        """Execute a command on a device.

        Args:
            device_url: Device URL
            command_name: Command name (e.g., "setClosure")
            parameters: Command parameters (e.g., [50] for 50% position)
            label: Label for the execution

        Returns:
            Execution ID or None on failure
        """
        if not self._connected or not self.client:
            raise RuntimeError("Not connected to TaHoma")

        try:
            command = Command(name=command_name, parameters=parameters)
            exec_id = await self.client.execute_command(
                device_url=device_url, command=command, label=label
            )
            LOGGER.debug(
                f"Executed {command_name} on {device_url} "
                f"with params {parameters} (exec: {exec_id})"
            )
            return exec_id

        except InvalidTokenException:
            LOGGER.error("Invalid token - regenerate in TaHoma app")
            raise
        except TooManyRequestsException:
            LOGGER.warning("Rate limited - backing off")
            await asyncio.sleep(5)
            return None
        except ExecutionQueueFullException:
            LOGGER.warning("Execution queue full - try again later")
            return None
        except Exception as e:
            LOGGER.error(
                f"Failed to execute command {command_name} on {device_url}: {e}",
                exc_info=True,
            )
            return None

    async def get_current_execution(self, exec_id: str):
        """Return current execution status for an exec ID."""
        if not self._connected or not self.client:
            raise RuntimeError("Not connected to TaHoma")

        try:
            execution = await self.client.get_current_execution(exec_id)
            LOGGER.debug(
                "Execution %s state=%s",
                exec_id,
                getattr(execution, "state", None),
            )
            return execution
        except Exception as e:
            LOGGER.debug("Could not fetch execution %s: %s", exec_id, e)
            raise

    async def register_event_listener(self) -> str:
        """Register for event notifications.

        Returns:
            Event listener ID

        Note:
            Listener expires after 10 minutes of inactivity.
            Keep alive by calling fetch_events() at least once per 10 minutes.
        """
        if not self._connected or not self.client:
            raise RuntimeError("Not connected to TaHoma")

        try:
            listener_id = await self.client.register_event_listener()
            self.event_listener_id = listener_id
            LOGGER.info(f"Registered event listener: {listener_id}")
            return listener_id
        except Exception as e:
            LOGGER.error(f"Failed to register event listener: {e}", exc_info=True)
            raise

    async def fetch_events(self) -> List[Event]:
        """Fetch pending events from registered listener.

        Returns:
            List of Event objects

        Note:
            Should be called at least once per second (Somfy recommendation)
            and at least once per 10 minutes (to keep listener alive).
        """
        if not self._connected or not self.client:
            raise RuntimeError("Not connected to TaHoma")

        if not self.event_listener_id:
            raise RuntimeError("No event listener registered")

        try:
            events = await self.client.fetch_events()
            if events:
                LOGGER.debug(f"Fetched {len(events)} events")
            return events

        except InvalidEventListenerIdException:
            LOGGER.warning("Event listener expired - re-registration needed")
            self.event_listener_id = None
            raise
        except NoRegisteredEventListenerException:
            LOGGER.warning("No registered event listener")
            self.event_listener_id = None
            raise
        except Exception as e:
            # Log connection timeouts at debug level (expected with slow gateways)
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                LOGGER.debug(f"Connection timeout fetching events (will retry): {e}")
            else:
                LOGGER.error(f"Failed to fetch events: {e}", exc_info=True)
            raise

    async def unregister_event_listener(self):
        """Unregister event listener."""
        if not self._connected or not self.client or not self.event_listener_id:
            return

        try:
            # The pyoverkiz method doesn't take parameters, it uses the internal listener ID
            await self.client.unregister_event_listener()
            LOGGER.info(f"Unregistered event listener: {self.event_listener_id}")
            self.event_listener_id = None
        except Exception as e:
            LOGGER.warning(f"Error unregistering event listener: {e}")

    @property
    def is_connected(self) -> bool:
        """Check if connected to TaHoma."""
        return self._connected

    def get_device_url_from_address(
        self, address: str, devices: List[Device]
    ) -> Optional[str]:
        """Helper to find device_url from node address.

        Args:
            address: Node address (e.g., "sh12345678")
            devices: List of devices from get_devices()

        Returns:
            device_url or None if not found
        """
        # Extract device ID from address (remove 'sh' prefix)
        device_id = address.replace("sh", "")

        for device in devices:
            if device.device_url.endswith(device_id):
                return device.device_url

        return None


# Convenience function for creating client
async def create_tahoma_client(
    token: str, gateway_pin: str, verify_ssl: bool = False
) -> TaHomaClient:
    """Create and connect a TaHoma client.

    Args:
        token: Bearer token from TaHoma app
        gateway_pin: Gateway PIN
        verify_ssl: Whether to verify SSL

    Returns:
        Connected TaHomaClient instance
    """
    client = TaHomaClient(token, gateway_pin, verify_ssl)
    await client.connect()
    return client
