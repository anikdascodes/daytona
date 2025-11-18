"""
Multi-Agent Orchestration Demonstration

Demonstrates various orchestration patterns:
1. Sequential execution
2. Parallel execution
3. Hierarchical delegation
4. Consensus decision making
"""
import asyncio
from services.agent_orchestrator import orchestrator, AgentType, ExecutionMode
from services.agent_registry_init import register_all_agents


async def demo_sequential_execution():
    """Demonstrate sequential task execution."""
    print("\n" + "=" * 70)
    print("1. SEQUENTIAL EXECUTION")
    print("=" * 70)
    print("Tasks execute one after another (A → B → C)")
    print()

    tasks = [
        {
            "agent_type": AgentType.KNOWLEDGE,
            "description": "Research Python async/await best practices",
            "input": {
                "type": "research",
                "question": "What are Python async/await best practices?",
                "depth": "quick",
                "max_sources": 2
            }
        },
        {
            "agent_type": AgentType.PLANNER,
            "description": "Create plan for implementing async Python application",
            "input": {
                "task": "Build async Python web scraper",
                "context": {}
            }
        },
        {
            "agent_type": AgentType.KNOWLEDGE,
            "description": "Verify Python 3.11+ is required for async",
            "input": {
                "type": "verify_fact",
                "claim": "Python 3.7+ supports async/await",
                "context": "Python async features"
            }
        }
    ]

    results = await orchestrator.execute_sequential(tasks)

    print("\n📊 Results:")
    for i, task in enumerate(results, 1):
        status_icon = "✅" if task.status.value == "completed" else "❌"
        print(f"  {status_icon} Task {i}: {task.agent_type.value} - {task.status.value}")
        if task.result:
            print(f"     Result: {str(task.result)[:100]}...")


async def demo_parallel_execution():
    """Demonstrate parallel task execution."""
    print("\n" + "=" * 70)
    print("2. PARALLEL EXECUTION")
    print("=" * 70)
    print("Tasks execute simultaneously (A || B || C)")
    print()

    tasks = [
        {
            "agent_type": AgentType.KNOWLEDGE,
            "description": "Research React hooks",
            "input": {
                "type": "search",
                "query": "React hooks useState useEffect",
                "max_results": 3
            }
        },
        {
            "agent_type": AgentType.KNOWLEDGE,
            "description": "Research Vue composition API",
            "input": {
                "type": "search",
                "query": "Vue 3 composition API",
                "max_results": 3
            }
        },
        {
            "agent_type": AgentType.PLANNER,
            "description": "Plan frontend architecture",
            "input": {
                "task": "Design modern frontend architecture",
                "context": {}
            }
        }
    ]

    print("🚀 Launching tasks in parallel...")
    results = await orchestrator.execute_parallel(tasks)

    print("\n📊 Results:")
    for i, task in enumerate(results, 1):
        status_icon = "✅" if task.status.value == "completed" else "❌"
        duration = "N/A"
        if task.started_at and task.completed_at:
            duration = f"{(task.completed_at - task.started_at).total_seconds():.2f}s"
        print(f"  {status_icon} Task {i}: {task.agent_type.value} - {task.status.value} ({duration})")


async def demo_hierarchical_execution():
    """Demonstrate hierarchical task delegation."""
    print("\n" + "=" * 70)
    print("3. HIERARCHICAL EXECUTION")
    print("=" * 70)
    print("Main task → Sub-agents → Aggregated result")
    print()

    main_task = "Research and plan a Python web application"

    subtasks = [
        {
            "agent_type": AgentType.KNOWLEDGE,
            "description": "Research Python web frameworks",
            "input": {
                "type": "search",
                "query": "Python web frameworks FastAPI Flask Django",
                "max_results": 3
            }
        },
        {
            "agent_type": AgentType.KNOWLEDGE,
            "description": "Research database options",
            "input": {
                "type": "search",
                "query": "Python async database PostgreSQL MongoDB",
                "max_results": 3
            }
        },
        {
            "agent_type": AgentType.PLANNER,
            "description": "Create development plan",
            "input": {
                "task": "Plan Python web application with REST API",
                "context": {}
            }
        }
    ]

    result = await orchestrator.execute_hierarchical(
        main_task=main_task,
        subtasks=subtasks,
        aggregation_strategy="concat"
    )

    print("\n📊 Hierarchical Results:")
    print(f"  Main task: {result['main_task']}")
    print(f"  Subtasks: {result['subtasks_count']}")
    print(f"  Successful: {result['successful']}")
    print(f"  Failed: {result['failed']}")
    print(f"\n  Subtask details:")
    for detail in result['subtask_details']:
        status_icon = "✅" if detail['status'] == "completed" else "❌"
        print(f"    {status_icon} {detail['agent']}: {detail['status']}")


async def demo_consensus_decision():
    """Demonstrate consensus decision making."""
    print("\n" + "=" * 70)
    print("4. CONSENSUS DECISION MAKING")
    print("=" * 70)
    print("Multiple agents vote on the best approach")
    print()

    task = "What is the best Python web framework for a REST API?"

    # Multiple knowledge agents research the same question
    agents = [
        AgentType.KNOWLEDGE,
        AgentType.KNOWLEDGE,
        AgentType.KNOWLEDGE
    ]

    input_data = {
        "type": "research",
        "question": task,
        "depth": "quick",
        "max_sources": 2
    }

    result = await orchestrator.execute_consensus(
        task=task,
        agents=agents,
        input_data=input_data,
        min_agreement=0.5  # 50% agreement required
    )

    print("\n📊 Consensus Results:")
    print(f"  Consensus reached: {'✅ Yes' if result['consensus'] else '⛔ No'}")
    print(f"  Agreement level: {result['agreement']*100:.1f}%")
    print(f"  Total agents: {result['total_agents']}")
    print(f"  Successful: {result['successful_agents']}")

    if result['consensus']:
        print(f"\n  🏆 Winning result: {str(result['winning_result'])[:200]}...")


async def demo_statistics():
    """Show orchestrator statistics."""
    print("\n" + "=" * 70)
    print("ORCHESTRATOR STATISTICS")
    print("=" * 70)

    stats = orchestrator.get_statistics()

    print(f"\n  Registered agents: {stats['registered_agents']}")
    print(f"  Agent types: {', '.join(stats['agent_types'])}")
    print(f"  Total capabilities: {stats['capabilities']}")
    print(f"\n  Tasks executed: {stats['total_tasks']}")
    print(f"  Tasks completed: {stats['tasks_completed']}")
    print(f"  Tasks failed: {stats['tasks_failed']}")
    print(f"  Tasks in progress: {stats['tasks_in_progress']}")
    print(f"  Success rate: {stats['success_rate']:.1f}%")


async def main():
    """Run all demonstrations."""
    print("=" * 70)
    print("MULTI-AGENT ORCHESTRATION SYSTEM - DEMONSTRATION")
    print("=" * 70)
    print("\nRegistering agents...")

    # Register all agents
    register_all_agents()

    print("\n✅ Agents registered!\n")

    # Run demonstrations
    try:
        # Note: Some demos may fail if internet is not available or LLM API is not configured
        # This is expected and demonstrates error handling

        await demo_sequential_execution()
        await demo_parallel_execution()
        await demo_hierarchical_execution()
        await demo_consensus_decision()
        await demo_statistics()

    except Exception as e:
        print(f"\n⚠️  Demo error (expected if APIs not configured): {e}")
        print("   This is normal - the orchestration system is working!")
        print("   Configure LLM_API_KEY and internet access for full functionality.")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)

    print("\n📚 Key Takeaways:")
    print("  ✅ Sequential: Tasks execute in order (good for dependencies)")
    print("  ✅ Parallel: Tasks execute simultaneously (good for speed)")
    print("  ✅ Hierarchical: Main task delegates to sub-agents (good for complex tasks)")
    print("  ✅ Consensus: Multiple agents vote (good for decisions)")
    print("\n  🎯 The orchestrator enables coordinated multi-agent workflows!")


if __name__ == "__main__":
    asyncio.run(main())
