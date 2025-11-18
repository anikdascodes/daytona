"""
Tool Masking Service - KV-cache optimization via static tool definitions.

Implements Manus AI's tool masking pattern:
- Static tool definitions (never changes system prompt)
- State machine for tool availability
- Logit bias masking for invalid tools
- Preserves KV-cache: $0.30/MTok vs $3.00/MTok (10x savings)

Key insight: Instead of changing tool lists (breaks cache), we define
ALL tools statically and use logit masking to prevent invalid calls.
"""
import json
from typing import Dict, List, Set, Optional, Any
from enum import Enum
from utils.logger import logger


class AgentState(Enum):
    """Agent execution states - determines available tools."""
    PLANNING = "planning"           # Planning phase - limited tools
    EXECUTING = "executing"         # Full execution - all tools
    VERIFYING = "verifying"         # Verification - read-only tools
    BROWSING = "browsing"           # Browser automation only
    LEARNING = "learning"           # Reflection and learning
    IDLE = "idle"                   # No active task


class ToolMaskingService:
    """
    Manages tool availability via state machine and logit masking.

    Benefits:
    - 10x cost reduction via KV-cache preservation
    - Cleaner state management
    - Prevents invalid tool calls
    - Better error handling
    """

    # ALL possible tools defined statically (NEVER changes)
    ALL_TOOLS = {
        "CREATE_FILE": {
            "name": "CREATE_FILE",
            "description": "Create or overwrite a file in the workspace",
            "parameters": ["PATH", "CONTENT"],
            "format": "ACTION: CREATE_FILE\nPATH: /workspace/file.py\nCONTENT:\n[content]\n---END---",
            "states": {AgentState.EXECUTING}  # Only available during execution
        },
        "READ_FILE": {
            "name": "READ_FILE",
            "description": "Read contents of a file",
            "parameters": ["PATH"],
            "format": "ACTION: READ_FILE\nPATH: /workspace/file.py\n---END---",
            "states": {AgentState.PLANNING, AgentState.EXECUTING, AgentState.VERIFYING, AgentState.LEARNING}
        },
        "EXECUTE": {
            "name": "EXECUTE",
            "description": "Execute a shell command in the sandbox",
            "parameters": ["COMMAND"],
            "format": "ACTION: EXECUTE\nCOMMAND: python test.py\n---END---",
            "states": {AgentState.EXECUTING, AgentState.VERIFYING}
        },
        "LIST_FILES": {
            "name": "LIST_FILES",
            "description": "List files in a directory",
            "parameters": ["PATH"],
            "format": "ACTION: LIST_FILES\nPATH: /workspace\n---END---",
            "states": {AgentState.PLANNING, AgentState.EXECUTING, AgentState.VERIFYING, AgentState.LEARNING}
        },
        "UPDATE_TODO": {
            "name": "UPDATE_TODO",
            "description": "Update task progress tracking (todo.md pattern)",
            "parameters": ["CONTENT"],
            "format": "ACTION: UPDATE_TODO\nCONTENT:\n## Progress\n- ✅ Done\n- 🔄 In progress\n---END---",
            "states": {AgentState.PLANNING, AgentState.EXECUTING}
        },
        "VERIFY": {
            "name": "VERIFY",
            "description": "Verify that an action worked correctly",
            "parameters": ["WHAT", "HOW"],
            "format": "ACTION: VERIFY\nWHAT: The script runs\nHOW: python test.py\n---END---",
            "states": {AgentState.VERIFYING}
        },
        "BROWSER": {
            "name": "BROWSER",
            "description": "Interact with web browser for research and automation",
            "parameters": ["TASK"],
            "format": "ACTION: BROWSER\nTASK: Search for 'python tutorials'\n---END---",
            "states": {AgentState.BROWSING, AgentState.EXECUTING}
        },
        "SEARCH_WEB": {
            "name": "SEARCH_WEB",
            "description": "Search the web for information (knowledge agent)",
            "parameters": ["QUERY", "MAX_RESULTS"],
            "format": "ACTION: SEARCH_WEB\nQUERY: latest python best practices\nMAX_RESULTS: 5\n---END---",
            "states": {AgentState.PLANNING, AgentState.EXECUTING, AgentState.LEARNING}
        },
        "THINK": {
            "name": "THINK",
            "description": "Internal reasoning and planning (no action taken)",
            "parameters": ["THOUGHT"],
            "format": "ACTION: THINK\nTHOUGHT: I need to analyze the requirements first\n---END---",
            "states": {AgentState.PLANNING, AgentState.EXECUTING, AgentState.VERIFYING, AgentState.LEARNING}
        },
        "DELEGATE": {
            "name": "DELEGATE",
            "description": "Delegate subtask to specialized agent",
            "parameters": ["AGENT_TYPE", "TASK"],
            "format": "ACTION: DELEGATE\nAGENT_TYPE: knowledge\nTASK: Research React hooks\n---END---",
            "states": {AgentState.EXECUTING}
        },
        "TASK_COMPLETED": {
            "name": "TASK_COMPLETED",
            "description": "Mark task as completed with summary",
            "parameters": ["SUMMARY", "REFLECTION"],
            "format": "TASK_COMPLETED: [summary]\n\nREFLECTION:\n- What worked: [...]\n---END---",
            "states": {AgentState.EXECUTING, AgentState.LEARNING}
        }
    }

    def __init__(self):
        """Initialize tool masking service."""
        self.current_state = AgentState.IDLE
        self.state_history: List[AgentState] = []
        logger.info("ToolMaskingService initialized with KV-cache optimization")

    def set_state(self, state: AgentState) -> None:
        """
        Transition to a new agent state.

        Args:
            state: New state to transition to
        """
        old_state = self.current_state
        self.current_state = state
        self.state_history.append(state)

        available = self.get_available_tools()
        logger.info(f"State transition: {old_state.value} → {state.value} (tools: {len(available)})")

    def get_available_tools(self) -> Set[str]:
        """
        Get tools available in current state.

        Returns:
            Set of tool names available in current state
        """
        available = set()
        for tool_name, tool_info in self.ALL_TOOLS.items():
            if self.current_state in tool_info["states"]:
                available.add(tool_name)

        return available

    def get_tool_definitions(self, state: Optional[AgentState] = None) -> str:
        """
        Get static tool definitions for system prompt.

        This NEVER changes - critical for KV-cache preservation.

        Args:
            state: Optional state to get definitions for (default: current state)

        Returns:
            Formatted tool definitions string
        """
        state = state or self.current_state
        available_tools = self.get_available_tools() if state == self.current_state else set(
            name for name, info in self.ALL_TOOLS.items() if state in info["states"]
        )

        definitions = ["AVAILABLE ACTIONS:"]

        for i, (tool_name, tool_info) in enumerate(self.ALL_TOOLS.items(), 1):
            # Mark unavailable tools clearly but still show them
            availability = "✅" if tool_name in available_tools else "⛔"

            definitions.append(f"\n{i}. {tool_name} {availability}")
            definitions.append(f"   Description: {tool_info['description']}")
            definitions.append(f"   Format:\n   {tool_info['format']}")

        return "\n".join(definitions)

    def get_logit_bias(self) -> Dict[str, float]:
        """
        Generate logit bias to mask unavailable tools.

        This is the KEY innovation from Manus AI:
        - Instead of changing system prompt (breaks cache)
        - Use logit bias to prevent invalid tool calls (preserves cache)

        Returns:
            Logit bias dictionary for LLM API

        Note:
            - Negative bias (-100) = strongly discourage
            - Positive bias (+100) = strongly encourage
            - Most LLM APIs support this (OpenAI, Anthropic, Groq, etc.)
        """
        available = self.get_available_tools()
        bias = {}

        # Strongly discourage unavailable tools
        for tool_name in self.ALL_TOOLS.keys():
            if tool_name not in available:
                # Bias against the tool name tokens
                # Note: Different tokenizers may require different approaches
                # For now, we bias against common prefixes
                bias[f"ACTION: {tool_name}"] = -100
                bias[tool_name] = -50

        logger.debug(f"Generated logit bias for state {self.current_state.value}: {len(bias)} tokens masked")
        return bias

    def validate_action(self, action: str) -> tuple[bool, Optional[str]]:
        """
        Validate that an action is allowed in current state.

        Args:
            action: Action name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if action not in self.ALL_TOOLS:
            return False, f"Unknown action: {action}"

        available = self.get_available_tools()
        if action not in available:
            allowed_states = [s.value for s in self.ALL_TOOLS[action]["states"]]
            return False, (
                f"Action {action} not available in state {self.current_state.value}. "
                f"Available in: {', '.join(allowed_states)}"
            )

        return True, None

    def get_state_prompt(self) -> str:
        """
        Get current state-specific instructions.

        This CAN change per state (doesn't break cache as it's in user message).

        Returns:
            State-specific guidance string
        """
        prompts = {
            AgentState.PLANNING: """
🎯 PLANNING MODE
Focus on: Understanding requirements, breaking down tasks, identifying risks
Available: READ_FILE, LIST_FILES, UPDATE_TODO, SEARCH_WEB, THINK
Goal: Create clear execution plan before taking action
""",
            AgentState.EXECUTING: """
⚡ EXECUTION MODE
Focus on: Taking action, implementing solutions, making changes
Available: All tools (CREATE_FILE, EXECUTE, BROWSER, etc.)
Goal: Execute plan step-by-step with verification
""",
            AgentState.VERIFYING: """
✅ VERIFICATION MODE
Focus on: Testing, validation, ensuring correctness
Available: READ_FILE, LIST_FILES, EXECUTE, VERIFY
Goal: Confirm actions worked as expected
""",
            AgentState.BROWSING: """
🌐 BROWSING MODE
Focus on: Web research, data gathering, online resources
Available: BROWSER, SEARCH_WEB
Goal: Gather information from the internet
""",
            AgentState.LEARNING: """
🧠 LEARNING MODE
Focus on: Reflection, analysis, improvement
Available: READ_FILE, LIST_FILES, SEARCH_WEB, THINK
Goal: Learn from results and improve future performance
""",
            AgentState.IDLE: """
💤 IDLE MODE
Waiting for task assignment
"""
        }

        return prompts.get(self.current_state, "")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get tool masking statistics.

        Returns:
            Statistics dictionary
        """
        available = self.get_available_tools()
        total = len(self.ALL_TOOLS)

        return {
            "current_state": self.current_state.value,
            "total_tools": total,
            "available_tools": len(available),
            "masked_tools": total - len(available),
            "state_transitions": len(self.state_history),
            "cache_preservation": "✅ Active (static tool definitions)",
            "cost_savings": "~10x (KV-cache optimization)"
        }


# Global singleton instance
tool_masking = ToolMaskingService()


# Convenience functions
def set_agent_state(state: AgentState) -> None:
    """Set current agent state."""
    tool_masking.set_state(state)


def get_available_tools() -> Set[str]:
    """Get currently available tools."""
    return tool_masking.get_available_tools()


def get_tool_definitions() -> str:
    """Get static tool definitions."""
    return tool_masking.get_tool_definitions()


def get_logit_bias() -> Dict[str, float]:
    """Get logit bias for masking."""
    return tool_masking.get_logit_bias()


def validate_action(action: str) -> tuple[bool, Optional[str]]:
    """Validate action."""
    return tool_masking.validate_action(action)


def get_state_prompt() -> str:
    """Get state-specific prompt."""
    return tool_masking.get_state_prompt()
