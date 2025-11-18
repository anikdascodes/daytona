"""
Adaptive Strategy System - Dynamic Strategy Selection and Optimization

Capabilities:
- Analyze task characteristics
- Select optimal agent combination
- Adapt execution patterns based on history
- Learn from outcomes
- Evolve strategies over time

Part of Phase 4: Task 4.5 - Advanced Learning Systems
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from utils.logger import logger


class ExecutionStrategy(Enum):
    """Types of execution strategies."""
    SINGLE_AGENT = "single_agent"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    CONSENSUS = "consensus"
    HYBRID = "hybrid"


class TaskComplexity(Enum):
    """Task complexity levels."""
    TRIVIAL = 1
    SIMPLE = 2
    MODERATE = 3
    COMPLEX = 4
    VERY_COMPLEX = 5


@dataclass
class TaskCharacteristics:
    """Characteristics of a task."""
    task_id: str
    description: str

    # Detected characteristics
    complexity: TaskComplexity
    keywords: List[str]
    estimated_duration: float  # seconds
    requires_research: bool
    requires_testing: bool
    requires_debugging: bool
    requires_review: bool

    # Resource requirements
    suggested_agents: List[str]
    agent_count: int

    # Context
    similar_tasks_count: int
    previous_success_rate: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "complexity": self.complexity.value,
            "keywords": self.keywords,
            "estimated_duration": self.estimated_duration,
            "requires_research": self.requires_research,
            "requires_testing": self.requires_testing,
            "requires_debugging": self.requires_debugging,
            "requires_review": self.requires_review,
            "suggested_agents": self.suggested_agents,
            "agent_count": self.agent_count,
            "similar_tasks_count": self.similar_tasks_count,
            "previous_success_rate": self.previous_success_rate
        }


@dataclass
class StrategyPlan:
    """Represents an adaptive execution strategy."""
    strategy_id: str
    task_id: str

    # Strategy details
    execution_strategy: ExecutionStrategy
    agent_sequence: List[str]
    execution_mode: str  # "sequential", "parallel", etc.

    # Reasoning
    reasoning: str
    confidence: float  # 0.0-1.0

    # Expected outcomes
    estimated_duration: float
    estimated_success_rate: float

    # Evidence
    based_on_history: bool
    historical_successes: int
    similar_task_count: int

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "strategy_id": self.strategy_id,
            "task_id": self.task_id,
            "execution_strategy": self.execution_strategy.value,
            "agent_sequence": self.agent_sequence,
            "execution_mode": self.execution_mode,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "estimated_duration": self.estimated_duration,
            "estimated_success_rate": self.estimated_success_rate,
            "based_on_history": self.based_on_history,
            "historical_successes": self.historical_successes,
            "similar_task_count": self.similar_task_count,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class StrategyOutcome:
    """Outcome of executing a strategy."""
    strategy_id: str
    task_id: str

    # Results
    success: bool
    actual_duration: float
    actual_iterations: int
    errors_encountered: int

    # Deviation from plan
    duration_deviation: float  # Percentage
    accuracy: float  # How close to estimated success rate

    # Learnings
    what_worked: List[str]
    what_failed: List[str]
    improvements: List[str]

    timestamp: datetime = field(default_factory=datetime.now)


class AdaptiveStrategySystem:
    """
    Adaptive Strategy System that learns optimal strategies over time.

    Capabilities:
    - Analyze task characteristics
    - Select optimal execution strategy
    - Adapt based on historical performance
    - Learn from outcomes
    - Evolve strategies continuously
    """

    def __init__(self):
        """Initialize adaptive strategy system."""
        self.task_characteristics_cache: Dict[str, TaskCharacteristics] = {}
        self.strategy_plans: Dict[str, StrategyPlan] = {}
        self.strategy_outcomes: List[StrategyOutcome] = []

        # Strategy performance tracking
        # pattern_key -> {success_count, total_count, avg_duration}
        self.strategy_performance: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "success_count": 0,
            "total_count": 0,
            "total_duration": 0.0,
            "avg_duration": 0.0,
            "success_rate": 0.0
        })

        # Task pattern matching
        # task_pattern -> optimal_strategy
        self.learned_patterns: Dict[str, Dict[str, Any]] = {}

        # Counters
        self.task_counter = 0
        self.strategy_counter = 0

        logger.info("🎯 AdaptiveStrategySystem initialized")

    def analyze_task(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> TaskCharacteristics:
        """
        Analyze task and determine its characteristics.

        Args:
            task_description: Description of the task
            context: Additional context

        Returns:
            TaskCharacteristics
        """
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Extract keywords
        keywords = self._extract_keywords(task_description)

        # Determine complexity
        complexity = self._determine_complexity(task_description, keywords, context)

        # Determine requirements
        requires_research = self._requires_research(keywords, task_description)
        requires_testing = self._requires_testing(keywords, task_description)
        requires_debugging = self._requires_debugging(keywords, task_description)
        requires_review = self._requires_review(keywords, task_description)

        # Suggest agents
        suggested_agents = self._suggest_agents(
            keywords,
            requires_research,
            requires_testing,
            requires_debugging,
            requires_review
        )

        # Find similar tasks
        similar_tasks = self._find_similar_tasks(keywords)
        similar_count = len(similar_tasks)

        # Calculate previous success rate
        previous_success_rate = self._calculate_success_rate(similar_tasks)

        # Estimate duration
        estimated_duration = self._estimate_duration(complexity, similar_tasks)

        characteristics = TaskCharacteristics(
            task_id=task_id,
            description=task_description,
            complexity=complexity,
            keywords=keywords,
            estimated_duration=estimated_duration,
            requires_research=requires_research,
            requires_testing=requires_testing,
            requires_debugging=requires_debugging,
            requires_review=requires_review,
            suggested_agents=suggested_agents,
            agent_count=len(suggested_agents),
            similar_tasks_count=similar_count,
            previous_success_rate=previous_success_rate
        )

        self.task_characteristics_cache[task_id] = characteristics

        logger.info(f"🔍 Analyzed task: complexity={complexity.name}, agents={len(suggested_agents)}, similar={similar_count}")

        return characteristics

    def select_strategy(
        self,
        task_characteristics: TaskCharacteristics
    ) -> StrategyPlan:
        """
        Select optimal execution strategy based on task characteristics.

        Args:
            task_characteristics: Analyzed task characteristics

        Returns:
            StrategyPlan
        """
        self.strategy_counter += 1
        strategy_id = f"strategy_{self.strategy_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Check if we have learned patterns for this type of task
        pattern_key = self._get_pattern_key(task_characteristics.keywords)
        learned_strategy = self.learned_patterns.get(pattern_key)

        if learned_strategy and learned_strategy["success_rate"] > 0.7:
            # Use learned strategy
            execution_strategy = ExecutionStrategy(learned_strategy["execution_strategy"])
            agent_sequence = learned_strategy["agent_sequence"]
            execution_mode = learned_strategy["execution_mode"]
            confidence = learned_strategy["success_rate"]
            reasoning = f"Based on {learned_strategy['usage_count']} successful similar tasks"
            based_on_history = True
            historical_successes = learned_strategy["success_count"]
        else:
            # Derive strategy from characteristics
            execution_strategy, agent_sequence, execution_mode, reasoning = self._derive_strategy(
                task_characteristics
            )
            confidence = 0.6  # Lower confidence for new strategies
            based_on_history = False
            historical_successes = 0

        # Create strategy plan
        strategy_plan = StrategyPlan(
            strategy_id=strategy_id,
            task_id=task_characteristics.task_id,
            execution_strategy=execution_strategy,
            agent_sequence=agent_sequence,
            execution_mode=execution_mode,
            reasoning=reasoning,
            confidence=confidence,
            estimated_duration=task_characteristics.estimated_duration,
            estimated_success_rate=task_characteristics.previous_success_rate if based_on_history else 0.7,
            based_on_history=based_on_history,
            historical_successes=historical_successes,
            similar_task_count=task_characteristics.similar_tasks_count
        )

        self.strategy_plans[strategy_id] = strategy_plan

        logger.info(f"🎯 Selected strategy: {execution_strategy.value} with {len(agent_sequence)} agents (confidence: {confidence*100:.0f}%)")

        return strategy_plan

    def record_outcome(
        self,
        strategy_id: str,
        task_id: str,
        success: bool,
        actual_duration: float,
        actual_iterations: int,
        errors_encountered: int,
        what_worked: Optional[List[str]] = None,
        what_failed: Optional[List[str]] = None,
        improvements: Optional[List[str]] = None
    ):
        """
        Record the outcome of a strategy execution.

        This enables learning and strategy evolution.
        """
        strategy_plan = self.strategy_plans.get(strategy_id)
        if not strategy_plan:
            logger.warning(f"Strategy {strategy_id} not found")
            return

        # Calculate deviations
        duration_deviation = ((actual_duration - strategy_plan.estimated_duration) /
                             strategy_plan.estimated_duration * 100) if strategy_plan.estimated_duration > 0 else 0

        # Accuracy: how close actual outcome was to prediction
        actual_success_value = 1.0 if success else 0.0
        accuracy = 1.0 - abs(actual_success_value - strategy_plan.estimated_success_rate)

        outcome = StrategyOutcome(
            strategy_id=strategy_id,
            task_id=task_id,
            success=success,
            actual_duration=actual_duration,
            actual_iterations=actual_iterations,
            errors_encountered=errors_encountered,
            duration_deviation=duration_deviation,
            accuracy=accuracy,
            what_worked=what_worked or [],
            what_failed=what_failed or [],
            improvements=improvements or []
        )

        self.strategy_outcomes.append(outcome)

        # Update strategy performance
        pattern_key = f"{strategy_plan.execution_strategy.value}_{len(strategy_plan.agent_sequence)}"
        perf = self.strategy_performance[pattern_key]
        perf["total_count"] += 1
        perf["total_duration"] += actual_duration
        if success:
            perf["success_count"] += 1
        perf["avg_duration"] = perf["total_duration"] / perf["total_count"]
        perf["success_rate"] = perf["success_count"] / perf["total_count"]

        # Learn from this execution
        self._update_learned_patterns(strategy_plan, outcome)

        logger.info(f"📝 Recorded outcome: {strategy_id} ({'✅ success' if success else '❌ failed'}, {actual_duration:.1f}s)")

    def _update_learned_patterns(self, strategy: StrategyPlan, outcome: StrategyOutcome):
        """Update learned patterns based on outcome."""
        task_chars = self.task_characteristics_cache.get(strategy.task_id)
        if not task_chars:
            return

        pattern_key = self._get_pattern_key(task_chars.keywords)

        if pattern_key not in self.learned_patterns:
            # Create new learned pattern
            self.learned_patterns[pattern_key] = {
                "execution_strategy": strategy.execution_strategy.value,
                "agent_sequence": strategy.agent_sequence,
                "execution_mode": strategy.execution_mode,
                "success_count": 1 if outcome.success else 0,
                "total_count": 1,
                "success_rate": 1.0 if outcome.success else 0.0,
                "avg_duration": outcome.actual_duration,
                "usage_count": 1,
                "last_used": datetime.now()
            }
        else:
            # Update existing pattern
            pattern = self.learned_patterns[pattern_key]
            pattern["total_count"] += 1
            if outcome.success:
                pattern["success_count"] += 1
            pattern["success_rate"] = pattern["success_count"] / pattern["total_count"]
            pattern["avg_duration"] = (pattern["avg_duration"] * (pattern["usage_count"] - 1) + outcome.actual_duration) / pattern["usage_count"]
            pattern["usage_count"] += 1
            pattern["last_used"] = datetime.now()

            # If this strategy is performing better, update it
            if outcome.success and outcome.actual_duration < pattern["avg_duration"]:
                pattern["execution_strategy"] = strategy.execution_strategy.value
                pattern["agent_sequence"] = strategy.agent_sequence
                pattern["execution_mode"] = strategy.execution_mode

        logger.info(f"📚 Updated learned pattern: {pattern_key} (success rate: {self.learned_patterns[pattern_key]['success_rate']*100:.0f}%)")

    def _derive_strategy(
        self,
        task_chars: TaskCharacteristics
    ) -> Tuple[ExecutionStrategy, List[str], str, str]:
        """
        Derive optimal strategy from task characteristics.

        Returns:
            (execution_strategy, agent_sequence, execution_mode, reasoning)
        """
        agents = task_chars.suggested_agents
        complexity = task_chars.complexity

        # Simple task - single agent
        if complexity in [TaskComplexity.TRIVIAL, TaskComplexity.SIMPLE] and len(agents) == 1:
            return (
                ExecutionStrategy.SINGLE_AGENT,
                agents,
                "single",
                "Simple task can be handled by single agent"
            )

        # Complex task requiring multiple agents
        if complexity >= TaskComplexity.COMPLEX and len(agents) > 2:
            # Use hierarchical if we have many agents
            if len(agents) >= 4:
                return (
                    ExecutionStrategy.HIERARCHICAL,
                    agents,
                    "hierarchical",
                    f"Complex task with {len(agents)} agents benefits from hierarchical coordination"
                )
            else:
                return (
                    ExecutionStrategy.SEQUENTIAL,
                    agents,
                    "sequential",
                    f"Complex task requiring {len(agents)} specialized agents in sequence"
                )

        # Moderate complexity
        if len(agents) == 2:
            return (
                ExecutionStrategy.SEQUENTIAL,
                agents,
                "sequential",
                "Two-agent collaboration in sequence"
            )

        # Multiple independent tasks - parallel
        if "and" in task_chars.description.lower() and len(agents) > 1:
            return (
                ExecutionStrategy.PARALLEL,
                agents,
                "parallel",
                "Multiple independent subtasks can run in parallel"
            )

        # Default to sequential
        return (
            ExecutionStrategy.SEQUENTIAL,
            agents,
            "sequential",
            "Default sequential execution for moderate complexity"
        )

    def _determine_complexity(
        self,
        description: str,
        keywords: List[str],
        context: Optional[Dict[str, Any]]
    ) -> TaskComplexity:
        """Determine task complexity."""
        complexity_score = 0

        # Length of description
        if len(description) > 200:
            complexity_score += 2
        elif len(description) > 100:
            complexity_score += 1

        # Number of requirements
        requirement_words = ["and", "also", "then", "after", "before", "must"]
        for word in requirement_words:
            if word in description.lower():
                complexity_score += 1

        # Multiple keywords indicate complexity
        complexity_score += min(len(keywords), 5)

        # Context indicators
        if context:
            if context.get("multiple_files"):
                complexity_score += 2
            if context.get("dependencies"):
                complexity_score += 2

        # Map score to complexity level
        if complexity_score <= 2:
            return TaskComplexity.TRIVIAL
        elif complexity_score <= 4:
            return TaskComplexity.SIMPLE
        elif complexity_score <= 7:
            return TaskComplexity.MODERATE
        elif complexity_score <= 10:
            return TaskComplexity.COMPLEX
        else:
            return TaskComplexity.VERY_COMPLEX

    def _extract_keywords(self, description: str) -> List[str]:
        """Extract keywords from task description."""
        keywords = []

        action_words = [
            "create", "build", "implement", "write", "code", "develop",
            "test", "verify", "check", "validate",
            "debug", "fix", "resolve", "troubleshoot",
            "review", "analyze", "inspect", "audit",
            "refactor", "optimize", "improve", "enhance",
            "deploy", "release", "publish",
            "research", "search", "find", "lookup"
        ]

        tech_words = [
            "python", "javascript", "typescript", "java", "go", "rust",
            "api", "rest", "graphql",
            "database", "sql", "mongodb",
            "frontend", "backend", "web", "mobile",
            "test", "unit", "integration"
        ]

        description_lower = description.lower()

        for word in action_words + tech_words:
            if word in description_lower:
                keywords.append(word)

        return list(set(keywords))  # Remove duplicates

    def _requires_research(self, keywords: List[str], description: str) -> bool:
        """Check if task requires research."""
        research_indicators = ["search", "find", "lookup", "research", "investigate", "web"]
        return any(word in keywords or word in description.lower() for word in research_indicators)

    def _requires_testing(self, keywords: List[str], description: str) -> bool:
        """Check if task requires testing."""
        test_indicators = ["test", "verify", "check", "validate", "coverage"]
        return any(word in keywords or word in description.lower() for word in test_indicators)

    def _requires_debugging(self, keywords: List[str], description: str) -> bool:
        """Check if task requires debugging."""
        debug_indicators = ["debug", "fix", "error", "bug", "issue", "troubleshoot"]
        return any(word in keywords or word in description.lower() for word in debug_indicators)

    def _requires_review(self, keywords: List[str], description: str) -> bool:
        """Check if task requires code review."""
        review_indicators = ["review", "analyze", "inspect", "audit", "security", "performance"]
        return any(word in keywords or word in description.lower() for word in review_indicators)

    def _suggest_agents(
        self,
        keywords: List[str],
        requires_research: bool,
        requires_testing: bool,
        requires_debugging: bool,
        requires_review: bool
    ) -> List[str]:
        """Suggest agents based on requirements."""
        agents = []

        # Core agent for implementation
        if any(word in keywords for word in ["create", "build", "implement", "write", "code", "develop"]):
            agents.append("code")

        # Research agent
        if requires_research:
            agents.append("knowledge")

        # Test agent
        if requires_testing:
            agents.append("test")

        # Debug agent
        if requires_debugging:
            agents.append("debug")

        # Review agent
        if requires_review:
            agents.append("review")

        # Default to code agent if nothing else
        if not agents:
            agents.append("code")

        return agents

    def _find_similar_tasks(self, keywords: List[str]) -> List[StrategyOutcome]:
        """Find similar tasks from history."""
        similar = []

        for outcome in self.strategy_outcomes:
            task_chars = self.task_characteristics_cache.get(outcome.task_id)
            if not task_chars:
                continue

            # Check keyword overlap
            overlap = set(keywords).intersection(set(task_chars.keywords))
            if len(overlap) >= 2:  # At least 2 matching keywords
                similar.append(outcome)

        return similar

    def _calculate_success_rate(self, similar_tasks: List[StrategyOutcome]) -> float:
        """Calculate success rate from similar tasks."""
        if not similar_tasks:
            return 0.7  # Default estimate

        successes = sum(1 for task in similar_tasks if task.success)
        return successes / len(similar_tasks)

    def _estimate_duration(self, complexity: TaskComplexity, similar_tasks: List[StrategyOutcome]) -> float:
        """Estimate task duration."""
        if similar_tasks:
            # Use average from similar tasks
            total_duration = sum(task.actual_duration for task in similar_tasks)
            return total_duration / len(similar_tasks)

        # Estimate based on complexity
        complexity_durations = {
            TaskComplexity.TRIVIAL: 10.0,
            TaskComplexity.SIMPLE: 30.0,
            TaskComplexity.MODERATE: 60.0,
            TaskComplexity.COMPLEX: 120.0,
            TaskComplexity.VERY_COMPLEX: 300.0
        }

        return complexity_durations.get(complexity, 60.0)

    def _get_pattern_key(self, keywords: List[str]) -> str:
        """Generate pattern key from keywords."""
        # Sort keywords to ensure consistent keys
        sorted_keywords = sorted(keywords)
        return "_".join(sorted_keywords[:3])  # Use top 3 keywords

    def get_statistics(self) -> Dict[str, Any]:
        """Get adaptive strategy statistics."""
        return {
            "total_tasks_analyzed": len(self.task_characteristics_cache),
            "total_strategies_created": len(self.strategy_plans),
            "total_outcomes_recorded": len(self.strategy_outcomes),
            "learned_patterns": len(self.learned_patterns),
            "strategy_performance": dict(self.strategy_performance),
            "overall_success_rate": (
                sum(1 for o in self.strategy_outcomes if o.success) / len(self.strategy_outcomes)
                if self.strategy_outcomes else 0
            ),
            "avg_accuracy": (
                sum(o.accuracy for o in self.strategy_outcomes) / len(self.strategy_outcomes)
                if self.strategy_outcomes else 0
            )
        }


# Global singleton instance
adaptive_strategy = AdaptiveStrategySystem()
