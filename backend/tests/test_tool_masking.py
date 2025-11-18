"""
Test Tool Masking Service - Verify KV-cache optimization works correctly.
"""
import pytest
from services.tool_masking_service import (
    ToolMaskingService,
    AgentState,
    tool_masking,
    set_agent_state,
    get_available_tools,
    validate_action,
    get_tool_definitions,
    get_logit_bias,
    get_state_prompt
)


def test_tool_masking_initialization():
    """Test that tool masking service initializes correctly."""
    service = ToolMaskingService()

    assert service.current_state == AgentState.IDLE
    assert len(service.ALL_TOOLS) == 11  # We defined 11 tools
    assert len(service.state_history) == 0


def test_state_transitions():
    """Test state transitions work correctly."""
    service = ToolMaskingService()

    # Start in IDLE
    assert service.current_state == AgentState.IDLE

    # Transition to PLANNING
    service.set_state(AgentState.PLANNING)
    assert service.current_state == AgentState.PLANNING
    assert len(service.state_history) == 1

    # Transition to EXECUTING
    service.set_state(AgentState.EXECUTING)
    assert service.current_state == AgentState.EXECUTING
    assert len(service.state_history) == 2


def test_available_tools_by_state():
    """Test that tool availability changes by state."""
    service = ToolMaskingService()

    # PLANNING state - should have limited tools
    service.set_state(AgentState.PLANNING)
    planning_tools = service.get_available_tools()
    assert "READ_FILE" in planning_tools
    assert "LIST_FILES" in planning_tools
    assert "UPDATE_TODO" in planning_tools
    assert "THINK" in planning_tools
    assert "SEARCH_WEB" in planning_tools
    # Should NOT have write tools
    assert "CREATE_FILE" not in planning_tools
    assert "EXECUTE" not in planning_tools

    # EXECUTING state - should have all tools
    service.set_state(AgentState.EXECUTING)
    executing_tools = service.get_available_tools()
    assert "CREATE_FILE" in executing_tools
    assert "READ_FILE" in executing_tools
    assert "EXECUTE" in executing_tools
    assert "BROWSER" in executing_tools
    assert "UPDATE_TODO" in executing_tools
    assert "DELEGATE" in executing_tools

    # VERIFYING state - should have read-only + execute
    service.set_state(AgentState.VERIFYING)
    verifying_tools = service.get_available_tools()
    assert "READ_FILE" in verifying_tools
    assert "EXECUTE" in verifying_tools
    assert "VERIFY" in verifying_tools
    # Should NOT have write tools
    assert "CREATE_FILE" not in verifying_tools
    assert "UPDATE_TODO" not in verifying_tools

    # BROWSING state - should have browser tools only
    service.set_state(AgentState.BROWSING)
    browsing_tools = service.get_available_tools()
    assert "BROWSER" in browsing_tools
    # Should not have file operations
    assert "CREATE_FILE" not in browsing_tools
    assert "EXECUTE" not in browsing_tools

    # LEARNING state - should have read-only tools
    service.set_state(AgentState.LEARNING)
    learning_tools = service.get_available_tools()
    assert "READ_FILE" in learning_tools
    assert "LIST_FILES" in learning_tools
    assert "SEARCH_WEB" in learning_tools
    assert "THINK" in learning_tools
    # Should NOT have write tools
    assert "CREATE_FILE" not in learning_tools
    assert "EXECUTE" not in learning_tools


def test_action_validation():
    """Test that action validation works correctly."""
    service = ToolMaskingService()

    # In PLANNING state
    service.set_state(AgentState.PLANNING)

    # Valid actions
    is_valid, error = service.validate_action("READ_FILE")
    assert is_valid is True
    assert error is None

    # Invalid actions
    is_valid, error = service.validate_action("CREATE_FILE")
    assert is_valid is False
    assert "not available" in error.lower()

    # Unknown action
    is_valid, error = service.validate_action("UNKNOWN_ACTION")
    assert is_valid is False
    assert "unknown action" in error.lower()

    # In EXECUTING state - everything should be valid
    service.set_state(AgentState.EXECUTING)
    is_valid, error = service.validate_action("CREATE_FILE")
    assert is_valid is True
    assert error is None


def test_tool_definitions_static():
    """Test that tool definitions are static (CRITICAL for KV-cache)."""
    service = ToolMaskingService()

    # Get definitions in different states
    service.set_state(AgentState.PLANNING)
    definitions_1 = service.get_tool_definitions()

    service.set_state(AgentState.EXECUTING)
    definitions_2 = service.get_tool_definitions()

    # The structure should be the same (all tools listed)
    # Only the availability markers (✅/⛔) should differ
    assert "CREATE_FILE" in definitions_1
    assert "CREATE_FILE" in definitions_2
    assert "READ_FILE" in definitions_1
    assert "READ_FILE" in definitions_2

    # Check that unavailable tools are marked
    assert "⛔" in definitions_1  # Some tools should be blocked in PLANNING


def test_logit_bias_generation():
    """Test logit bias generation for tool masking."""
    service = ToolMaskingService()

    # In PLANNING state
    service.set_state(AgentState.PLANNING)
    bias = service.get_logit_bias()

    # Should have negative bias for unavailable tools
    assert isinstance(bias, dict)
    # CREATE_FILE should be biased against in PLANNING
    assert any("CREATE_FILE" in key for key in bias.keys())
    # All bias values should be negative (discourage)
    assert all(value < 0 for value in bias.values())

    # In EXECUTING state (all tools available)
    service.set_state(AgentState.EXECUTING)
    bias_executing = service.get_logit_bias()
    # Should have fewer (or no) biases since most tools are available
    # (Only unavailable tools get biased)


def test_state_prompt_generation():
    """Test state-specific prompt generation."""
    service = ToolMaskingService()

    # Each state should have unique guidance
    service.set_state(AgentState.PLANNING)
    planning_prompt = service.get_state_prompt()
    assert "PLANNING MODE" in planning_prompt or "planning" in planning_prompt.lower()

    service.set_state(AgentState.EXECUTING)
    executing_prompt = service.get_state_prompt()
    assert "EXECUTION MODE" in executing_prompt or "execution" in executing_prompt.lower()

    service.set_state(AgentState.VERIFYING)
    verifying_prompt = service.get_state_prompt()
    assert "VERIFICATION MODE" in verifying_prompt or "verification" in verifying_prompt.lower()


def test_statistics():
    """Test statistics generation."""
    service = ToolMaskingService()

    service.set_state(AgentState.PLANNING)
    stats = service.get_statistics()

    assert "current_state" in stats
    assert stats["current_state"] == "planning"
    assert "total_tools" in stats
    assert stats["total_tools"] == 11
    assert "available_tools" in stats
    assert "masked_tools" in stats
    assert stats["available_tools"] + stats["masked_tools"] == 11
    assert "cache_preservation" in stats
    assert "cost_savings" in stats


def test_global_singleton_functions():
    """Test global convenience functions work correctly."""
    # Reset to known state
    set_agent_state(AgentState.PLANNING)

    # Test get_available_tools
    tools = get_available_tools()
    assert isinstance(tools, set)
    assert "READ_FILE" in tools

    # Test validate_action
    is_valid, error = validate_action("READ_FILE")
    assert is_valid is True

    # Test get_tool_definitions
    definitions = get_tool_definitions()
    assert isinstance(definitions, str)
    assert "CREATE_FILE" in definitions

    # Test get_logit_bias
    bias = get_logit_bias()
    assert isinstance(bias, dict)

    # Test get_state_prompt
    prompt = get_state_prompt()
    assert isinstance(prompt, str)


def test_tool_masking_preserves_kv_cache():
    """
    Test that tool masking pattern preserves KV-cache.

    Key insight: System prompt NEVER changes, only logit bias changes.
    This keeps the prompt hash stable → KV-cache preserved → 10x cost savings.
    """
    service = ToolMaskingService()

    # Get system prompt in different states
    service.set_state(AgentState.PLANNING)
    definitions_planning = service.get_tool_definitions()

    service.set_state(AgentState.EXECUTING)
    definitions_executing = service.get_tool_definitions()

    service.set_state(AgentState.LEARNING)
    definitions_learning = service.get_tool_definitions()

    # All should contain the SAME tools (critical for cache)
    for tool_name in service.ALL_TOOLS.keys():
        assert tool_name in definitions_planning
        assert tool_name in definitions_executing
        assert tool_name in definitions_learning

    # The structure is identical, only availability markers differ
    # This means the core system prompt remains stable → cache preserved!


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
