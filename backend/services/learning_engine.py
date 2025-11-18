"""
Learning Engine - Advanced Learning System for Daytona AI

Capabilities:
- Continuous learning from all agent interactions
- Pattern recognition and analysis
- Knowledge extraction and storage
- Learning from successes and failures
- Adaptive improvement based on history

Part of Phase 4: Task 4.5 - Advanced Learning Systems
"""
import json
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
from utils.logger import logger


class LearningType(Enum):
    """Types of learning."""
    SUCCESS_PATTERN = "success_pattern"       # Successful approach
    FAILURE_PATTERN = "failure_pattern"       # Common mistake
    OPTIMIZATION = "optimization"             # Performance improvement
    BEST_PRACTICE = "best_practice"          # Proven technique
    ERROR_RECOVERY = "error_recovery"        # How to recover from errors
    TASK_STRATEGY = "task_strategy"          # Task-specific strategy
    AGENT_CAPABILITY = "agent_capability"    # Agent capability evolution


class ConfidenceLevel(Enum):
    """Confidence levels for learnings."""
    LOW = 1          # 1-2 occurrences
    MEDIUM = 2       # 3-5 occurrences
    HIGH = 3         # 6-10 occurrences
    VERY_HIGH = 4    # 11+ occurrences


@dataclass
class Learning:
    """Represents a single learning."""
    learning_id: str
    learning_type: LearningType
    title: str
    description: str
    context: Dict[str, Any]

    # Evidence
    occurrences: int = 1
    success_rate: float = 0.0
    confidence: ConfidenceLevel = ConfidenceLevel.LOW

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)

    # Tags for searchability
    tags: Set[str] = field(default_factory=set)
    related_agents: Set[str] = field(default_factory=set)

    # Evidence trail
    evidence: List[Dict[str, Any]] = field(default_factory=list)

    # Applicability
    applicable_to: List[str] = field(default_factory=list)  # Task types

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['learning_type'] = self.learning_type.value
        data['confidence'] = self.confidence.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['last_seen'] = self.last_seen.isoformat()
        data['tags'] = list(self.tags)
        data['related_agents'] = list(self.related_agents)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Learning':
        """Create from dictionary."""
        data['learning_type'] = LearningType(data['learning_type'])
        data['confidence'] = ConfidenceLevel(data['confidence'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        data['last_seen'] = datetime.fromisoformat(data['last_seen'])
        data['tags'] = set(data['tags'])
        data['related_agents'] = set(data['related_agents'])
        return cls(**data)


@dataclass
class InteractionRecord:
    """Records a single agent interaction for learning."""
    interaction_id: str
    agent_type: str
    task_description: str

    # Execution details
    actions_taken: List[Dict[str, Any]]
    results: List[Dict[str, Any]]

    # Outcome
    success: bool
    completion_time: float  # seconds
    iterations: int
    errors_encountered: int

    # Context
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class LearningEngine:
    """
    Advanced Learning Engine that learns from all agent interactions.

    Capabilities:
    - Records all agent interactions
    - Analyzes patterns in successes and failures
    - Extracts learnings automatically
    - Provides insights for future tasks
    - Evolves knowledge over time
    """

    def __init__(self):
        """Initialize learning engine."""
        self.learnings: Dict[str, Learning] = {}
        self.interaction_history: List[InteractionRecord] = []
        self.learning_counter = 0
        self.interaction_counter = 0

        # Pattern detection
        self.success_patterns: Dict[str, int] = defaultdict(int)
        self.failure_patterns: Dict[str, int] = defaultdict(int)

        # Performance tracking
        self.agent_performance: Dict[str, List[float]] = defaultdict(list)
        self.task_type_performance: Dict[str, List[float]] = defaultdict(list)

        logger.info("✨ LearningEngine initialized")

    async def record_interaction(
        self,
        agent_type: str,
        task_description: str,
        actions_taken: List[Dict[str, Any]],
        results: List[Dict[str, Any]],
        success: bool,
        completion_time: float,
        iterations: int,
        errors_encountered: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InteractionRecord:
        """
        Record an agent interaction for learning.

        Args:
            agent_type: Type of agent that executed the task
            task_description: Description of the task
            actions_taken: List of actions executed
            results: Results of each action
            success: Whether the task succeeded
            completion_time: Time taken to complete (seconds)
            iterations: Number of iterations
            errors_encountered: Number of errors
            metadata: Additional metadata

        Returns:
            InteractionRecord
        """
        self.interaction_counter += 1
        interaction_id = f"interaction_{self.interaction_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        interaction = InteractionRecord(
            interaction_id=interaction_id,
            agent_type=agent_type,
            task_description=task_description,
            actions_taken=actions_taken,
            results=results,
            success=success,
            completion_time=completion_time,
            iterations=iterations,
            errors_encountered=errors_encountered,
            metadata=metadata or {}
        )

        self.interaction_history.append(interaction)

        # Update performance tracking
        self.agent_performance[agent_type].append(1.0 if success else 0.0)

        logger.info(f"📝 Recorded interaction: {interaction_id} ({agent_type}, {'✅ success' if success else '❌ failed'})")

        # Trigger learning analysis asynchronously
        asyncio.create_task(self._analyze_interaction(interaction))

        return interaction

    async def _analyze_interaction(self, interaction: InteractionRecord):
        """
        Analyze an interaction and extract learnings.

        This runs asynchronously after each interaction.
        """
        try:
            # Pattern detection
            if interaction.success:
                await self._extract_success_patterns(interaction)
            else:
                await self._extract_failure_patterns(interaction)

            # Optimization opportunities
            if interaction.iterations > 5 or interaction.completion_time > 60:
                await self._identify_optimization_opportunities(interaction)

            # Error recovery patterns
            if interaction.errors_encountered > 0 and interaction.success:
                await self._extract_error_recovery_patterns(interaction)

        except Exception as e:
            logger.error(f"Error analyzing interaction: {e}")

    async def _extract_success_patterns(self, interaction: InteractionRecord):
        """Extract patterns from successful interactions."""
        # Identify successful action sequences
        if len(interaction.actions_taken) >= 2:
            # Extract action sequence pattern
            action_sequence = " -> ".join([a.get("type", "unknown") for a in interaction.actions_taken])
            pattern_key = f"success_{interaction.agent_type}_{action_sequence}"

            self.success_patterns[pattern_key] += 1

            # If pattern is frequent, create a learning
            if self.success_patterns[pattern_key] >= 3:
                await self._create_or_update_learning(
                    learning_type=LearningType.SUCCESS_PATTERN,
                    title=f"Successful {interaction.agent_type} pattern: {action_sequence}",
                    description=f"The action sequence '{action_sequence}' has been successful {self.success_patterns[pattern_key]} times for {interaction.agent_type} agent.",
                    context={
                        "agent_type": interaction.agent_type,
                        "action_sequence": action_sequence,
                        "task_description": interaction.task_description,
                        "avg_completion_time": interaction.completion_time,
                        "pattern_key": pattern_key
                    },
                    tags={interaction.agent_type, "success", "pattern", "action_sequence"},
                    related_agents={interaction.agent_type},
                    evidence={
                        "interaction_id": interaction.interaction_id,
                        "timestamp": interaction.timestamp.isoformat(),
                        "actions": interaction.actions_taken,
                        "completion_time": interaction.completion_time
                    }
                )

        # Extract task-specific strategies
        task_keywords = self._extract_keywords(interaction.task_description)
        if task_keywords:
            for keyword in task_keywords:
                strategy_key = f"strategy_{keyword}_{interaction.agent_type}"
                self.success_patterns[strategy_key] += 1

                if self.success_patterns[strategy_key] >= 2:
                    await self._create_or_update_learning(
                        learning_type=LearningType.TASK_STRATEGY,
                        title=f"Strategy for '{keyword}' tasks",
                        description=f"Using {interaction.agent_type} agent for '{keyword}' tasks has been successful {self.success_patterns[strategy_key]} times.",
                        context={
                            "task_keyword": keyword,
                            "agent_type": interaction.agent_type,
                            "success_count": self.success_patterns[strategy_key]
                        },
                        tags={keyword, interaction.agent_type, "strategy"},
                        related_agents={interaction.agent_type},
                        applicable_to=[keyword]
                    )

    async def _extract_failure_patterns(self, interaction: InteractionRecord):
        """Extract patterns from failed interactions."""
        # Identify failure patterns to avoid
        if interaction.actions_taken:
            last_action = interaction.actions_taken[-1]
            failure_key = f"failure_{interaction.agent_type}_{last_action.get('type')}"

            self.failure_patterns[failure_key] += 1

            # If failure is recurring, create a learning
            if self.failure_patterns[failure_key] >= 2:
                await self._create_or_update_learning(
                    learning_type=LearningType.FAILURE_PATTERN,
                    title=f"Common failure: {interaction.agent_type} - {last_action.get('type')}",
                    description=f"Action '{last_action.get('type')}' in {interaction.agent_type} agent has failed {self.failure_patterns[failure_key]} times. Consider alternative approaches.",
                    context={
                        "agent_type": interaction.agent_type,
                        "failed_action": last_action.get('type'),
                        "failure_count": self.failure_patterns[failure_key],
                        "common_errors": [r.get("error") for r in interaction.results if r.get("error")]
                    },
                    tags={interaction.agent_type, "failure", "warning", last_action.get('type')},
                    related_agents={interaction.agent_type},
                    evidence={
                        "interaction_id": interaction.interaction_id,
                        "timestamp": interaction.timestamp.isoformat(),
                        "failed_action": last_action,
                        "errors": interaction.errors_encountered
                    }
                )

    async def _identify_optimization_opportunities(self, interaction: InteractionRecord):
        """Identify opportunities to optimize performance."""
        if interaction.iterations > 5:
            await self._create_or_update_learning(
                learning_type=LearningType.OPTIMIZATION,
                title=f"High iteration count for {interaction.agent_type}",
                description=f"Tasks like '{interaction.task_description[:50]}...' took {interaction.iterations} iterations. Consider optimizing the approach.",
                context={
                    "agent_type": interaction.agent_type,
                    "iterations": interaction.iterations,
                    "completion_time": interaction.completion_time,
                    "task_pattern": self._extract_keywords(interaction.task_description)
                },
                tags={interaction.agent_type, "optimization", "performance"},
                related_agents={interaction.agent_type}
            )

        if interaction.completion_time > 60:
            await self._create_or_update_learning(
                learning_type=LearningType.OPTIMIZATION,
                title=f"Slow execution for {interaction.agent_type}",
                description=f"Tasks took {interaction.completion_time:.1f}s. Consider optimization or parallel execution.",
                context={
                    "agent_type": interaction.agent_type,
                    "completion_time": interaction.completion_time,
                    "actions_count": len(interaction.actions_taken)
                },
                tags={interaction.agent_type, "optimization", "slow"},
                related_agents={interaction.agent_type}
            )

    async def _extract_error_recovery_patterns(self, interaction: InteractionRecord):
        """Extract patterns for recovering from errors."""
        # This task encountered errors but still succeeded - valuable learning!
        recovery_actions = []

        for i, result in enumerate(interaction.results):
            if not result.get("success") and i + 1 < len(interaction.results):
                # Found an error followed by more actions
                recovery_action = interaction.actions_taken[i + 1]
                recovery_actions.append({
                    "error": result.get("error"),
                    "recovery": recovery_action
                })

        if recovery_actions:
            await self._create_or_update_learning(
                learning_type=LearningType.ERROR_RECOVERY,
                title=f"Error recovery pattern for {interaction.agent_type}",
                description=f"Successfully recovered from {len(recovery_actions)} errors during task execution.",
                context={
                    "agent_type": interaction.agent_type,
                    "recovery_actions": recovery_actions,
                    "total_errors": interaction.errors_encountered,
                    "final_outcome": "success"
                },
                tags={interaction.agent_type, "error_recovery", "resilience"},
                related_agents={interaction.agent_type},
                evidence={
                    "interaction_id": interaction.interaction_id,
                    "recovery_actions": recovery_actions
                }
            )

    async def _create_or_update_learning(
        self,
        learning_type: LearningType,
        title: str,
        description: str,
        context: Dict[str, Any],
        tags: Set[str],
        related_agents: Set[str],
        evidence: Optional[Dict[str, Any]] = None,
        applicable_to: Optional[List[str]] = None
    ):
        """Create a new learning or update existing one."""
        # Check if similar learning exists
        learning_key = f"{learning_type.value}_{title}"

        if learning_key in self.learnings:
            # Update existing learning
            learning = self.learnings[learning_key]
            learning.occurrences += 1
            learning.updated_at = datetime.now()
            learning.last_seen = datetime.now()
            learning.tags.update(tags)
            learning.related_agents.update(related_agents)

            if evidence:
                learning.evidence.append(evidence)

            # Update confidence based on occurrences
            if learning.occurrences >= 11:
                learning.confidence = ConfidenceLevel.VERY_HIGH
            elif learning.occurrences >= 6:
                learning.confidence = ConfidenceLevel.HIGH
            elif learning.occurrences >= 3:
                learning.confidence = ConfidenceLevel.MEDIUM
            else:
                learning.confidence = ConfidenceLevel.LOW

            logger.info(f"📈 Updated learning: {title} (occurrences: {learning.occurrences}, confidence: {learning.confidence.name})")
        else:
            # Create new learning
            self.learning_counter += 1
            learning_id = f"learning_{self.learning_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            learning = Learning(
                learning_id=learning_id,
                learning_type=learning_type,
                title=title,
                description=description,
                context=context,
                tags=tags,
                related_agents=related_agents,
                applicable_to=applicable_to or []
            )

            if evidence:
                learning.evidence.append(evidence)

            self.learnings[learning_key] = learning
            logger.info(f"✨ Created learning: {title} (type: {learning_type.value})")

    def get_relevant_learnings(
        self,
        task_description: str,
        agent_type: Optional[str] = None,
        learning_types: Optional[List[LearningType]] = None,
        min_confidence: ConfidenceLevel = ConfidenceLevel.LOW
    ) -> List[Learning]:
        """
        Get learnings relevant to a specific task.

        Args:
            task_description: Task description
            agent_type: Filter by agent type
            learning_types: Filter by learning types
            min_confidence: Minimum confidence level

        Returns:
            List of relevant learnings, sorted by relevance
        """
        task_keywords = set(self._extract_keywords(task_description))
        relevant = []

        for learning in self.learnings.values():
            # Filter by confidence
            if learning.confidence.value < min_confidence.value:
                continue

            # Filter by agent type
            if agent_type and agent_type not in learning.related_agents:
                continue

            # Filter by learning type
            if learning_types and learning.learning_type not in learning_types:
                continue

            # Calculate relevance score
            relevance = 0

            # Check tag overlap
            tag_overlap = task_keywords.intersection(learning.tags)
            relevance += len(tag_overlap) * 2

            # Check applicable_to
            for applicable in learning.applicable_to:
                if applicable in task_description.lower():
                    relevance += 3

            # Boost by confidence
            relevance += learning.confidence.value

            # Boost by occurrences
            relevance += min(learning.occurrences / 10.0, 2.0)

            if relevance > 0:
                relevant.append((relevance, learning))

        # Sort by relevance
        relevant.sort(key=lambda x: x[0], reverse=True)

        return [learning for _, learning in relevant]

    def get_learnings_by_type(self, learning_type: LearningType) -> List[Learning]:
        """Get all learnings of a specific type."""
        return [
            learning for learning in self.learnings.values()
            if learning.learning_type == learning_type
        ]

    def get_high_confidence_learnings(self) -> List[Learning]:
        """Get all high-confidence learnings."""
        return [
            learning for learning in self.learnings.values()
            if learning.confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]
        ]

    def get_agent_performance_summary(self, agent_type: str) -> Dict[str, Any]:
        """Get performance summary for an agent."""
        if agent_type not in self.agent_performance:
            return {"error": "No data for this agent"}

        performance_data = self.agent_performance[agent_type]

        return {
            "agent_type": agent_type,
            "total_interactions": len(performance_data),
            "success_rate": sum(performance_data) / len(performance_data) if performance_data else 0,
            "successes": int(sum(performance_data)),
            "failures": len(performance_data) - int(sum(performance_data)),
            "related_learnings": len([
                l for l in self.learnings.values()
                if agent_type in l.related_agents
            ])
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get learning engine statistics."""
        return {
            "total_interactions": len(self.interaction_history),
            "total_learnings": len(self.learnings),
            "by_type": {
                learning_type.value: len(self.get_learnings_by_type(learning_type))
                for learning_type in LearningType
            },
            "by_confidence": {
                conf.name: len([l for l in self.learnings.values() if l.confidence == conf])
                for conf in ConfidenceLevel
            },
            "high_confidence_learnings": len(self.get_high_confidence_learnings()),
            "success_patterns": len(self.success_patterns),
            "failure_patterns": len(self.failure_patterns),
            "agents_tracked": len(self.agent_performance)
        }

    def export_learnings(self) -> List[Dict[str, Any]]:
        """Export all learnings to JSON-serializable format."""
        return [learning.to_dict() for learning in self.learnings.values()]

    def import_learnings(self, learnings_data: List[Dict[str, Any]]):
        """Import learnings from JSON data."""
        for data in learnings_data:
            try:
                learning = Learning.from_dict(data)
                self.learnings[f"{learning.learning_type.value}_{learning.title}"] = learning
                logger.info(f"Imported learning: {learning.title}")
            except Exception as e:
                logger.error(f"Failed to import learning: {e}")

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for pattern matching."""
        # Simple keyword extraction
        # In production, use NLP techniques
        keywords = []

        common_task_words = [
            "create", "test", "debug", "review", "refactor", "implement",
            "fix", "analyze", "optimize", "deploy", "build", "search"
        ]

        text_lower = text.lower()
        for word in common_task_words:
            if word in text_lower:
                keywords.append(word)

        # Extract technology keywords
        tech_keywords = [
            "python", "javascript", "typescript", "go", "rust", "java",
            "api", "database", "frontend", "backend", "web", "mobile"
        ]

        for tech in tech_keywords:
            if tech in text_lower:
                keywords.append(tech)

        return keywords


# Global singleton instance
learning_engine = LearningEngine()
