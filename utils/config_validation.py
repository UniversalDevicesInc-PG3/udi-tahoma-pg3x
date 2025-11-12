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
