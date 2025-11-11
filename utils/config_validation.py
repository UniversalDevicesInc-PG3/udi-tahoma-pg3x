"""Configuration validation utilities for TaHoma NodeServer.

This module provides validation functions for configuration parameters
to ensure they meet the required format and contain valid values.

(C) 2025 Stephen Jenkins
"""

import re
import logging

LOGGER = logging.getLogger(__name__)


def validate_gateway_pin(pin: str) -> tuple[bool, str]:
    """Validate TaHoma gateway PIN format.

    Args:
        pin: Gateway PIN string

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_gateway_pin("1234-5678-9012")
        (True, "")
        >>> validate_gateway_pin("1234")
        (False, "Invalid PIN format...")
    """
    if not pin:
        return False, "Gateway PIN is required"

    # Remove whitespace
    pin = pin.strip()

    # Check format: NNNN-NNNN-NNNN
    pattern = r"^\d{4}-\d{4}-\d{4}$"
    if not re.match(pattern, pin):
        return False, (
            f"Invalid gateway PIN format: '{pin}'. "
            "Expected format: 1234-5678-9012 (12 digits with dashes)"
        )

    LOGGER.debug(f"Gateway PIN format valid: {pin}")
    return True, ""


def validate_bearer_token(token: str) -> tuple[bool, str]:
    """Validate TaHoma bearer token.

    Args:
        token: Bearer token string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not token:
        return False, (
            "Bearer token is required. "
            "Generate in TaHoma app: Settings > Developer Mode > Generate Token"
        )

    # Remove whitespace
    token = token.strip()

    # Check minimum length (tokens are typically 50+ characters)
    if len(token) < 20:
        return False, (
            f"Bearer token seems too short ({len(token)} chars). "
            "Tokens are typically 50+ characters. "
            "Verify you copied the complete token from TaHoma app."
        )

    # Check for common copy/paste errors
    if " " in token:
        return False, (
            "Bearer token contains spaces. "
            "Ensure you copied the complete token without line breaks."
        )

    if "\n" in token or "\r" in token:
        return False, (
            "Bearer token contains line breaks. "
            "Ensure you copied the complete token as a single line."
        )

    # Check for placeholder text
    placeholder_texts = [
        "your-bearer-token",
        "abc123",
        "example",
        "token-here",
        "paste-token",
    ]
    if any(placeholder in token.lower() for placeholder in placeholder_texts):
        return False, (
            "Bearer token appears to be placeholder text. "
            "Replace with actual token from TaHoma app."
        )

    LOGGER.debug(f"Bearer token format valid (length: {len(token)})")
    return True, ""


def validate_boolean_param(value: str, param_name: str) -> tuple[bool, str]:
    """Validate boolean configuration parameter.

    Args:
        value: Parameter value string
        param_name: Name of parameter for error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value:
        return True, ""  # Use default

    value_lower = value.strip().lower()
    valid_values = ["true", "false", "1", "0", "yes", "no"]

    if value_lower not in valid_values:
        return False, (
            f"Invalid value for {param_name}: '{value}'. "
            f"Expected: true/false, yes/no, or 1/0"
        )

    return True, ""


def validate_network_connectivity(gateway_pin: str) -> tuple[bool, str]:
    """Check if TaHoma gateway is reachable on network.

    Args:
        gateway_pin: Gateway PIN for hostname construction

    Returns:
        Tuple of (is_reachable, error_message)

    Note:
        This is a basic check and may not work in all network configurations.
    """
    import socket

    # Construct hostname
    hostname = f"gateway-{gateway_pin}.local"
    port = 8443

    try:
        # Try to resolve hostname
        socket.getaddrinfo(hostname, port, socket.AF_INET)
        LOGGER.debug(f"Successfully resolved {hostname}")
        return True, ""
    except socket.gaierror:
        return False, (
            f"Cannot resolve TaHoma hostname: {hostname}. "
            "Possible issues:\n"
            "  1. TaHoma not connected to network (check LED - should be green)\n"
            "  2. TaHoma on different network segment\n"
            "  3. mDNS not working (try adding TaHoma to /etc/hosts)\n"
            "  4. Incorrect gateway PIN"
        )
    except Exception as e:
        LOGGER.warning(f"Network check failed: {e}")
        return False, f"Network check failed: {str(e)}"


def get_helpful_error_message(error_type: str, details: str = "") -> str:
    """Get user-friendly error message with troubleshooting steps.

    Args:
        error_type: Type of error (auth_failed, connection_failed, etc.)
        details: Additional error details

    Returns:
        Formatted error message with troubleshooting steps
    """
    messages = {
        "auth_failed": (
            "Authentication failed with TaHoma gateway.\n"
            "Troubleshooting steps:\n"
            "  1. Verify Developer Mode is enabled in TaHoma app\n"
            "  2. Generate a new Bearer token in TaHoma app\n"
            "  3. Ensure token was copied completely without spaces\n"
            "  4. Check that gateway PIN matches device label\n"
            "  5. Restart TaHoma gateway and try again"
        ),
        "connection_failed": (
            "Cannot connect to TaHoma gateway.\n"
            "Troubleshooting steps:\n"
            "  1. Check TaHoma LED is green (connected to network)\n"
            "  2. Verify TaHoma is on same network as Polisy/EISY\n"
            "  3. Try pinging: gateway-{pin}.local\n"
            "  4. Check firewall allows port 8443 (HTTPS)\n"
            "  5. Try rebooting TaHoma gateway"
        ),
        "ssl_error": (
            "SSL certificate verification failed.\n"
            "TaHoma uses self-signed certificates.\n"
            "Solutions:\n"
            "  1. Set 'verify_ssl' to 'false' in configuration (quick fix)\n"
            "  2. Install Somfy root CA certificate (proper fix):\n"
            "     curl -o /usr/local/share/ca-certificates/overkiz-root-ca.crt \\\n"
            "       https://ca.overkiz.com/overkiz-root-ca-2048.crt\n"
            "     sudo update-ca-certificates"
        ),
        "no_devices": (
            "No devices discovered from TaHoma.\n"
            "Troubleshooting steps:\n"
            "  1. Verify shades are paired in TaHoma app\n"
            "  2. Check shades are working in TaHoma app\n"
            "  3. Ensure Developer Mode has full API access\n"
            "  4. Try re-pairing shades with TaHoma\n"
            "  5. Check TaHoma is within 25-35 feet of shades"
        ),
        "timeout": (
            "Connection to TaHoma timed out.\n"
            "Troubleshooting steps:\n"
            "  1. Check network connectivity to TaHoma\n"
            "  2. Verify TaHoma is not overloaded (restart if needed)\n"
            "  3. Check network is not blocking HTTPS traffic\n"
            "  4. Increase timeout if network is slow\n"
            "  5. Try cloud API instead of local API"
        ),
    }

    base_message = messages.get(error_type, f"Error: {error_type}")

    if details:
        return f"{base_message}\n\nDetails: {details}"

    return base_message
