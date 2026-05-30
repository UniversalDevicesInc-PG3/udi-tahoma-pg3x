"""Configuration validation utilities for TaHoma NodeServer.

This module provides validation functions for configuration parameters
to ensure they meet the required format and contain valid values.

(C) 2025 Stephen Jenkins
"""

import re
import logging
from typing import Optional

LOGGER = logging.getLogger(__name__)

# Polyglot UI placeholder defaults (must be replaced before connecting).
DEFAULT_GATEWAY_PIN = "0000-0000-0000"
DEFAULT_TAHOMA_TOKEN = "0" * 20
DEFAULT_GATEWAY_IP = "gateway-0000-0000-0000.local"


def is_default_gateway_pin(pin: str) -> bool:
    """Return True if pin is the unset Polyglot placeholder."""
    return pin.strip() == DEFAULT_GATEWAY_PIN


def is_default_tahoma_token(token: str) -> bool:
    """Return True if token is the unset Polyglot placeholder."""
    value = token.strip()
    return value == DEFAULT_TAHOMA_TOKEN or (bool(value) and set(value) == {"0"})


def is_default_gateway_ip(gateway_ip: str) -> bool:
    """Return True if gateway_ip is empty or the unset Polyglot placeholder."""
    value = gateway_ip.strip()
    return not value or value == DEFAULT_GATEWAY_IP


def normalize_tahoma_token(token: str) -> str:
    """Strip whitespace and an optional Bearer prefix from the configured token."""
    value = token.strip()
    if value.lower().startswith("bearer "):
        value = value[7:].strip()
    return value


def normalize_gateway_ip(gateway_ip: str, gateway_pin: str) -> Optional[str]:
    """Return gateway IP/hostname to use, or None for gateway-{pin}.local."""
    _ = gateway_pin  # reserved; hostname is derived from PIN when IP is omitted
    if is_default_gateway_ip(gateway_ip):
        return None
    return gateway_ip.strip()


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

    if is_default_gateway_pin(pin):
        return False, (
            "Gateway PIN is still set to the default placeholder (0000-0000-0000). "
            "Enter your TaHoma PIN from the device label or app."
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

    # Remove whitespace and optional Bearer prefix from UI paste
    token = normalize_tahoma_token(token)

    if is_default_tahoma_token(token):
        return False, (
            "Bearer token is still set to the default placeholder. "
            "Generate a token in the TaHoma app Developer Mode and paste it here."
        )

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
