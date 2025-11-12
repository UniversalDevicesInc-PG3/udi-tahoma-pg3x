"""Unit tests for TaHoma client wrapper.

(C) 2025 Stephen Jenkins
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from utils.tahoma_client import TaHomaClient, create_tahoma_client


@pytest.fixture
def mock_overkiz_client():
    """Mock OverkizClient for testing."""
    with patch("utils.tahoma_client.OverkizClient") as mock:
        client = Mock()
        client.login = AsyncMock()
        client.get_devices = AsyncMock(return_value=[])
        client.get_scenarios = AsyncMock(return_value=[])
        client.register_event_listener = AsyncMock(return_value="listener-123")
        client.fetch_events = AsyncMock(return_value=[])
        client.execute_command = AsyncMock(return_value="exec-456")
        client.execute_scenario = AsyncMock(return_value="exec-789")
        mock.return_value = client
        yield mock, client


@pytest.mark.asyncio
async def test_tahoma_client_init():
    """Test TaHoma client initialization."""
    client = TaHomaClient(token="test-token", gateway_pin="1234-5678-9012")

    assert client.token == "test-token"
    assert client.gateway_pin == "1234-5678-9012"
    assert not client.is_connected
    assert client.event_listener_id is None


@pytest.mark.asyncio
async def test_tahoma_client_connect(mock_overkiz_client):
    """Test TaHoma client connection."""
    mock_class, mock_instance = mock_overkiz_client

    client = TaHomaClient(token="test-token", gateway_pin="1234-5678-9012")

    result = await client.connect()

    assert result is True
    assert client.is_connected
    mock_instance.login.assert_called_once()


@pytest.mark.asyncio
async def test_tahoma_client_get_devices(mock_overkiz_client):
    """Test getting devices from TaHoma."""
    mock_class, mock_instance = mock_overkiz_client

    # Setup mock devices
    mock_device = Mock()
    mock_device.device_url = "io://1234-5678-9012/12345678"
    mock_device.label = "Test Shade"
    mock_instance.get_devices.return_value = [mock_device]

    client = TaHomaClient(token="test-token", gateway_pin="1234-5678-9012")
    await client.connect()

    devices = await client.get_devices()

    assert len(devices) == 1
    assert devices[0].device_url == "io://1234-5678-9012/12345678"


@pytest.mark.asyncio
async def test_tahoma_client_execute_command(mock_overkiz_client):
    """Test executing a command."""
    mock_class, mock_instance = mock_overkiz_client

    client = TaHomaClient(token="test-token", gateway_pin="1234-5678-9012")
    await client.connect()

    exec_id = await client.execute_command(
        device_url="io://1234-5678-9012/12345678",
        command_name="setClosure",
        parameters=[50],
    )

    assert exec_id == "exec-456"
    mock_instance.execute_command.assert_called_once()


@pytest.mark.asyncio
async def test_tahoma_client_register_event_listener(mock_overkiz_client):
    """Test registering event listener."""
    mock_class, mock_instance = mock_overkiz_client

    client = TaHomaClient(token="test-token", gateway_pin="1234-5678-9012")
    await client.connect()

    listener_id = await client.register_event_listener()

    assert listener_id == "listener-123"
    assert client.event_listener_id == "listener-123"


@pytest.mark.asyncio
async def test_tahoma_client_fetch_events(mock_overkiz_client):
    """Test fetching events."""
    mock_class, mock_instance = mock_overkiz_client

    # Setup mock events
    mock_event = Mock()
    mock_event.name = "DeviceStateChangedEvent"
    mock_instance.fetch_events.return_value = [mock_event]

    client = TaHomaClient(token="test-token", gateway_pin="1234-5678-9012")
    await client.connect()
    await client.register_event_listener()

    events = await client.fetch_events()

    assert len(events) == 1
    assert events[0].name == "DeviceStateChangedEvent"


@pytest.mark.asyncio
async def test_tahoma_client_disconnect(mock_overkiz_client):
    """Test disconnecting from TaHoma."""
    mock_class, mock_instance = mock_overkiz_client
    mock_instance.unregister_event_listener = AsyncMock()

    client = TaHomaClient(token="test-token", gateway_pin="1234-5678-9012")
    await client.connect()
    await client.register_event_listener()
    await client.disconnect()

    assert not client.is_connected
    assert client.event_listener_id is None


@pytest.mark.asyncio
async def test_tahoma_client_not_connected_error():
    """Test error when executing command without connection."""
    client = TaHomaClient(token="test-token", gateway_pin="1234-5678-9012")

    with pytest.raises(RuntimeError, match="Not connected"):
        await client.get_devices()


@pytest.mark.asyncio
async def test_create_tahoma_client_convenience(mock_overkiz_client):
    """Test convenience function for creating client."""
    mock_class, mock_instance = mock_overkiz_client

    client = await create_tahoma_client(
        token="test-token", gateway_pin="1234-5678-9012"
    )

    assert client.is_connected
    mock_instance.login.assert_called_once()


@pytest.mark.asyncio
async def test_get_device_url_from_address():
    """Test helper to get device_url from node address."""
    client = TaHomaClient(token="test-token", gateway_pin="1234-5678-9012")

    # Mock devices
    mock_device1 = Mock()
    mock_device1.device_url = "io://1234-5678-9012/12345678"
    mock_device2 = Mock()
    mock_device2.device_url = "io://1234-5678-9012/87654321"

    devices = [mock_device1, mock_device2]

    # Test finding device
    device_url = client.get_device_url_from_address("sh12345678", devices)  # type: ignore[arg-type]
    assert device_url == "io://1234-5678-9012/12345678"

    # Test not found
    device_url = client.get_device_url_from_address("sh99999999", devices)  # type: ignore[arg-type]
    assert device_url is None
