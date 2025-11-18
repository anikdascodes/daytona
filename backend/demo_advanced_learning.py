"""
Demo: Advanced Learning Systems

Demonstrates all 5 components of the Advanced Learning System:
1. Learning Engine - Continuous learning from interactions
2. Knowledge Hub - Cross-agent knowledge sharing
3. Performance Optimizer - Historical performance analysis
4. Adaptive Strategy - Dynamic strategy selection
5. Knowledge Base Evolution - Persistent knowledge storage

Part of Phase 4, Task 4.5
"""
import asyncio
import time
from services.learning_engine import learning_engine, LearningType, ConfidenceLevel
from services.knowledge_hub import knowledge_hub, KnowledgeType, KnowledgePriority
from services.performance_optimizer import performance_optimizer, OptimizationType
from services.adaptive_strategy import adaptive_strategy, ExecutionStrategy, TaskComplexity
from services.knowledge_base_evolution import knowledge_base_evolution, KnowledgeState
from utils.logger import logger


async def demo_learning_engine():
    """Demonstrate Learning Engine capabilities."""
    print("\n" + "="*60)
    print("1. LEARNING ENGINE - Continuous Learning")
    print("="*60)

    # Simulate successful interactions
    print("\n📝 Recording successful interactions...")
    for i in range(3):
        interaction = await learning_engine.record_interaction(
            agent_type="code",
            task_description=f"Create Python function (iteration {i+1})",
            actions_taken=[
                {"type": "CREATE_FILE", "path": f"/workspace/func{i}.py"},
                {"type": "EXECUTE", "command": f"python /workspace/func{i}.py"}
            ],
            results=[
                {"success": True},
                {"success": True, "stdout": "Function created successfully"}
            ],
            success=True,
            completion_time=3.0 + i,
            iterations=2,
            errors_encountered=0,
            metadata={"language": "python"}
        )
        print(f"  ✅ Recorded interaction {i+1}: {interaction.interaction_id}")

    # Wait for pattern extraction
    await asyncio.sleep(0.5)

    # Get learnings
    print("\n🧠 Extracting learnings...")
    success_patterns = learning_engine.get_learnings_by_type(LearningType.SUCCESS_PATTERN)
    print(f"  📊 Success patterns learned: {len(success_patterns)}")

    for learning in success_patterns[:3]:
        print(f"    - {learning.title}")
        print(f"      Confidence: {learning.confidence.name}, Occurrences: {learning.occurrences}")

    # Get relevant learnings
    print("\n🔍 Finding relevant learnings for new task...")
    relevant = learning_engine.get_relevant_learnings(
        task_description="Create Python unit tests",
        agent_type="code",
        min_confidence=ConfidenceLevel.LOW
    )
    print(f"  📚 Found {len(relevant)} relevant learnings")

    # Statistics
    stats = learning_engine.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  - Total interactions: {stats['total_interactions']}")
    print(f"  - Total learnings: {stats['total_learnings']}")
    print(f"  - High-confidence learnings: {stats['high_confidence_learnings']}")


async def demo_knowledge_hub():
    """Demonstrate Knowledge Hub capabilities."""
    print("\n" + "="*60)
    print("2. KNOWLEDGE HUB - Cross-Agent Knowledge Sharing")
    print("="*60)

    # Share knowledge
    print("\n📢 Sharing knowledge between agents...")

    knowledge1 = await knowledge_hub.share_knowledge(
        source_agent="code",
        knowledge_type=KnowledgeType.SOLUTION,
        title="Fast sorting algorithm implementation",
        content="Use quicksort for O(n log n) performance with good average case",
        context={"language": "python", "complexity": "O(n log n)"},
        priority=KnowledgePriority.MEDIUM,
        tags={"algorithm", "sorting", "optimization"},
        channel_id="code"
    )
    print(f"  ✅ {knowledge1.source_agent} shared: {knowledge1.title}")

    knowledge2 = await knowledge_hub.broadcast_warning(
        source_agent="review",
        title="SQL Injection Vulnerability",
        content="Always use parameterized queries to prevent SQL injection attacks",
        context={"severity": "critical", "category": "security"}
    )
    print(f"  ⚠️  WARNING broadcast: SQL Injection Vulnerability")

    knowledge3 = await knowledge_hub.broadcast_discovery(
        source_agent="debug",
        title="Common off-by-one error pattern",
        content="Check loop boundaries carefully - use <= instead of < when inclusive",
        context={"type": "debugging", "common_error": "off_by_one"}
    )
    print(f"  🔍 DISCOVERY broadcast: Off-by-one error pattern")

    # Subscribe to channels
    print("\n📨 Setting up channel subscriptions...")
    knowledge_hub.subscribe_to_channel("test", "testing")
    knowledge_hub.subscribe_to_channel("code", "code")
    print("  ✅ Agents subscribed to channels")

    # Query knowledge
    print("\n🔎 Querying knowledge base...")
    results = knowledge_hub.query_knowledge(
        query="sorting algorithm",
        min_priority=KnowledgePriority.LOW,
        limit=5
    )
    print(f"  📚 Found {len(results)} relevant knowledge items")
    for k in results[:3]:
        print(f"    - {k.title} (from {k.source_agent})")

    # Get popular knowledge
    print("\n⭐ Most popular knowledge:")
    popular = knowledge_hub.get_popular_knowledge(limit=5)
    for k in popular[:3]:
        print(f"    - {k.title} ({k.useful_votes} votes, {k.applied_count} applications)")

    # Statistics
    stats = knowledge_hub.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  - Total knowledge items: {stats['total_knowledge_items']}")
    print(f"  - Total channels: {stats['total_channels']}")
    print(f"  - Total views: {stats['total_views']}")


async def demo_performance_optimizer():
    """Demonstrate Performance Optimizer capabilities."""
    print("\n" + "="*60)
    print("3. PERFORMANCE OPTIMIZER - Historical Performance Analysis")
    print("="*60)

    # Record executions
    print("\n📊 Recording execution metrics...")

    # Fast agent
    for i in range(5):
        performance_optimizer.record_execution(
            agent_type="code",
            task_category="simple_task",
            completion_time=5.0 + i*0.5,
            iterations=2,
            success=True,
            errors=0,
            actions_count=3
        )
    print("  ✅ Recorded 5 fast executions (code agent)")

    # Slow agent
    for i in range(5):
        performance_optimizer.record_execution(
            agent_type="slow_agent",
            task_category="complex_task",
            completion_time=45.0 + i*2,
            iterations=8,
            success=True,
            errors=1,
            actions_count=10
        )
    print("  ⚠️  Recorded 5 slow executions (slow_agent)")

    # Get agent performance
    print("\n📈 Agent Performance Summary:")
    perf_code = performance_optimizer.get_agent_performance("code")
    if "error" not in perf_code:
        print(f"  Code Agent:")
        print(f"    - Success rate: {perf_code['success_rate']*100:.1f}%")
        print(f"    - Avg time: {perf_code['avg_completion_time']:.1f}s")
        print(f"    - Avg iterations: {perf_code['avg_iterations']:.1f}")

    # Get recommendations
    print("\n💡 Optimization Recommendations:")
    recommendations = performance_optimizer.get_recommendations(min_priority=5)
    print(f"  Found {len(recommendations)} recommendations")

    for rec in recommendations[:3]:
        print(f"\n  🔧 {rec.title}")
        print(f"     Priority: {rec.priority}/10")
        print(f"     Confidence: {rec.confidence*100:.0f}%")
        print(f"     Expected improvement: {rec.expected_improvement}")

    # Compare agents
    print("\n⚖️  Agent Comparison:")
    # Only compare if both have data
    if "error" not in perf_code:
        print("  Code agent is performing well!")

    # Statistics
    stats = performance_optimizer.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  - Total executions: {stats['total_executions']}")
    print(f"  - Total recommendations: {stats['total_recommendations']}")
    print(f"  - High-priority recommendations: {stats['high_priority_recommendations']}")


async def demo_adaptive_strategy():
    """Demonstrate Adaptive Strategy System capabilities."""
    print("\n" + "="*60)
    print("4. ADAPTIVE STRATEGY - Dynamic Strategy Selection")
    print("="*60)

    # Analyze simple task
    print("\n🔍 Analyzing SIMPLE task...")
    task1 = adaptive_strategy.analyze_task(
        "Create a hello world function in Python"
    )
    print(f"  Task: {task1.description[:50]}...")
    print(f"  Complexity: {task1.complexity.name}")
    print(f"  Suggested agents: {task1.suggested_agents}")
    print(f"  Estimated duration: {task1.estimated_duration}s")

    strategy1 = adaptive_strategy.select_strategy(task1)
    print(f"\n  📋 Selected Strategy:")
    print(f"    - Type: {strategy1.execution_strategy.value}")
    print(f"    - Agent sequence: {strategy1.agent_sequence}")
    print(f"    - Confidence: {strategy1.confidence*100:.0f}%")
    print(f"    - Reasoning: {strategy1.reasoning}")

    # Analyze complex task
    print("\n🔍 Analyzing COMPLEX task...")
    task2 = adaptive_strategy.analyze_task(
        "Build REST API with authentication, database integration, comprehensive testing, and security review",
        context={"multiple_files": True, "dependencies": True}
    )
    print(f"  Task: {task2.description[:50]}...")
    print(f"  Complexity: {task2.complexity.name}")
    print(f"  Suggested agents: {task2.suggested_agents}")
    print(f"  Requirements:")
    print(f"    - Research: {task2.requires_research}")
    print(f"    - Testing: {task2.requires_testing}")
    print(f"    - Review: {task2.requires_review}")

    strategy2 = adaptive_strategy.select_strategy(task2)
    print(f"\n  📋 Selected Strategy:")
    print(f"    - Type: {strategy2.execution_strategy.value}")
    print(f"    - Agent sequence: {strategy2.agent_sequence}")
    print(f"    - Execution mode: {strategy2.execution_mode}")
    print(f"    - Confidence: {strategy2.confidence*100:.0f}%")

    # Record outcomes
    print("\n✅ Recording strategy outcomes...")
    adaptive_strategy.record_outcome(
        strategy_id=strategy1.strategy_id,
        task_id=task1.task_id,
        success=True,
        actual_duration=8.5,
        actual_iterations=1,
        errors_encountered=0,
        what_worked=["Single agent was efficient"],
        improvements=["None needed"]
    )
    print("  ✅ Outcome recorded for simple task")

    adaptive_strategy.record_outcome(
        strategy_id=strategy2.strategy_id,
        task_id=task2.task_id,
        success=True,
        actual_duration=120.0,
        actual_iterations=5,
        errors_encountered=2,
        what_worked=["Sequential execution with multiple agents"],
        improvements=["Could parallelize testing and review"]
    )
    print("  ✅ Outcome recorded for complex task")

    # Statistics
    stats = adaptive_strategy.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  - Tasks analyzed: {stats['total_tasks_analyzed']}")
    print(f"  - Strategies created: {stats['total_strategies_created']}")
    print(f"  - Patterns learned: {stats['learned_patterns']}")
    print(f"  - Overall success rate: {stats['overall_success_rate']*100:.1f}%")


async def demo_knowledge_base_evolution():
    """Demonstrate Knowledge Base Evolution capabilities."""
    print("\n" + "="*60)
    print("5. KNOWLEDGE BASE EVOLUTION - Persistent Knowledge Storage")
    print("="*60)

    # Add knowledge
    print("\n📝 Adding knowledge to base...")

    k1 = knowledge_base_evolution.add_knowledge(
        category="patterns",
        title="Test-Driven Development",
        content={
            "description": "Write tests before implementation",
            "benefits": ["Better code quality", "Faster debugging", "Documentation"],
            "steps": ["Write test", "Run test (fail)", "Implement", "Run test (pass)", "Refactor"]
        },
        tags=["testing", "best_practice", "tdd"],
        state=KnowledgeState.EXPERIMENTAL
    )
    print(f"  ✅ Added: {k1.title} (state: {k1.state.value})")

    k2 = knowledge_base_evolution.add_knowledge(
        category="best_practices",
        title="Code Review Checklist",
        content={
            "items": ["Security", "Performance", "Testing", "Documentation"],
            "priority": "high"
        },
        tags=["code_review", "quality"],
        state=KnowledgeState.EXPERIMENTAL
    )
    print(f"  ✅ Added: {k2.title} (state: {k2.state.value})")

    # Update knowledge
    print("\n🔄 Updating knowledge...")
    updated = knowledge_base_evolution.update_knowledge(
        knowledge_id=k2.knowledge_id,
        new_content={
            "items": ["Security", "Performance", "Testing", "Documentation", "Accessibility"],
            "priority": "high"
        },
        changes="Added accessibility to checklist"
    )
    print(f"  ✅ Updated: {updated.title} (version {updated.current_version})")

    # Record usage and evolution
    print("\n📈 Recording usage and triggering evolution...")
    for i in range(6):
        knowledge_base_evolution.record_usage(k1.knowledge_id, success=True)
    print(f"  ✅ Recorded 6 successful usages")

    # Check state evolution
    evolved_k1 = knowledge_base_evolution.knowledge_base[k1.knowledge_id]
    print(f"  📊 Knowledge evolved: {k1.state.value} → {evolved_k1.state.value}")
    success_rate = evolved_k1.success_count / (evolved_k1.success_count + evolved_k1.failure_count)
    print(f"  📈 Success rate: {success_rate*100:.0f}%")

    # Get validated knowledge
    print("\n✅ Retrieving validated knowledge...")
    validated = knowledge_base_evolution.get_validated_knowledge()
    print(f"  📚 Validated knowledge items: {len(validated)}")
    for k in validated:
        print(f"    - {k.title} ({k.usage_count} usages)")

    # Export knowledge base
    print("\n💾 Exporting knowledge base...")
    filepath = knowledge_base_evolution.export_to_file("demo_export.json")
    print(f"  ✅ Exported to: {filepath}")

    # Statistics
    stats = knowledge_base_evolution.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  - Total knowledge items: {stats['total_knowledge_items']}")
    print(f"  - Validated knowledge: {stats['validated_knowledge']}")
    print(f"  - Total usage: {stats['total_usage']}")
    print(f"  - Overall success rate: {stats['overall_success_rate']*100:.1f}%")


async def demo_full_integration():
    """Demonstrate all systems working together."""
    print("\n" + "="*60)
    print("6. FULL INTEGRATION - All Systems Working Together")
    print("="*60)

    print("\n🔄 Simulating complete task execution with all systems...")

    # 1. Analyze task
    print("\n1️⃣  Analyzing task...")
    task_chars = adaptive_strategy.analyze_task(
        "Create a REST API endpoint with unit tests"
    )
    print(f"   Complexity: {task_chars.complexity.name}")

    # 2. Select strategy
    print("\n2️⃣  Selecting optimal strategy...")
    strategy = adaptive_strategy.select_strategy(task_chars)
    print(f"   Strategy: {strategy.execution_strategy.value}")
    print(f"   Agents: {strategy.agent_sequence}")

    # 3. Query knowledge
    print("\n3️⃣  Querying knowledge hub...")
    knowledge = knowledge_hub.query_knowledge("REST API", limit=3)
    print(f"   Found {len(knowledge)} relevant knowledge items")

    # 4. Get learnings
    print("\n4️⃣  Retrieving relevant learnings...")
    learnings = learning_engine.get_relevant_learnings(
        "Create REST API endpoint",
        min_confidence=ConfidenceLevel.LOW
    )
    print(f"   Found {len(learnings)} relevant learnings")

    # 5. Execute (simulated)
    print("\n5️⃣  Executing task...")
    start_time = time.time()
    actions = [
        {"type": "CREATE_FILE", "path": "/workspace/api.py"},
        {"type": "CREATE_FILE", "path": "/workspace/test_api.py"},
        {"type": "EXECUTE", "command": "python -m pytest test_api.py"}
    ]
    results = [
        {"success": True},
        {"success": True},
        {"success": True, "stdout": "All tests passed"}
    ]
    duration = time.time() - start_time
    print(f"   ✅ Task completed in {duration:.1f}s")

    # 6. Record in all systems
    print("\n6️⃣  Recording in all learning systems...")

    # Learning Engine
    await learning_engine.record_interaction(
        agent_type="code",
        task_description=task_chars.description,
        actions_taken=actions,
        results=results,
        success=True,
        completion_time=duration,
        iterations=1,
        errors_encountered=0
    )
    print("   ✅ Recorded in Learning Engine")

    # Performance Optimizer
    performance_optimizer.record_execution(
        agent_type="code",
        task_category="api_development",
        completion_time=duration,
        iterations=1,
        success=True,
        errors=0,
        actions_count=len(actions)
    )
    print("   ✅ Recorded in Performance Optimizer")

    # Adaptive Strategy
    adaptive_strategy.record_outcome(
        strategy_id=strategy.strategy_id,
        task_id=task_chars.task_id,
        success=True,
        actual_duration=duration,
        actual_iterations=1,
        errors_encountered=0,
        what_worked=["Sequential execution with code and test agents"]
    )
    print("   ✅ Recorded in Adaptive Strategy")

    # 7. Share knowledge
    print("\n7️⃣  Sharing knowledge with other agents...")
    await knowledge_hub.share_solution(
        source_agent="code",
        problem="REST API endpoint with tests",
        solution="Use Flask with pytest for clean API development",
        context={"framework": "Flask", "testing": "pytest"}
    )
    print("   ✅ Shared in Knowledge Hub")

    # 8. Add to knowledge base
    print("\n8️⃣  Adding to knowledge base...")
    knowledge_base_evolution.add_knowledge(
        category="solutions",
        title="REST API Development Pattern",
        content={
            "framework": "Flask",
            "testing": "pytest",
            "pattern": "Route decorators + test fixtures"
        },
        tags=["api", "rest", "flask", "testing"]
    )
    print("   ✅ Added to Knowledge Base")

    print("\n✅ Complete learning cycle executed!")


async def main():
    """Run all demos."""
    print("\n" + "🌟"*30)
    print("   ADVANCED LEARNING SYSTEMS - Complete Demo")
    print("   Phase 4, Task 4.5")
    print("🌟"*30)

    # Run individual component demos
    await demo_learning_engine()
    await demo_knowledge_hub()
    await demo_performance_optimizer()
    await demo_adaptive_strategy()
    await demo_knowledge_base_evolution()

    # Run integration demo
    await demo_full_integration()

    # Final statistics
    print("\n" + "="*60)
    print("FINAL SYSTEM STATISTICS")
    print("="*60)

    systems = [
        ("Learning Engine", learning_engine),
        ("Knowledge Hub", knowledge_hub),
        ("Performance Optimizer", performance_optimizer),
        ("Adaptive Strategy", adaptive_strategy),
        ("Knowledge Base Evolution", knowledge_base_evolution)
    ]

    for name, system in systems:
        stats = system.get_statistics()
        print(f"\n{name}:")
        for key, value in list(stats.items())[:5]:  # Show first 5 stats
            print(f"  - {key}: {value}")

    print("\n" + "🌟"*30)
    print("   Demo Complete! All Systems Operational! 🚀")
    print("🌟"*30)


if __name__ == "__main__":
    asyncio.run(main())
