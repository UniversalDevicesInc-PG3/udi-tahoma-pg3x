"""Module for Somfy TaHoma/Phantom Blinds Controller node in a Polyglot v3 NodeServer.

This module defines the Controller class, which is the primary node for interacting
with Somfy TaHoma gateways. It handles discovery of devices and scenarios,
manages the connection to the gateway, and processes events.

(C) 2025 Stephen Jenkins
"""

# std libraries
import asyncio
import logging
from threading import Thread, Event, Lock, Condition
from typing import Optional

# external libraries
from udi_interface import Node, LOGGER, Custom, LOG_HANDLER

# personal libraries
from utils.tahoma_client import TaHomaClient
from utils.config_validation import (
    validate_gateway_pin,
    validate_bearer_token,
)
from pyoverkiz.exceptions import (
    InvalidEventListenerIdException,
    NoRegisteredEventListenerException,
)

# Nodes
from nodes import (
    Scene,
    Shade,
    ShadeNoTilt,
    ShadeOnlyPrimary,
)

# limit the room label length as room - shade/scene must be < 30
ROOM_NAME_LIMIT = 15

# We need an event loop as we run in a thread which doesn't have a loop
mainloop = asyncio.get_event_loop()


class Controller(Node):
    """Polyglot v3 NodeServer Controller for Somfy TaHoma/Phantom Blinds.

    This class represents the main controller node that communicates with the
    Somfy TaHoma gateway. It is responsible for discovering and managing
    device and scenario nodes, handling user configuration, processing
    events from the gateway, and reporting status to the ISY.
    """

    id = "hdctrl"

    def __init__(self, poly, primary, address, name):
        """Initializes the Controller node.

        Args:
            poly: An instance of the Polyglot interface.
            primary: The address of the primary node.
            address: The address of this node.
            name: The name of this node.
        """
        super(Controller, self).__init__(poly, primary, address, name)
        # important flags, timers, vars
        self.poly = poly
        self.address = address
        self.name = name
        self.hb = 0  # heartbeat
        self.update_last = 0.0
        self.update_minimum = 3.0  # do not allow updates more often than this
        self.eventTimer = 0
        self.numNodes = 0

        # TaHoma client (initialized in start())
        self.tahoma_client: Optional[TaHomaClient] = None
        self.token = ""
        self.gateway_pin = ""
        self.use_local_api = True
        self.verify_ssl = True

        # in function vars
        self.update_in = False
        self.discovery_in = False
        self.poll_in = False
        self.event_polling_in = False

        # storage arrays & conditions
        self.n_queue = []
        self.queue_condition = Condition()
        self.gateway_event = []
        self.gateway_event_condition = Condition()
        self._event_polling_thread = None

        self.devices_map = {}  # Key: deviceURL, Value: device data
        self.devices_map_lock = Lock()

        self.scenarios_map = {}  # Key: scenario OID, Value: scenario data

        # Events
        self.ready_event = Event()
        self.stop_event = Event()
        self.all_handlers_st_event = Event()

        # Create data storage classes
        self.Notices = Custom(self.poly, "notices")
        self.Parameters = Custom(self.poly, "customparams")
        self.Data = Custom(self.poly, "customdata")
        self.TypedParameters = Custom(self.poly, "customtypedparams")
        self.TypedData = Custom(self.poly, "customtypeddata")

        # startup completion flags
        self.handler_params_st = False
        self.handler_data_st = False
        self.handler_typedparams_st = False
        self.handler_typeddata_st = False

        # Subscribe to various events from the Interface class.
        # The START event is unique in that you can subscribe to
        # the start event for each node you define.

        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CONFIGDONE, self.config_done)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.CUSTOMDATA, self.dataHandler)
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.DISCOVER, self.discover_cmd)
        self.poly.subscribe(self.poly.CUSTOMTYPEDDATA, self.typedDataHandler)
        self.poly.subscribe(self.poly.CUSTOMTYPEDPARAMS, self.typedParameterHandler)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)

        # Tell the interface we have subscribed to all the events we need.
        # Once we call ready(), the interface will start publishing data.
        self.poly.ready()

        # Tell the interface we exist.
        self.poly.addNode(self, conn_status="ST")

    def start(self):
        """Handles the startup sequence for the node.

        This method is called once by Polyglot at startup. It initializes
        the controller, sets up custom parameters, establishes a connection
        to the TaHoma gateway, performs initial discovery, and starts background
        tasks for event polling.
        """
        LOGGER.info(
            f"Started Phantom Blinds/TaHoma PG3 NodeServer {self.poly.serverdata['version']}"
        )
        self.Notices.clear()
        self.Notices["hello"] = "Plugin Start-up"
        self.setDriver("ST", 1, report=True, force=True)
        self.update_last = 0.0

        # Send the profile files to the ISY if neccessary or version changed.
        self.poly.updateProfile()

        # Send the default custom parameters documentation file to Polyglot
        self.poly.setCustomParamsDoc()

        # Initializing heartbeat
        self.heartbeat()

        # set-up async loop
        self.mainloop = mainloop
        asyncio.set_event_loop(mainloop)
        self.connect_thread = Thread(target=mainloop.run_forever)
        self.connect_thread.start()

        # Wait for all handlers to finish
        LOGGER.warning("Waiting for all handlers to complete...")
        self.all_handlers_st_event.wait(timeout=300)
        if not self.all_handlers_st_event.is_set():
            # start-up failed
            LOGGER.error("Timed out waiting for handlers to startup")
            self.setDriver("ST", 2)  # start-up failed
            self.Notices["error"] = (
                "Error start-up timeout.  Check config / hardware & restart"
            )
            return

        # Initialize TaHoma client connection
        try:
            LOGGER.info("Initializing TaHoma client...")
            self.tahoma_client = TaHomaClient(
                token=self.token,
                gateway_pin=self.gateway_pin,
                verify_ssl=self.verify_ssl,
            )

            # Connect to TaHoma gateway
            connect_result = asyncio.run_coroutine_threadsafe(
                self.tahoma_client.connect(), self.mainloop
            ).result(timeout=30)

            if not connect_result:
                LOGGER.error("Failed to connect to TaHoma gateway")
                self.Notices["error"] = (
                    "Failed to connect to TaHoma - check token and gateway PIN"
                )
                self.setDriver("ST", 2)
                return

            LOGGER.info("Successfully connected to TaHoma gateway")

        except Exception as e:
            LOGGER.error(f"Error connecting to TaHoma: {e}", exc_info=True)
            self.Notices["error"] = f"TaHoma connection error: {e}"
            self.setDriver("ST", 2)
            return

        # Discover and wait for discovery to complete
        discoverSuccess = asyncio.run_coroutine_threadsafe(
            self.discover(), self.mainloop
        ).result()

        # first update from Gateway
        if not discoverSuccess:
            # start-up failed
            LOGGER.error(
                f"First discovery & update from Gateway failed!!! exit {self.name}"
            )
            self.Notices["error"] = (
                "Error first discovery-update.  Check config / hardware & restart"
            )
            self.setDriver("ST", 2)
            return

        # Queue initial update event for all devices
        with self.devices_map_lock:
            self.gateway_event.append(
                {
                    "evt": "home",
                    "devices": list(self.devices_map.keys()),
                    "scenarios": list(self.scenarios_map.keys()),
                }
            )
        LOGGER.info(f"first update event[0]: {self.gateway_event[0]}")

        # Start event polling loop (replaces SSE client)
        if not self.event_polling_in:
            self.start_event_polling()

        # signal to the nodes, its ok to start
        self.ready_event.set()

        # clear inital start-up message
        if self.Notices.get("hello"):
            self.Notices.delete("hello")

        LOGGER.info(f"exit {self.name}")

    def node_queue(self, data):
        """Queues a node address to signify its creation is complete.

        This method, used in conjunction with wait_for_node_done(), provides a
        mechanism to synchronize node creation, as the addNode operation is
        asynchronous.

        Args:
            data (dict): The data payload from the ADDNODEDONE event,
                         containing the node's address.
        """
        address = data.get("address")
        if address:
            with self.queue_condition:
                self.n_queue.append(address)
                self.queue_condition.notify()

    def wait_for_node_done(self):
        """Waits for a node to be fully added before proceeding.

        See node_queue() for more details on the synchronization mechanism.
        """
        with self.queue_condition:
            while not self.n_queue:
                self.queue_condition.wait(timeout=0.2)
            self.n_queue.pop()

    def get_shade_data(self, sid):
        """Gets shade data from the internal map in a thread-safe manner.

        Args:
            sid (str): The device URL or shade ID to retrieve.

        Returns:
            dict or None: The device data dictionary if found, otherwise None.
        """
        with self.devices_map_lock:
            return self.devices_map.get(sid)

    def update_shade_data(self, sid, data):
        """Updates or adds device data in the internal map in a thread-safe manner.

        Args:
            sid (str): The device URL or shade ID to update or add.
            data (dict): The dictionary of device data to store.
        """
        with self.devices_map_lock:
            if sid in self.devices_map:
                self.devices_map[sid].update(data)
            else:
                self.devices_map[sid] = data

    def append_gateway_event(self, event):
        """Appends a new event from the gateway to the event queue.

        This method is called by the SSE client thread to add an incoming event
        to the shared gateway_event list and notify consumer threads that a new
        event is available.

        Args:
            event (dict): The event data received from the gateway.
        """
        with self.gateway_event_condition:
            self.gateway_event.append(event)
            self.gateway_event_condition.notify_all()  # Wake up all waiting consumers

    def get_gateway_event(self) -> list[dict]:
        """Waits for and returns the list of gateway events.

        This method is used by consumer threads to wait for new events to be
        posted to the gateway_event list. It blocks until events are available.

        Returns:
            list[dict]: A reference to the list containing gateway events.
        """
        with self.gateway_event_condition:
            while not self.gateway_event:
                self.gateway_event_condition.wait()
            return self.gateway_event  # return reference, not a copy

    def remove_gateway_event(self, event):
        """Removes a processed event from the gateway event queue.

        Args:
            event (dict): The event object to remove from the queue.
        """
        with self.gateway_event_condition:
            if event in self.gateway_event:
                self.gateway_event.remove(event)

    def config_done(self):
        """Finalizes configuration setup after Polyglot has loaded.

        This method is called by Polyglot once the configuration is fully loaded.
        It's used to set up features that depend on the initial configuration,
        such as custom log levels.
        """
        LOGGER.debug("enter")
        self.poly.addLogLevel("DEBUG_MODULES", 9, "Debug + Modules")
        LOGGER.debug("exit")

    def dataHandler(self, data):
        """Handles the loading of custom data from Polyglot.

        This method is called on startup to load any persistent custom data
        that was saved by the node.

        Args:
            data (dict): A dictionary containing the custom data.
        """
        LOGGER.debug(f"enter: Loading data {data}")
        if data is None:
            LOGGER.warning("No custom data")
        else:
            self.Data.load(data)
            LOGGER.info(f"Custom data:{self.Data}")
        self.handler_data_st = True
        self.check_handlers()

    def parameterHandler(self, params):
        """Handles updates to custom parameters from the Polyglot dashboard.

        This method is called when a user changes the custom parameters in the
        Polyglot UI. It loads the new parameters and re-validates them.

        Args:
            params (dict): A dictionary of the custom parameters.
        """
        LOGGER.debug("Loading parameters now")
        if params:
            self.Parameters.load(params)

        defaults = {
            # TaHoma/Phantom Blinds parameters
            "tahoma_token": "",  # Bearer token from TaHoma app Developer Mode
            "gateway_pin": "",  # Gateway PIN (e.g., 2001-0001-1891)
            "use_local_api": "true",  # Use local API (true) or cloud API (false)
            "verify_ssl": "true",  # Verify SSL certificates
            # Legacy parameter (kept for migration reference, not used)
            "gatewayip": "",
        }
        for param, default_value in defaults.items():
            if param not in self.Parameters:
                self.Parameters[param] = default_value
            if self.checkParams():
                self.handler_params_st = True
        self.check_handlers()

    def typedParameterHandler(self, params):
        """Handles the creation of custom typed parameters.

        This method is called when the custom typed parameters are first
        created by Polyglot.

        Args:
            params (dict): A dictionary of the typed parameters' structure.
        """
        LOGGER.debug("Loading typed parameters now")
        self.TypedParameters.load(params)
        LOGGER.debug(params)
        self.handler_typedparams_st = True
        self.check_handlers()

    def typedDataHandler(self, data):
        """Handles updates to custom typed data from the Polyglot dashboard.

        This method is called when a user enters or updates data in the
        custom typed parameters UI.

        Args:
            data (dict): A dictionary of the custom typed data.
        """
        LOGGER.debug("Loading typed data now")
        if data is None:
            LOGGER.warning("No custom data")
        else:
            self.TypedData.load(data)
        LOGGER.debug(f"Loaded typed data {data}")
        self.handler_typeddata_st = True
        self.check_handlers()

    def check_handlers(self):
        """Checks if all startup handlers have completed and signals an event.

        This method is called after each handler completes. Once all handlers
        (parameters, data, etc.) have finished their startup tasks, it sets
        an event to signal that the main startup process can continue.
        """
        if (
            self.handler_params_st
            and self.handler_data_st
            and self.handler_typedparams_st
            and self.handler_typeddata_st
        ):
            self.all_handlers_st_event.set()
            LOGGER.info("All parameters loaded & good")

    def handleLevelChange(self, level):
        """Handles a change in the log level.

        Args:
            level (dict): A dictionary containing the new log level.
        """
        LOGGER.info(f"enter: level={level}")
        if level["level"] < 10:
            LOGGER.info("Setting basic config to DEBUG...")
            LOG_HANDLER.set_basic_config(True, logging.DEBUG)
        else:
            LOGGER.info("Setting basic config to INFO...")
            LOG_HANDLER.set_basic_config(True, logging.INFO)
        LOGGER.info(f"exit: level={level}")

    def checkParams(self):
        """Validates the custom parameters for the controller.

        This method checks TaHoma-specific parameters (token and gateway PIN).

        Returns:
            bool: True if parameters are valid, False otherwise.
        """
        self.Notices.delete("config")

        # Check for required TaHoma token
        token = self.Parameters.get("tahoma_token", "")
        is_valid, error_msg = validate_bearer_token(token)
        if not is_valid:
            LOGGER.error(f"Bearer token validation failed: {error_msg}")
            self.Notices["config"] = error_msg
            return False

        # Check for gateway PIN
        gateway_pin = self.Parameters.get("gateway_pin", "")
        is_valid, error_msg = validate_gateway_pin(gateway_pin)
        if not is_valid:
            LOGGER.error(f"Gateway PIN validation failed: {error_msg}")
            self.Notices["config"] = error_msg
            return False

        # Store validated parameters
        self.token = token
        self.gateway_pin = gateway_pin
        use_local = self.Parameters.get("use_local_api")
        verify = self.Parameters.get("verify_ssl")
        self.use_local_api = use_local.lower() == "true" if use_local else True
        self.verify_ssl = verify.lower() == "true" if verify else True

        LOGGER.info(f"TaHoma configuration valid - Gateway PIN: {gateway_pin}")
        self.Notices.delete("config")
        return True

    def poll(self, flag):
        """Handles polling requests from Polyglot.

        This method is called by Polyglot for both short and long polls.

        Args:
            flag (str): A string indicating the type of poll ('shortPoll' or 'longPoll').
        """
        LOGGER.debug("enter")
        # no updates until node is through start-up
        if not self.ready_event:
            LOGGER.error("Node not ready yet, exiting")
            return

        # pause updates when in discovery
        if self.discovery_in:
            LOGGER.debug("exit, in discovery")
            return

        if "shortPoll" in flag:
            LOGGER.debug("shortPoll controller")

            # Event polling is started automatically in start()
            # eventTimer has no purpose beyond an indicator of how long since the last event
            self.eventTimer += 1
            LOGGER.info(f"increment eventTimer = {self.eventTimer}")
            self.heartbeat()

            # start event polling loop
            if not self.event_polling_in:
                self.start_event_polling()

        if "longPoll" in flag:
            # TaHoma uses real-time events, no polling needed
            LOGGER.debug("longPoll - TaHoma uses event-based updates")
        LOGGER.debug("exit")

    def start_event_polling(self):
        """Starts the background task for polling TaHoma events.

        This initiates the asynchronous event polling loop that continuously
        fetches events from the TaHoma gateway (replaces SSE streaming).
        """
        LOGGER.debug("Starting event polling...")
        self.stop_event.clear()
        future = asyncio.run_coroutine_threadsafe(self._poll_events(), self.mainloop)
        LOGGER.info(f"Event polling started: {future}")
        LOGGER.debug("exit")
        return

    async def _poll_events(self):
        """Poll TaHoma events (replaces SSE streaming).

        This async method polls the TaHoma gateway for events at 1-second intervals
        (per Somfy recommendations). It registers an event listener and continuously
        fetches events, handling listener expiration and errors gracefully.
        """
        self.event_polling_in = True
        LOGGER.info("Starting TaHoma event polling...")

        retries = 0
        max_retries = 5
        base_delay = 1

        try:
            # Ensure tahoma_client is initialized
            assert self.tahoma_client is not None, "TaHoma client not initialized"

            # Register event listener
            if not self.tahoma_client.event_listener_id:
                listener_id = await self.tahoma_client.register_event_listener()
                LOGGER.info(f"Event listener registered: {listener_id}")

            while not self.stop_event.is_set():
                try:
                    # Fetch events (Somfy recommends max once per second)
                    events = await self.tahoma_client.fetch_events()

                    if events:
                        LOGGER.debug(f"Received {len(events)} events")
                        for event in events:
                            self.process_tahoma_event(event)
                        retries = 0  # Reset on successful fetch

                except InvalidEventListenerIdException:
                    # Listener expired (after 10 min inactivity), re-register
                    LOGGER.warning("Event listener expired, re-registering...")
                    try:
                        listener_id = await self.tahoma_client.register_event_listener()
                        LOGGER.info(f"Event listener re-registered: {listener_id}")
                    except Exception as e:
                        LOGGER.error(f"Failed to re-register event listener: {e}")
                        if retries >= max_retries:
                            LOGGER.error("Max retries reached. Stopping event polling.")
                            break
                        delay = base_delay * (2**retries)
                        LOGGER.warning(f"Retrying in {delay}s")
                        await asyncio.sleep(delay)
                        retries += 1
                        continue

                except NoRegisteredEventListenerException:
                    LOGGER.error("No registered event listener")
                    # Try to register new listener
                    try:
                        listener_id = await self.tahoma_client.register_event_listener()
                        LOGGER.info(f"Event listener registered: {listener_id}")
                    except Exception as e:
                        LOGGER.error(f"Failed to register event listener: {e}")
                        break

                except Exception as e:
                    LOGGER.error(f"Event polling error: {e}", exc_info=True)
                    if retries >= max_retries:
                        LOGGER.error("Max retries reached. Stopping event polling.")
                        break
                    delay = base_delay * (2**retries)
                    await asyncio.sleep(delay)
                    retries += 1
                    continue

                # Poll every 1 second (Somfy recommendation)
                await asyncio.sleep(1)

        except Exception as e:
            LOGGER.error(f"Fatal event polling error: {e}", exc_info=True)
        finally:
            self.event_polling_in = False
            LOGGER.info("Event polling stopped")

    def process_tahoma_event(self, event):
        """Process event from TaHoma gateway.

        Maps TaHoma event types to internal actions and updates nodes accordingly.

        Args:
            event: Event object from pyoverkiz

        TaHoma Event Types:
            - DeviceStateChangedEvent: Device state changed (shade moved, etc.)
            - ExecutionRegisteredEvent: Command execution started
            - ExecutionStateChangedEvent: Command execution state changed
            - GatewayAliveEvent: Gateway heartbeat/connection restored
            - ScenarioAddedEvent: New scenario added
            - ScenarioUpdatedEvent: Scenario modified
            - DeviceAddedEvent: New device added
            - DeviceRemovedEvent: Device removed
        """
        event_name = event.name if hasattr(event, "name") else str(event)

        LOGGER.debug(f"Processing TaHoma event: {event_name}")

        try:
            if event_name == "DeviceStateChangedEvent":
                # Device state changed (shade moved, tilt changed, etc.)
                self._handle_device_state_event(event)

            elif event_name == "ExecutionRegisteredEvent":
                # Command execution started
                LOGGER.debug(f"Execution registered: {event}")
                self.eventTimer = 0

            elif event_name == "ExecutionStateChangedEvent":
                # Command execution state changed (completed, failed, etc.)
                LOGGER.debug(f"Execution state changed: {event}")

            elif event_name == "GatewayAliveEvent":
                # Gateway heartbeat / connection restored
                LOGGER.debug("Gateway alive event")
                self.eventTimer = 0

            elif event_name == "ScenarioAddedEvent":
                # New scenario added - trigger discovery
                LOGGER.info(f"New scenario added - triggering discovery: {event}")
                asyncio.run_coroutine_threadsafe(self.discover(), self.mainloop)

            elif event_name == "DeviceAddedEvent":
                # New device added - trigger discovery
                LOGGER.info(f"New device added - triggering discovery: {event}")
                asyncio.run_coroutine_threadsafe(self.discover(), self.mainloop)

            elif event_name == "DeviceRemovedEvent":
                # Device removed - trigger discovery to clean up
                LOGGER.info(f"Device removed - triggering discovery: {event}")
                asyncio.run_coroutine_threadsafe(self.discover(), self.mainloop)

            else:
                # Log unknown event types for future implementation
                LOGGER.debug(f"Unhandled event type: {event_name}")

        except Exception as e:
            LOGGER.error(f"Error processing event {event_name}: {e}", exc_info=True)

    def _handle_device_state_event(self, event):
        """Handle device state changed events.

        Updates node drivers when device state changes (position, tilt, etc.).

        Args:
            event: DeviceStateChangedEvent from TaHoma
        """
        try:
            device_url = event.device_url if hasattr(event, "device_url") else None
            if not device_url:
                LOGGER.warning(f"Device state event missing device_url: {event}")
                return

            # Find the node for this device
            nodes = self.poly.getNodes()
            for node_addr, node in nodes.items():
                if hasattr(node, "device_url") and node.device_url == device_url:
                    # Update node with new state
                    if hasattr(event, "device_states"):
                        node.update_drivers_from_states(event.device_states)
                    LOGGER.debug(f"Updated node {node_addr} from state event")
                    break

        except Exception as e:
            LOGGER.error(f"Error handling device state event: {e}", exc_info=True)

    def query(self, command=None):
        """Queries all nodes and reports their current status.

        This method is typically called by Polyglot in response to a 'Query'
        command from the ISY. It fetches the latest data from the gateway and
        then asks each child node to report its drivers.

        Args:
            command (dict, optional): The command payload from Polyglot.
                                      Defaults to None.
        """
        LOGGER.info(f"Enter {command}")
        # TaHoma uses real-time events, just report current values
        nodes = self.poly.getNodes()
        for node in nodes:
            nodes[node].reportDrivers()
        LOGGER.debug("Exit")

    def updateProfile(self, command=None):
        """Initiates a profile update in Polyglot.

        This is typically called in response to an 'Update Profile' command
        from the ISY.

        Args:
            command (dict, optional): The command payload from Polyglot.
                                      Defaults to None.

        Returns:
            bool: The result of the profile update operation.
        """
        LOGGER.info(f"Enter {command}")
        st = self.poly.updateProfile()
        LOGGER.debug("Exit")
        return st

    def discover_cmd(self, command=None):
        """Handles the 'Discover' command from Polyglot.

        This method is a wrapper around the main `discover` async method,
        allowing it to be called from a synchronous command handler.

        Args:
            command (dict, optional): The command payload from Polyglot.
                                      Defaults to None.
        """
        LOGGER.info(f"Enter {command}")
        # run discover
        if asyncio.run_coroutine_threadsafe(self.discover(), self.mainloop).result():
            LOGGER.info("Success")
        else:
            LOGGER.error("Failure")
        LOGGER.debug("Exit")

    async def discover(self):
        """Discovers all devices and scenarios from TaHoma and creates nodes.

        This async method fetches all device data from the TaHoma gateway,
        compares it with existing nodes in Polyglot, and creates, updates,
        or removes nodes as necessary.

        Returns:
            bool: True if discovery was successful, False otherwise.
        """
        success = False
        if self.discovery_in:
            LOGGER.info("Discover already running.")
            return success

        self.discovery_in = True
        LOGGER.info("Starting TaHoma discovery...")

        nodes_existing = self.poly.getNodes()
        LOGGER.debug(f"current nodes = {nodes_existing}")
        nodes_old = [node for node in nodes_existing if node != "hdctrl"]
        nodes_new = []

        try:
            # Ensure tahoma_client is initialized
            assert self.tahoma_client is not None, "TaHoma client not initialized"

            # Get all devices from TaHoma
            devices = await self.tahoma_client.get_devices()
            LOGGER.info(f"Retrieved {len(devices)} devices from TaHoma")

            # Discover and create device nodes
            self._discover_devices(devices, nodes_existing, nodes_new)

            # Get all scenarios (scenes) from TaHoma
            scenarios = await self.tahoma_client.get_scenarios()
            LOGGER.info(f"Retrieved {len(scenarios)} scenarios from TaHoma")

            # Discover and create scenario nodes
            self._discover_scenarios(scenarios, nodes_existing, nodes_new)

            # Cleanup removed nodes
            self._cleanup_nodes(nodes_new, nodes_old)

            # Update node count
            self.numNodes = len(nodes_new)
            self.setDriver("GV0", self.numNodes)

            LOGGER.debug(f"devices_map:  {list(self.devices_map.keys())}")
            LOGGER.debug(f"scenarios_map:  {list(self.scenarios_map.keys())}")
            success = True

        except Exception as e:
            LOGGER.error(f"Discovery failed: {e}", exc_info=True)
            success = False

        LOGGER.info(f"Discovery complete. success = {success}")
        self.discovery_in = False
        return success

    def _discover_devices(self, devices, nodes_existing, nodes_new):
        """Discovers and creates nodes for TaHoma devices.

        Args:
            devices (list): List of Device objects from TaHoma
            nodes_existing (dict): Dictionary of existing nodes in Polyglot
            nodes_new (list): List to be populated with discovered node addresses
        """
        for device in devices:
            try:
                device_url = device.deviceURL

                # Convert deviceURL to node address
                node_address = self._device_url_to_address(device_url)

                # Store device in map
                with self.devices_map_lock:
                    self.devices_map[device_url] = {
                        "device": device,
                        "address": node_address,
                        "label": device.label,
                        "controllableName": device.controllable_name,
                    }

                nodes_new.append(node_address)

                if node_address not in nodes_existing:
                    # Create new device node
                    node = self._create_device_node(device, node_address)
                    if node:
                        LOGGER.info(
                            f"Adding device node: {node_address} ({device.label})"
                        )
                        self.poly.addNode(node)
                        self.wait_for_node_done()
                    else:
                        LOGGER.warning(
                            f"Could not create node for device: {device.label}"
                        )

            except Exception as e:
                LOGGER.error(
                    f"Error discovering device {device.label}: {e}", exc_info=True
                )

    def _discover_scenarios(self, scenarios, nodes_existing, nodes_new):
        """Discovers and creates nodes for TaHoma scenarios (scenes).

        Args:
            scenarios (list): List of Scenario objects from TaHoma
            nodes_existing (dict): Dictionary of existing nodes in Polyglot
            nodes_new (list): List to be populated with discovered node addresses
        """
        for scenario in scenarios:
            try:
                scenario_oid = scenario.oid
                node_address = f"scene{scenario_oid}"

                # Store scenario in map
                self.scenarios_map[scenario_oid] = {
                    "scenario": scenario,
                    "address": node_address,
                    "label": scenario.label,
                }

                nodes_new.append(node_address)

                if node_address not in nodes_existing:
                    # Create new scenario node
                    LOGGER.info(
                        f"Adding scenario node: {node_address} ({scenario.label})"
                    )
                    node = Scene(
                        self.poly,
                        self.address,
                        node_address,
                        scenario.label,
                        scenario_oid,
                    )
                    self.poly.addNode(node)
                    self.wait_for_node_done()

            except Exception as e:
                LOGGER.error(
                    f"Error discovering scenario {scenario.label}: {e}", exc_info=True
                )

    def _cleanup_nodes(self, nodes_new, nodes_old):
        """Removes any nodes that are no longer present on the gateway.

        Args:
            nodes_new (list): A list of node addresses that were found during
                              the current discovery process.
            nodes_old (list): A list of node addresses that existed before
                              the current discovery process.
        """
        nodes_db = self.poly.getNodesFromDb()
        LOGGER.debug(f"db nodes = {nodes_db}")

        nodes_current = self.poly.getNodes()
        nodes_get = {key: nodes_current[key] for key in nodes_current if key != self.id}

        LOGGER.debug(f"old nodes = {nodes_old}")
        LOGGER.debug(f"new nodes = {nodes_new}")
        LOGGER.debug(f"pre-delete nodes = {nodes_get}")

        for node in nodes_get:
            if node not in nodes_new:
                LOGGER.info(f"need to delete node {node}")
                self.poly.delNode(node)

        if set(nodes_get) == set(nodes_new):
            LOGGER.info("Discovery NO NEW activity")

    def _create_device_node(self, device, node_address):
        """Creates the appropriate device node based on TaHoma device type.

        Args:
            device: Device object from TaHoma
            node_address (str): The node address for the new device

        Returns:
            Node: An instance of the appropriate Shade node class, or None
        """
        controllable = device.controllable_name
        label = device.label
        device_url = device.deviceURL

        LOGGER.debug(f"Creating node for device type: {controllable}")

        # Map TaHoma controllableNames to node classes
        # Based on Somfy device capabilities

        if "VenetianBlind" in controllable:
            # Venetian blinds have tilt capability
            LOGGER.info(f"Creating Shade node (with tilt) for {label}")
            return Shade(self.poly, self.address, node_address, label, device_url)

        elif "DualRollerShutter" in controllable:
            # Dual roller shutters have primary + secondary
            LOGGER.info(f"Creating ShadeNoTilt node (dual) for {label}")
            return ShadeNoTilt(self.poly, self.address, node_address, label, device_url)

        elif "ExteriorScreen" in controllable or "Screen" in controllable:
            # Screens typically only primary position
            LOGGER.info(f"Creating ShadeOnlyPrimary node (screen) for {label}")
            return ShadeOnlyPrimary(
                self.poly, self.address, node_address, label, device_url
            )

        elif "RollerShutter" in controllable:
            # Standard roller shutters - primary position only
            LOGGER.info(f"Creating ShadeOnlyPrimary node (roller) for {label}")
            return ShadeOnlyPrimary(
                self.poly, self.address, node_address, label, device_url
            )

        elif "Awning" in controllable:
            # Awnings - primary position only
            LOGGER.info(f"Creating ShadeOnlyPrimary node (awning) for {label}")
            return ShadeOnlyPrimary(
                self.poly, self.address, node_address, label, device_url
            )

        elif "Curtain" in controllable:
            # Curtains - primary position only
            LOGGER.info(f"Creating ShadeOnlyPrimary node (curtain) for {label}")
            return ShadeOnlyPrimary(
                self.poly, self.address, node_address, label, device_url
            )

        else:
            # Unknown device type - use generic shade with full capabilities
            LOGGER.warning(
                f"Unknown device type '{controllable}' - creating generic Shade node for {label}"
            )
            return Shade(self.poly, self.address, node_address, label, device_url)

    def _device_url_to_address(self, device_url: str) -> str:
        """Convert TaHoma deviceURL to valid Polyglot node address.

        TaHoma deviceURL format: io://1234-5678-9012/12345678
        Node address: sh12345678 (max 14 chars, alphanumeric + underscore)

        Args:
            device_url (str): TaHoma device URL

        Returns:
            str: Valid Polyglot node address
        """
        # Extract device ID from URL (last part after /)
        device_id = device_url.split("/")[-1]

        # Create address with 'sh' prefix (sh = shade)
        # Ensure it fits in 14 character limit
        address = f"sh{device_id}"[:14]

        # Convert to lowercase (Polyglot convention)
        return address.lower()

    def delete(self):
        """Handles node deletion from Polyglot.

        This method is called by Polyglot upon deletion of the NodeServer.
        If the process is co-resident and controlled by Polyglot, it will be
        terminated within 5 seconds of receiving this message. It sets the
        node status to off and stops background tasks.
        """
        self.setDriver("ST", 0, report=True, force=True)
        self.stop_event.set()
        LOGGER.info("bye bye ... deleted.")

    def stop(self):
        """Handles the shutdown sequence for the node.

        This method is called by Polyglot when the NodeServer is stopped.
        It performs cleanup tasks such as disconnecting from TaHoma,
        stopping event polling, and setting the driver status to off.
        """
        LOGGER.info("Stopping NodeServer...")

        # Stop event polling
        self.stop_event.set()

        # Disconnect from TaHoma
        if self.tahoma_client and self.tahoma_client.is_connected:
            try:
                asyncio.run_coroutine_threadsafe(
                    self.tahoma_client.disconnect(), self.mainloop
                ).result(timeout=10)
                LOGGER.info("Disconnected from TaHoma")
            except Exception as e:
                LOGGER.error(f"Error disconnecting from TaHoma: {e}")

        self.setDriver("ST", 0, report=True, force=True)
        self.Notices.clear()
        LOGGER.info("NodeServer stopped.")

    def heartbeat(self):
        """Sends a heartbeat signal to the ISY.

        This method alternates sending 'DON' and 'DOF' commands to the controller
        node, allowing ISY programs to monitor the NodeServer's status.
        """
        LOGGER.debug(f"heartbeat: hb={self.hb}")
        command = "DOF" if self.hb else "DON"
        self.reportCmd(command, 2)
        self.hb = not self.hb
        LOGGER.debug("Exit")

    def removeNoticesAll(self, command=None):
        """Removes all custom notices from the Polyglot dashboard.

        Args:
            command (dict, optional): The command payload from Polyglot.
                                      Defaults to None.
        """
        LOGGER.info(f"remove_notices_all: notices={self.Notices} , {command}")
        # Remove all existing notices
        self.Notices.clear()
        LOGGER.debug("Exit")

    """
    UOMs:
    25: index
    107: Raw 1-byte unsigned value

    Driver controls:
    ST: Status
    GV0: Custom Control 0
    """
    drivers = [
        {"driver": "ST", "value": 1, "uom": 25, "name": "Controller Status"},
        {"driver": "GV0", "value": 0, "uom": 107, "name": "NumberOfNodes"},
    ]

    """
    Commands that this node can handle.
    Should match the 'accepts' section of the nodedef file.
    """
    commands = {
        "QUERY": query,
        "DISCOVER": discover_cmd,
        "UPDATE_PROFILE": updateProfile,
        "REMOVE_NOTICES_ALL": removeNoticesAll,
    }
