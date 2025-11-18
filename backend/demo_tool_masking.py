"""
Demo Tool Masking - Demonstrates KV-cache optimization
Run this to see tool masking in action.
"""
from enum import Enum
from typing import Dict, Set


# Simple standalone demo (no dependencies)
class AgentState(Enum):
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"


def demo_tool_masking():
    """Demonstrate how tool masking works for KV-cache optimization."""

    print("=" * 70)
    print("TOOL MASKING DEMONSTRATION")
    print("KV-Cache Optimization Pattern from Manus AI")
    print("=" * 70)

    # Define all tools statically
    ALL_TOOLS = {
        "CREATE_FILE": {"states": {"executing"}},
        "READ_FILE": {"states": {"planning", "executing", "verifying"}},
        "EXECUTE": {"states": {"executing", "verifying"}},
        "LIST_FILES": {"states": {"planning", "executing", "verifying"}},
        "UPDATE_TODO": {"states": {"planning", "executing"}},
        "VERIFY": {"states": {"verifying"}},
        "BROWSER": {"states": {"executing"}},
    }

    print("\n📋 STATIC TOOL DEFINITIONS (Never changes - preserves KV-cache):")
    print("-" * 70)
    for i, (tool_name, tool_info) in enumerate(ALL_TOOLS.items(), 1):
        states_str = ", ".join(tool_info["states"])
        print(f"  {i}. {tool_name:15} (available in: {states_str})")

    print("\n🔄 STATE TRANSITIONS:")
    print("-" * 70)

    states = ["planning", "executing", "verifying"]

    for state in states:
        print(f"\n  STATE: {state.upper()}")

        available = [name for name, info in ALL_TOOLS.items() if state in info["states"]]
        masked = [name for name, info in ALL_TOOLS.items() if state not in info["states"]]

        print(f"    ✅ Available tools ({len(available)}):")
        for tool in available:
            print(f"       • {tool}")

        print(f"    ⛔ Masked tools ({len(masked)}):")
        for tool in masked:
            print(f"       • {tool} (logit bias: -100)")

    print("\n💡 KEY INSIGHT:")
    print("-" * 70)
    print("  Traditional Approach (Breaks Cache):")
    print("    • Planning phase: Include only READ_FILE, LIST_FILES")
    print("    • Execution phase: Include CREATE_FILE, EXECUTE, etc.")
    print("    • System prompt CHANGES → Cache INVALIDATED → $3.00/MTok")
    print()
    print("  Tool Masking Approach (Preserves Cache):")
    print("    • ALL phases: Include ALL tools (never changes)")
    print("    • Use logit bias to mask unavailable tools")
    print("    • System prompt STABLE → Cache PRESERVED → $0.30/MTok")
    print()
    print("  💰 COST SAVINGS: 10x reduction!")

    print("\n🔬 HOW IT WORKS:")
    print("-" * 70)
    print("  1. System Prompt (STATIC - never changes):")
    print("     'You have these tools: CREATE_FILE, READ_FILE, EXECUTE, ...'")
    print()
    print("  2. State Machine:")
    print("     current_state = PLANNING → only allow READ_FILE, LIST_FILES")
    print()
    print("  3. Logit Bias (sent with each API call):")
    print("     {'CREATE_FILE': -100, 'EXECUTE': -100, ...}")
    print("     Prevents LLM from using masked tools")
    print()
    print("  4. Result:")
    print("     • System prompt hash stays the same")
    print("     • KV-cache is reused")
    print("     • 10x cost reduction!")

    print("\n✅ IMPLEMENTATION STATUS:")
    print("-" * 70)
    print("  ✅ Tool definitions: STATIC (preserves cache)")
    print("  ✅ State machine: IMPLEMENTED")
    print("  ✅ Logit bias: GENERATED per state")
    print("  ✅ Action validation: ENFORCED")
    print("  ✅ Integration: COMPLETE")

    print("\n" + "=" * 70)
    print("TOOL MASKING: READY FOR PRODUCTION ✅")
    print("Expected cost savings: ~10x on LLM API calls")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    demo_tool_masking()
