"""Tests for configuration validation utilities."""

from utils.config_validation import (
    DEFAULT_GATEWAY_IP,
    DEFAULT_GATEWAY_PIN,
    DEFAULT_TAHOMA_TOKEN,
    is_default_gateway_ip,
    is_default_gateway_pin,
    is_default_tahoma_token,
    normalize_gateway_ip,
    normalize_tahoma_token,
    validate_bearer_token,
    validate_gateway_pin,
)


def test_defaults_are_detected():
    assert is_default_gateway_pin(DEFAULT_GATEWAY_PIN)
    assert is_default_tahoma_token(DEFAULT_TAHOMA_TOKEN)
    assert is_default_gateway_ip(DEFAULT_GATEWAY_IP)
    assert is_default_gateway_ip("")


def test_validate_rejects_default_placeholders():
    ok, _ = validate_gateway_pin(DEFAULT_GATEWAY_PIN)
    assert not ok

    ok, _ = validate_bearer_token(DEFAULT_TAHOMA_TOKEN)
    assert not ok


def test_validate_accepts_real_values():
    ok, msg = validate_gateway_pin("2001-0001-1891")
    assert ok, msg

    ok, msg = validate_bearer_token("a" * 64)
    assert ok, msg


def test_normalize_gateway_ip_ignores_placeholder():
    assert normalize_gateway_ip(DEFAULT_GATEWAY_IP, "2001-0001-1891") is None
    assert normalize_gateway_ip("", "2001-0001-1891") is None
    assert (
        normalize_gateway_ip("192.168.1.100", "2001-0001-1891")
        == "192.168.1.100"
    )


def test_normalize_tahoma_token_strips_bearer_prefix():
    token = "a" * 64
    assert normalize_tahoma_token(f"Bearer {token}") == token


def test_validate_accepts_bearer_prefixed_token():
    token = "a" * 64
    ok, msg = validate_bearer_token(f"Bearer {token}")
    assert ok, msg
