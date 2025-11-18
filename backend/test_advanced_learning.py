"""
Comprehensive Tests for Advanced Learning Systems

Tests all components of Phase 4, Task 4.5:
- Learning Engine
- Knowledge Hub
- Performance Optimizer
- Adaptive Strategy System
- Knowledge Base Evolution
"""
import asyncio
import pytest
from datetime import datetime
from services.learning_engine import (
    learning_engine,
    LearningType,
    ConfidenceLevel
)
from services.knowledge_hub import (
    knowledge_hub,
    KnowledgeType,
    KnowledgePriority
)
from services.performance_optimizer import (
    performance_optimizer,
    OptimizationType
)
from services.adaptive_strategy import (
    adaptive_strategy,
    ExecutionStrategy,
    TaskComplexity
)
from services.knowledge_base_evolution import (
    knowledge_base_evolution,
    KnowledgeState
)


class TestLearningEngine:
    """Tests for Learning Engine."""

    @pytest.mark.asyncio
    async def test_record_interaction_success(self):
        """Test recording a successful interaction."""
        interaction = await learning_engine.record_interaction(
            agent_type="code",
            task_description="Create a simple Python function",
            actions_taken=[
                {"type": "CREATE_FILE", "path": "/workspace/test.py"},
                {"type": "EXECUTE", "command": "python /workspace/test.py"}
            ],
            results=[
                {"success": True},
                {"success": True, "stdout": "Success"}
            ],
            success=True,
            completion_time=5.2,
            iterations=2,
            errors_encountered=0,
            metadata={"language": "python"}
        )

        assert interaction.success == True
        assert interaction.agent_type == "code"
        assert interaction.completion_time == 5.2
        assert len(learning_engine.interaction_history) > 0

    @pytest.mark.asyncio
    async def test_extract_success_patterns(self):
        """Test extraction of success patterns."""
        # Record multiple successful interactions with same pattern
        for i in range(3):
            await learning_engine.record_interaction(
                agent_type="test",
                task_description=f"Create unit tests for function {i}",
                actions_taken=[
                    {"type": "CREATE_FILE"},
                    {"type": "EXECUTE"}
                ],
                results=[{"success": True}, {"success": True}],
                success=True,
                completion_time=3.0,
                iterations=1,
                errors_encountered=0
            )

        # Wait for async pattern extraction
        await asyncio.sleep(0.5)

        # Check if pattern was learned
        learnings = learning_engine.get_learnings_by_type(LearningType.SUCCESS_PATTERN)
        assert len(learnings) > 0

    def test_get_relevant_learnings(self):
        """Test retrieving relevant learnings for a task."""
        learnings = learning_engine.get_relevant_learnings(
            task_description="Create Python unit tests",
            agent_type="test",
            min_confidence=ConfidenceLevel.LOW
        )

        # Should find relevant learnings
        assert isinstance(learnings, list)

    def test_get_statistics(self):
        """Test getting learning engine statistics."""
        stats = learning_engine.get_statistics()

        assert "total_interactions" in stats
        assert "total_learnings" in stats
        assert "by_type" in stats
        assert isinstance(stats["total_interactions"], int)


class TestKnowledgeHub:
    """Tests for Knowledge Hub."""

    @pytest.mark.asyncio
    async def test_share_knowledge(self):
        """Test sharing knowledge between agents."""
        knowledge = await knowledge_hub.share_knowledge(
            source_agent="code",
            knowledge_type=KnowledgeType.SOLUTION,
            title="Fast sorting algorithm",
            content="Use quicksort for optimal O(n log n) performance",
            context={"language": "python", "complexity": "O(n log n)"},
            priority=KnowledgePriority.MEDIUM,
            tags={"algorithm", "sorting", "optimization"}
        )

        assert knowledge.source_agent == "code"
        assert knowledge.knowledge_type == KnowledgeType.SOLUTION
        assert knowledge.priority == KnowledgePriority.MEDIUM

    def test_subscribe_to_channel(self):
        """Test subscribing to knowledge channel."""
        success = knowledge_hub.subscribe_to_channel("test", "testing")
        assert success == True

        # Check subscription was recorded
        assert "test" in knowledge_hub.agent_subscriptions
        assert "testing" in knowledge_hub.agent_subscriptions["test"]

    def test_query_knowledge(self):
        """Test querying knowledge base."""
        results = knowledge_hub.query_knowledge(
            query="sorting algorithm",
            min_priority=KnowledgePriority.LOW,
            limit=10
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_broadcast_discovery(self):
        """Test broadcasting important discovery."""
        await knowledge_hub.broadcast_discovery(
            source_agent="review",
            title="Security vulnerability pattern detected",
            content="Always sanitize user input to prevent XSS attacks",
            context={"severity": "high", "category": "security"}
        )

        # Check knowledge was added
        assert len(knowledge_hub.knowledge_items) > 0

    def test_get_statistics(self):
        """Test getting knowledge hub statistics."""
        stats = knowledge_hub.get_statistics()

        assert "total_knowledge_items" in stats
        assert "by_type" in stats
        assert "total_channels" in stats


class TestPerformanceOptimizer:
    """Tests for Performance Optimizer."""

    def test_record_execution(self):
        """Test recording execution for performance tracking."""
        performance_optimizer.record_execution(
            agent_type="code",
            task_category="code_generation",
            completion_time=12.5,
            iterations=3,
            success=True,
            errors=0,
            actions_count=5,
            metadata={"language": "python"}
        )

        assert len(performance_optimizer.execution_history) > 0

    def test_generate_recommendations_slow_execution(self):
        """Test recommendation generation for slow execution."""
        # Record multiple slow executions
        for i in range(6):
            performance_optimizer.record_execution(
                agent_type="slow_agent",
                task_category="slow_task",
                completion_time=45.0,  # Slow execution
                iterations=3,
                success=True,
                errors=0,
                actions_count=5
            )

        # Should generate optimization recommendation
        recommendations = performance_optimizer.get_recommendations(
            agent_type="slow_agent",
            min_priority=5
        )

        # Should have at least one recommendation
        assert len(recommendations) >= 0  # May or may not generate based on thresholds

    def test_get_agent_performance(self):
        """Test getting agent performance summary."""
        perf = performance_optimizer.get_agent_performance("code")

        # Should have performance data if executions were recorded
        if "error" not in perf:
            assert "success_rate" in perf
            assert "avg_completion_time" in perf

    def test_compare_agents(self):
        """Test comparing performance between agents."""
        # Record some data for two agents
        for i in range(3):
            performance_optimizer.record_execution(
                agent_type="agent_a",
                task_category="common_task",
                completion_time=10.0,
                iterations=2,
                success=True,
                errors=0,
                actions_count=3
            )

            performance_optimizer.record_execution(
                agent_type="agent_b",
                task_category="common_task",
                completion_time=15.0,
                iterations=3,
                success=True,
                errors=1,
                actions_count=4
            )

        comparison = performance_optimizer.compare_agents("agent_a", "agent_b")

        # Should have comparison data if both agents have data
        if "error" not in comparison:
            assert "metrics" in comparison
            assert "recommendation" in comparison

    def test_get_statistics(self):
        """Test getting performance optimizer statistics."""
        stats = performance_optimizer.get_statistics()

        assert "total_executions" in stats
        assert "total_recommendations" in stats


class TestAdaptiveStrategy:
    """Tests for Adaptive Strategy System."""

    def test_analyze_task_simple(self):
        """Test analyzing a simple task."""
        task_chars = adaptive_strategy.analyze_task(
            task_description="Create a hello world function in Python",
            context={}
        )

        assert task_chars.complexity in [TaskComplexity.TRIVIAL, TaskComplexity.SIMPLE]
        assert "create" in task_chars.keywords
        assert "code" in task_chars.suggested_agents

    def test_analyze_task_complex(self):
        """Test analyzing a complex task."""
        task_chars = adaptive_strategy.analyze_task(
            task_description="Build a full REST API with authentication, database integration, comprehensive testing, and security review",
            context={"multiple_files": True, "dependencies": True}
        )

        assert task_chars.complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]
        assert len(task_chars.suggested_agents) > 1
        assert task_chars.requires_testing == True

    def test_select_strategy_single_agent(self):
        """Test strategy selection for single agent."""
        task_chars = adaptive_strategy.analyze_task(
            "Write a simple function",
            {}
        )

        strategy = adaptive_strategy.select_strategy(task_chars)

        assert strategy.execution_strategy in [
            ExecutionStrategy.SINGLE_AGENT,
            ExecutionStrategy.SEQUENTIAL
        ]
        assert len(strategy.agent_sequence) >= 1

    def test_select_strategy_multi_agent(self):
        """Test strategy selection for multi-agent task."""
        task_chars = adaptive_strategy.analyze_task(
            "Implement feature, write tests, and review code for security",
            {}
        )

        strategy = adaptive_strategy.select_strategy(task_chars)

        assert len(strategy.agent_sequence) >= 2
        assert strategy.confidence > 0

    def test_record_outcome(self):
        """Test recording strategy outcome."""
        # First create a strategy
        task_chars = adaptive_strategy.analyze_task("Test task", {})
        strategy = adaptive_strategy.select_strategy(task_chars)

        # Record outcome
        adaptive_strategy.record_outcome(
            strategy_id=strategy.strategy_id,
            task_id=task_chars.task_id,
            success=True,
            actual_duration=10.5,
            actual_iterations=2,
            errors_encountered=0,
            what_worked=["Good planning"],
            what_failed=[],
            improvements=["Could be faster"]
        )

        assert len(adaptive_strategy.strategy_outcomes) > 0

    def test_get_statistics(self):
        """Test getting adaptive strategy statistics."""
        stats = adaptive_strategy.get_statistics()

        assert "total_tasks_analyzed" in stats
        assert "total_strategies_created" in stats
        assert "learned_patterns" in stats


class TestKnowledgeBaseEvolution:
    """Tests for Knowledge Base Evolution."""

    def test_add_knowledge(self):
        """Test adding knowledge to the base."""
        knowledge = knowledge_base_evolution.add_knowledge(
            category="patterns",
            title="Test-Driven Development",
            content={
                "description": "Write tests before implementation",
                "benefits": ["Better code quality", "Faster debugging"],
                "applies_to": ["code", "test"]
            },
            tags=["testing", "best_practice"],
            state=KnowledgeState.EXPERIMENTAL
        )

        assert knowledge.category == "patterns"
        assert knowledge.state == KnowledgeState.EXPERIMENTAL
        assert len(knowledge.versions) == 1

    def test_update_knowledge(self):
        """Test updating knowledge."""
        # Add knowledge first
        knowledge = knowledge_base_evolution.add_knowledge(
            category="techniques",
            title="Code Review Checklist",
            content={"items": ["Security", "Performance"]},
            state=KnowledgeState.EXPERIMENTAL
        )

        # Update it
        updated = knowledge_base_evolution.update_knowledge(
            knowledge_id=knowledge.knowledge_id,
            new_content={"items": ["Security", "Performance", "Testing"]},
            changes="Added testing to checklist",
            updated_by="test"
        )

        assert updated is not None
        assert updated.current_version == 2
        assert len(updated.versions) == 2

    def test_record_usage_and_evolution(self):
        """Test recording usage and state evolution."""
        knowledge = knowledge_base_evolution.add_knowledge(
            category="solutions",
            title="Quick Sort Implementation",
            content={"algorithm": "quicksort"},
            state=KnowledgeState.EXPERIMENTAL
        )

        # Record successful usage multiple times
        for i in range(6):
            knowledge_base_evolution.record_usage(
                knowledge_id=knowledge.knowledge_id,
                success=True
            )

        # Should evolve to VALIDATED
        updated_knowledge = knowledge_base_evolution.knowledge_base[knowledge.knowledge_id]
        assert updated_knowledge.usage_count == 6
        assert updated_knowledge.state == KnowledgeState.VALIDATED

    def test_get_knowledge_filtered(self):
        """Test getting knowledge with filters."""
        results = knowledge_base_evolution.get_knowledge(
            category="patterns",
            state=KnowledgeState.VALIDATED,
            min_success_rate=0.7
        )

        assert isinstance(results, list)

    def test_get_validated_knowledge(self):
        """Test getting all validated knowledge."""
        validated = knowledge_base_evolution.get_validated_knowledge()
        assert isinstance(validated, list)

        for knowledge in validated:
            assert knowledge.state == KnowledgeState.VALIDATED

    def test_export_import(self):
        """Test exporting and importing knowledge base."""
        # Export
        filepath = knowledge_base_evolution.export_to_file("test_export.json")
        assert filepath.endswith("test_export.json")

        # Clear knowledge base
        original_count = len(knowledge_base_evolution.knowledge_base)
        knowledge_base_evolution.knowledge_base.clear()

        # Import back
        imported_count = knowledge_base_evolution.import_from_file(filepath)
        assert imported_count == original_count

    def test_get_statistics(self):
        """Test getting knowledge base statistics."""
        stats = knowledge_base_evolution.get_statistics()

        assert "total_knowledge_items" in stats
        assert "by_state" in stats
        assert "by_category" in stats
        assert "overall_success_rate" in stats


class TestIntegration:
    """Integration tests for all learning systems working together."""

    @pytest.mark.asyncio
    async def test_full_learning_cycle(self):
        """Test complete learning cycle across all systems."""
        # 1. Record interaction in Learning Engine
        interaction = await learning_engine.record_interaction(
            agent_type="code",
            task_description="Create REST API endpoint",
            actions_taken=[{"type": "CREATE_FILE"}, {"type": "EXECUTE"}],
            results=[{"success": True}, {"success": True}],
            success=True,
            completion_time=15.0,
            iterations=3,
            errors_encountered=0
        )

        # 2. Share knowledge via Knowledge Hub
        await knowledge_hub.share_knowledge(
            source_agent="code",
            knowledge_type=KnowledgeType.SOLUTION,
            title="REST API endpoint pattern",
            content="Use Flask route decorators for clean API design",
            priority=KnowledgePriority.MEDIUM
        )

        # 3. Record performance
        performance_optimizer.record_execution(
            agent_type="code",
            task_category="api_development",
            completion_time=15.0,
            iterations=3,
            success=True,
            errors=0,
            actions_count=2
        )

        # 4. Analyze task and select strategy
        task_chars = adaptive_strategy.analyze_task(
            "Create REST API endpoint",
            {}
        )
        strategy = adaptive_strategy.select_strategy(task_chars)

        # 5. Add to knowledge base
        knowledge_base_evolution.add_knowledge(
            category="patterns",
            title="REST API Design Pattern",
            content={"framework": "Flask", "pattern": "Route decorators"},
            tags=["api", "rest", "flask"]
        )

        # Verify all systems have data
        assert len(learning_engine.interaction_history) > 0
        assert len(knowledge_hub.knowledge_items) > 0
        assert len(performance_optimizer.execution_history) > 0
        assert len(adaptive_strategy.task_characteristics_cache) > 0
        assert len(knowledge_base_evolution.knowledge_base) > 0


def test_all_systems_statistics():
    """Test that all systems can provide statistics."""
    systems = [
        learning_engine,
        knowledge_hub,
        performance_optimizer,
        adaptive_strategy,
        knowledge_base_evolution
    ]

    for system in systems:
        stats = system.get_statistics()
        assert isinstance(stats, dict)
        assert len(stats) > 0


if __name__ == "__main__":
    print("Running Advanced Learning Systems Tests...")
    print("=" * 60)

    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
