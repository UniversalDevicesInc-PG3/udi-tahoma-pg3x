"""Tests for exec_status Last Command mapping."""

from pyoverkiz.enums.execution import ExecutionState

from utils.exec_status import (
    LAST_CMD_COMPLETED,
    LAST_CMD_FAILED,
    LAST_CMD_PENDING,
    execution_state_to_last_cmd,
    last_cmd_label,
    scenario_parent_exec_to_last_cmd,
)


def test_execution_state_to_last_cmd_terminal():
    assert execution_state_to_last_cmd(ExecutionState.COMPLETED) == LAST_CMD_COMPLETED
    assert execution_state_to_last_cmd(ExecutionState.FAILED) == LAST_CMD_FAILED
    assert execution_state_to_last_cmd(ExecutionState.NOT_TRANSMITTED) == LAST_CMD_FAILED


def test_execution_state_to_last_cmd_pending():
    assert execution_state_to_last_cmd(ExecutionState.IN_PROGRESS) == LAST_CMD_PENDING
    assert execution_state_to_last_cmd("TRANSMITTED") == LAST_CMD_PENDING


def test_last_cmd_label():
    assert last_cmd_label(LAST_CMD_COMPLETED) == "Completed"
    assert last_cmd_label(LAST_CMD_FAILED) == "Failed"


def test_scenario_parent_exec_ignores_spurious_failed():
    assert (
        scenario_parent_exec_to_last_cmd(ExecutionState.FAILED) is None
    )
    assert (
        scenario_parent_exec_to_last_cmd(ExecutionState.INITIALIZED)
        == LAST_CMD_PENDING
    )
    assert (
        scenario_parent_exec_to_last_cmd(ExecutionState.COMPLETED)
        == LAST_CMD_COMPLETED
    )
    assert (
        scenario_parent_exec_to_last_cmd(ExecutionState.NOT_TRANSMITTED)
        == LAST_CMD_FAILED
    )
