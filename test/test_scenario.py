"""Tests for TaHoma scenario parsing."""

from utils.scenario import TaHomaScenario, parse_action_group


def test_parse_action_group_minimal():
    scenario = parse_action_group({"label": "Morning", "oid": "1234567890"})
    assert scenario == TaHomaScenario(oid="1234567890", label="Morning")


def test_parse_action_group_with_extra_fields():
    scenario = parse_action_group(
        {
            "label": "Evening",
            "oid": "999",
            "actions": [{"deviceURL": "rts://pin/1", "commands": []}],
            "creationTime": 1710000000,
        }
    )
    assert scenario == TaHomaScenario(oid="999", label="Evening")


def test_parse_action_group_camel_case():
    scenario = parse_action_group(
        {"Label": "Away", "OID": "42", "creationTime": 1, "actions": []}
    )
    assert scenario == TaHomaScenario(oid="42", label="Away")


def test_parse_action_group_missing_oid():
    assert parse_action_group({"label": "No Id"}) is None


def test_parse_action_group_uses_oid_as_fallback_label():
    scenario = parse_action_group({"oid": "555"})
    assert scenario == TaHomaScenario(oid="555", label="555")
