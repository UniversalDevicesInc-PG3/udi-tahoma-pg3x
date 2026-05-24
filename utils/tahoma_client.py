"""TaHoma API client wrapper for Polyglot integration.

This module provides a wrapper around the pyoverkiz library to integrate
Somfy TaHoma API with the Universal Devices Polyglot NodeServer framework.

(C) 2025 Stephen Jenkins
"""

import asyncio
import ssl
from typing import Optional, List, Any

from pyoverkiz.client import OverkizClient
from pyoverkiz.auth.credentials import LocalTokenCredentials
from pyoverkiz.utils import create_local_server_config
from pyoverkiz.models import Action, Command, Device, Event, PersistedActionGroup
from pyoverkiz.exceptions import (
    NotAuthenticatedError,
    InvalidTokenError,
    TooManyRequestsError,
    InvalidEventListenerIdError,
    NoRegisteredEventListenerError,
    ExecutionQueueFullError,
)
from udi_interface import LOGGER
import aiohttp


class TaHomaClient:
    """Wrapper around pyoverkiz for TaHoma/Phantom Blinds integration.

    This class provides a simplified interface to the TaHoma API,
    handling authentication, event listening, and device control
    in a way that integrates well with Polyglot's architecture.
    """

    def __init__(
        self,
        token: str,
        gateway_pin: str,
        verify_ssl: bool = True,
        gateway_ip: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """Initialize TaHoma client.

        Args:
            token: Bearer token from TaHoma app Developer Mode
            gateway_pin: Gateway PIN (e.g., "2001-0001-1891")
            verify_ssl: Whether to verify SSL certificates
            gateway_ip: Optional IP address of gateway (e.g., "192.168.1.100")
            session: Optional aiohttp session (created if None)
        """
        self.token = token
        self.gateway_pin = gateway_pin
        self.verify_ssl = verify_ssl
        self.gateway_ip = gateway_ip
        self._session = session
        self._own_session = session is None

        self.client: Optional[OverkizClient] = None
        self.event_listener_id: Optional[str] = None
        self._connected = False

        # Build server config for local API using v2 API
        self.server = create_local_server_config(
            host=f"{gateway_ip}:8443" if gateway_ip else f"gateway-{gateway_pin}.local:8443"
        )

    async def connect(self) -> bool:
        """Initialize connection to TaHoma gateway.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create session if needed
            if self._own_session:
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

            # Create OverkizClient with v2 API using LocalTokenCredentials
            self.client = OverkizClient(
                server=self.server,
                credentials=LocalTokenCredentials(self.token),
                verify_ssl=self.verify_ssl,
                session=self._session,
            )

            # Login (validates token) - don't register event listener yet
            # to avoid timeout issues during initial connection
            await self.client.login(register_event_listener=False)

            LOGGER.info(f"Connected to TaHoma gateway: {self.gateway_pin}")
            self._connected = True
            
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

        except InvalidTokenError:
            LOGGER.error("Invalid TaHoma token - regenerate in app")
            raise
        except NotAuthenticatedError:
            LOGGER.error("Authentication failed - check token")
            raise
        except Exception as e:
            LOGGER.error(f"Failed to connect to TaHoma: {e}", exc_info=True)
            return False

    async def disconnect(self):
        """Disconnect from TaHoma and cleanup resources."""
        if self.event_listener_id:
            try:
                await self.unregister_event_listener()
            except Exception as e:
                LOGGER.warning(f"Error unregistering event listener: {e}")

        if self._own_session and self._session:
            await self._session.close()

        self._connected = False
        LOGGER.info("Disconnected from TaHoma")

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

    async def get_scenarios(self) -> List[PersistedActionGroup]:
        """Get all scenarios (scenes) from TaHoma.

        Returns:
            List of PersistedActionGroup objects (formerly Scenario)
            
        Note:
            In pyoverkiz v2, scenarios are called action groups.
            This method provides backward compatibility.
        """
        if not self._connected or not self.client:
            raise RuntimeError("Not connected to TaHoma")

        try:
            action_groups = await self.client.get_action_groups()
            LOGGER.info(f"Retrieved {len(action_groups)} scenarios from TaHoma")
            return action_groups
        except TypeError as e:
            # Handle case where API response doesn't match model
            if "missing" in str(e) and "required positional argument" in str(e):
                LOGGER.warning(f"Action group response format doesn't match model: {e}")
                LOGGER.info("Returning empty scenario list - will retry on next poll")
                return []
            else:
                LOGGER.error(f"Failed to get scenarios: {e}", exc_info=True)
                raise
        except Exception as e:
            LOGGER.error(f"Failed to get scenarios: {e}", exc_info=True)
            raise

    async def execute_scenario(self, scenario_oid: str) -> Optional[str]:
        """Execute a scenario (scene).

        Args:
            scenario_oid: Scenario OID

        Returns:
            Execution ID or None on failure
        """
        if not self._connected or not self.client:
            raise RuntimeError("Not connected to TaHoma")

        try:
            exec_id = await self.client.execute_persisted_action_group(scenario_oid)
            LOGGER.info(f"Executed scenario {scenario_oid} (exec: {exec_id})")
            return exec_id
        except ExecutionQueueFullError:
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
            action = Action(device_url=device_url, commands=[command])
            exec_id = await self.client.execute_action_group(
                actions=[action], label=label
            )
            LOGGER.debug(
                f"Executed {command_name} on {device_url} "
                f"with params {parameters} (exec: {exec_id})"
            )
            return exec_id

        except InvalidTokenError:
            LOGGER.error("Invalid token - regenerate in TaHoma app")
            raise
        except TooManyRequestsError:
            LOGGER.warning("Rate limited - backing off")
            await asyncio.sleep(5)
            return None
        except ExecutionQueueFullError:
            LOGGER.warning("Execution queue full - try again later")
            return None
        except Exception as e:
            LOGGER.error(
                f"Failed to execute command {command_name} on {device_url}: {e}",
                exc_info=True,
            )
            return None

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

        except InvalidEventListenerIdError:
            LOGGER.warning("Event listener expired - re-registration needed")
            self.event_listener_id = None
            raise
        except NoRegisteredEventListenerError:
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
    token: str, gateway_pin: str, verify_ssl: bool = True
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
