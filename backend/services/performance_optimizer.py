"""
Performance Optimizer - Historical Performance Analysis and Optimization

Capabilities:
- Track agent performance over time
- Identify optimization opportunities
- Suggest performance improvements
- Analyze execution patterns
- Provide performance insights

Part of Phase 4: Task 4.5 - Advanced Learning Systems
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum
from utils.logger import logger


class OptimizationType(Enum):
    """Types of optimizations."""
    EXECUTION_SPEED = "execution_speed"
    ITERATION_REDUCTION = "iteration_reduction"
    ERROR_REDUCTION = "error_reduction"
    RESOURCE_EFFICIENCY = "resource_efficiency"
    AGENT_SELECTION = "agent_selection"
    PARALLEL_EXECUTION = "parallel_execution"
    CACHING = "caching"


@dataclass
class PerformanceMetric:
    """Represents a performance metric."""
    metric_id: str
    agent_type: str
    task_category: str

    # Timing metrics
    avg_completion_time: float  # seconds
    min_completion_time: float
    max_completion_time: float

    # Iteration metrics
    avg_iterations: float
    min_iterations: int
    max_iterations: int

    # Success metrics
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float

    # Error metrics
    avg_errors_per_execution: float
    total_errors: int

    # Resource metrics
    avg_actions_per_execution: float

    # Time window
    time_window_start: datetime
    time_window_end: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_id": self.metric_id,
            "agent_type": self.agent_type,
            "task_category": self.task_category,
            "avg_completion_time": self.avg_completion_time,
            "min_completion_time": self.min_completion_time,
            "max_completion_time": self.max_completion_time,
            "avg_iterations": self.avg_iterations,
            "min_iterations": self.min_iterations,
            "max_iterations": self.max_iterations,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate": self.success_rate,
            "avg_errors_per_execution": self.avg_errors_per_execution,
            "total_errors": self.total_errors,
            "avg_actions_per_execution": self.avg_actions_per_execution,
            "time_window_start": self.time_window_start.isoformat(),
            "time_window_end": self.time_window_end.isoformat()
        }


@dataclass
class OptimizationRecommendation:
    """Represents an optimization recommendation."""
    recommendation_id: str
    optimization_type: OptimizationType
    priority: int  # 1-10, higher = more important

    # Details
    title: str
    description: str
    current_state: Dict[str, Any]
    proposed_change: Dict[str, Any]
    expected_improvement: Dict[str, Any]

    # Applicability
    applicable_to: List[str]  # Agent types or task categories

    # Evidence
    based_on: List[str]  # Metric IDs or observation IDs
    confidence: float  # 0.0-1.0

    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "recommendation_id": self.recommendation_id,
            "optimization_type": self.optimization_type.value,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "current_state": self.current_state,
            "proposed_change": self.proposed_change,
            "expected_improvement": self.expected_improvement,
            "applicable_to": self.applicable_to,
            "based_on": self.based_on,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat()
        }


class PerformanceOptimizer:
    """
    Analyzes historical performance and provides optimization recommendations.

    Capabilities:
    - Track performance metrics over time
    - Identify bottlenecks and inefficiencies
    - Generate optimization recommendations
    - Compare agent performance
    - Suggest best practices
    """

    def __init__(self):
        """Initialize performance optimizer."""
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.recommendations: Dict[str, OptimizationRecommendation] = {}

        # Historical data
        self.execution_history: List[Dict[str, Any]] = []

        # Performance baselines
        self.baselines: Dict[str, Dict[str, float]] = {}

        # Counters
        self.metric_counter = 0
        self.recommendation_counter = 0

        logger.info("📊 PerformanceOptimizer initialized")

    def record_execution(
        self,
        agent_type: str,
        task_category: str,
        completion_time: float,
        iterations: int,
        success: bool,
        errors: int,
        actions_count: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record an execution for performance tracking.

        Args:
            agent_type: Type of agent
            task_category: Category of task
            completion_time: Time taken (seconds)
            iterations: Number of iterations
            success: Whether execution succeeded
            errors: Number of errors encountered
            actions_count: Number of actions executed
            metadata: Additional metadata
        """
        execution = {
            "agent_type": agent_type,
            "task_category": task_category,
            "completion_time": completion_time,
            "iterations": iterations,
            "success": success,
            "errors": errors,
            "actions_count": actions_count,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        }

        self.execution_history.append(execution)

        logger.info(f"📝 Recorded execution: {agent_type} - {task_category} ({completion_time:.2f}s, {iterations} iter)")

        # Update metrics if we have enough data
        if len(self.execution_history) >= 5:
            self._update_metrics(agent_type, task_category)
            self._generate_recommendations()

    def _update_metrics(self, agent_type: str, task_category: str):
        """Update performance metrics for agent and task category."""
        # Filter relevant executions
        relevant_executions = [
            e for e in self.execution_history
            if e["agent_type"] == agent_type and e["task_category"] == task_category
        ]

        if not relevant_executions:
            return

        # Calculate metrics
        completion_times = [e["completion_time"] for e in relevant_executions]
        iterations_list = [e["iterations"] for e in relevant_executions]
        successes = [e for e in relevant_executions if e["success"]]
        errors_list = [e["errors"] for e in relevant_executions]
        actions_list = [e["actions_count"] for e in relevant_executions]

        self.metric_counter += 1
        metric_id = f"metric_{self.metric_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        metric = PerformanceMetric(
            metric_id=metric_id,
            agent_type=agent_type,
            task_category=task_category,
            avg_completion_time=sum(completion_times) / len(completion_times),
            min_completion_time=min(completion_times),
            max_completion_time=max(completion_times),
            avg_iterations=sum(iterations_list) / len(iterations_list),
            min_iterations=min(iterations_list),
            max_iterations=max(iterations_list),
            total_executions=len(relevant_executions),
            successful_executions=len(successes),
            failed_executions=len(relevant_executions) - len(successes),
            success_rate=len(successes) / len(relevant_executions),
            avg_errors_per_execution=sum(errors_list) / len(errors_list),
            total_errors=sum(errors_list),
            avg_actions_per_execution=sum(actions_list) / len(actions_list),
            time_window_start=min(e["timestamp"] for e in relevant_executions),
            time_window_end=max(e["timestamp"] for e in relevant_executions)
        )

        key = f"{agent_type}_{task_category}"
        self.metrics[key] = metric

        logger.info(f"📊 Updated metrics for {agent_type} - {task_category}: {metric.success_rate*100:.1f}% success")

    def _generate_recommendations(self):
        """Generate optimization recommendations based on metrics."""
        for metric in self.metrics.values():
            # Check for slow execution
            if metric.avg_completion_time > 30:  # More than 30 seconds
                self._create_recommendation(
                    optimization_type=OptimizationType.EXECUTION_SPEED,
                    title=f"Slow execution detected: {metric.agent_type}",
                    description=f"Average completion time of {metric.avg_completion_time:.1f}s is above threshold. Consider optimization or parallel execution.",
                    current_state={
                        "avg_time": metric.avg_completion_time,
                        "agent": metric.agent_type,
                        "task_category": metric.task_category
                    },
                    proposed_change={
                        "action": "optimize_execution",
                        "suggestions": [
                            "Use parallel execution for independent tasks",
                            "Cache frequent operations",
                            "Optimize action sequences"
                        ]
                    },
                    expected_improvement={
                        "time_reduction": "30-50%",
                        "estimated_time": f"{metric.avg_completion_time * 0.5:.1f}s"
                    },
                    applicable_to=[metric.agent_type],
                    based_on=[metric.metric_id],
                    confidence=0.8,
                    priority=8
                )

            # Check for high iteration count
            if metric.avg_iterations > 8:
                self._create_recommendation(
                    optimization_type=OptimizationType.ITERATION_REDUCTION,
                    title=f"High iteration count: {metric.agent_type}",
                    description=f"Average of {metric.avg_iterations:.1f} iterations indicates potential inefficiency. Review planning and execution strategy.",
                    current_state={
                        "avg_iterations": metric.avg_iterations,
                        "agent": metric.agent_type,
                        "task_category": metric.task_category
                    },
                    proposed_change={
                        "action": "improve_planning",
                        "suggestions": [
                            "Enhance initial planning phase",
                            "Better task decomposition",
                            "Improve error handling to reduce retries"
                        ]
                    },
                    expected_improvement={
                        "iteration_reduction": "30-40%",
                        "estimated_iterations": f"{metric.avg_iterations * 0.6:.1f}"
                    },
                    applicable_to=[metric.agent_type],
                    based_on=[metric.metric_id],
                    confidence=0.75,
                    priority=7
                )

            # Check for low success rate
            if metric.success_rate < 0.8:
                self._create_recommendation(
                    optimization_type=OptimizationType.ERROR_REDUCTION,
                    title=f"Low success rate: {metric.agent_type}",
                    description=f"Success rate of {metric.success_rate*100:.1f}% is below 80%. Investigate common failure patterns.",
                    current_state={
                        "success_rate": metric.success_rate,
                        "failed_executions": metric.failed_executions,
                        "agent": metric.agent_type,
                        "task_category": metric.task_category
                    },
                    proposed_change={
                        "action": "improve_reliability",
                        "suggestions": [
                            "Analyze failure patterns",
                            "Add error recovery mechanisms",
                            "Improve input validation",
                            "Better error handling"
                        ]
                    },
                    expected_improvement={
                        "success_rate_increase": "15-20%",
                        "target_success_rate": "90%+"
                    },
                    applicable_to=[metric.agent_type],
                    based_on=[metric.metric_id],
                    confidence=0.85,
                    priority=9
                )

            # Check for high error rate
            if metric.avg_errors_per_execution > 2:
                self._create_recommendation(
                    optimization_type=OptimizationType.ERROR_REDUCTION,
                    title=f"High error rate: {metric.agent_type}",
                    description=f"Average of {metric.avg_errors_per_execution:.1f} errors per execution. Implement better error prevention.",
                    current_state={
                        "avg_errors": metric.avg_errors_per_execution,
                        "total_errors": metric.total_errors,
                        "agent": metric.agent_type
                    },
                    proposed_change={
                        "action": "error_prevention",
                        "suggestions": [
                            "Validate inputs before execution",
                            "Add pre-flight checks",
                            "Improve action planning",
                            "Learn from previous errors"
                        ]
                    },
                    expected_improvement={
                        "error_reduction": "40-60%",
                        "target_errors": "<1 per execution"
                    },
                    applicable_to=[metric.agent_type],
                    based_on=[metric.metric_id],
                    confidence=0.7,
                    priority=8
                )

    def _create_recommendation(
        self,
        optimization_type: OptimizationType,
        title: str,
        description: str,
        current_state: Dict[str, Any],
        proposed_change: Dict[str, Any],
        expected_improvement: Dict[str, Any],
        applicable_to: List[str],
        based_on: List[str],
        confidence: float,
        priority: int
    ):
        """Create an optimization recommendation."""
        # Check if similar recommendation already exists
        recommendation_key = f"{optimization_type.value}_{applicable_to[0] if applicable_to else 'general'}"

        if recommendation_key in self.recommendations:
            # Update existing recommendation
            existing = self.recommendations[recommendation_key]
            existing.based_on.extend(based_on)
            existing.confidence = min(1.0, existing.confidence + 0.05)  # Increase confidence
            return

        self.recommendation_counter += 1
        recommendation_id = f"rec_{self.recommendation_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        recommendation = OptimizationRecommendation(
            recommendation_id=recommendation_id,
            optimization_type=optimization_type,
            priority=priority,
            title=title,
            description=description,
            current_state=current_state,
            proposed_change=proposed_change,
            expected_improvement=expected_improvement,
            applicable_to=applicable_to,
            based_on=based_on,
            confidence=confidence
        )

        self.recommendations[recommendation_key] = recommendation

        logger.info(f"💡 Generated recommendation: {title} (priority: {priority}, confidence: {confidence*100:.0f}%)")

    def get_agent_performance(self, agent_type: str) -> Dict[str, Any]:
        """Get performance summary for an agent."""
        agent_metrics = [
            m for m in self.metrics.values()
            if m.agent_type == agent_type
        ]

        if not agent_metrics:
            return {"error": "No performance data available"}

        total_executions = sum(m.total_executions for m in agent_metrics)
        total_successes = sum(m.successful_executions for m in agent_metrics)
        avg_time = sum(m.avg_completion_time * m.total_executions for m in agent_metrics) / total_executions
        avg_iterations = sum(m.avg_iterations * m.total_executions for m in agent_metrics) / total_executions

        return {
            "agent_type": agent_type,
            "total_executions": total_executions,
            "success_rate": total_successes / total_executions if total_executions > 0 else 0,
            "avg_completion_time": avg_time,
            "avg_iterations": avg_iterations,
            "task_categories": len(agent_metrics),
            "recommendations": len([
                r for r in self.recommendations.values()
                if agent_type in r.applicable_to
            ])
        }

    def get_recommendations(
        self,
        agent_type: Optional[str] = None,
        optimization_type: Optional[OptimizationType] = None,
        min_priority: int = 5
    ) -> List[OptimizationRecommendation]:
        """
        Get optimization recommendations.

        Args:
            agent_type: Filter by agent type
            optimization_type: Filter by optimization type
            min_priority: Minimum priority (1-10)

        Returns:
            List of recommendations, sorted by priority
        """
        recommendations = list(self.recommendations.values())

        # Filter by agent type
        if agent_type:
            recommendations = [
                r for r in recommendations
                if agent_type in r.applicable_to
            ]

        # Filter by optimization type
        if optimization_type:
            recommendations = [
                r for r in recommendations
                if r.optimization_type == optimization_type
            ]

        # Filter by priority
        recommendations = [
            r for r in recommendations
            if r.priority >= min_priority
        ]

        # Sort by priority and confidence
        recommendations.sort(
            key=lambda r: (r.priority, r.confidence),
            reverse=True
        )

        return recommendations

    def compare_agents(
        self,
        agent1: str,
        agent2: str,
        task_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare performance between two agents.

        Args:
            agent1: First agent type
            agent2: Second agent type
            task_category: Optional task category filter

        Returns:
            Comparison results
        """
        perf1 = self.get_agent_performance(agent1)
        perf2 = self.get_agent_performance(agent2)

        if "error" in perf1 or "error" in perf2:
            return {"error": "Insufficient data for comparison"}

        comparison = {
            "agent1": agent1,
            "agent2": agent2,
            "metrics": {
                "success_rate": {
                    agent1: perf1["success_rate"],
                    agent2: perf2["success_rate"],
                    "winner": agent1 if perf1["success_rate"] > perf2["success_rate"] else agent2
                },
                "avg_completion_time": {
                    agent1: perf1["avg_completion_time"],
                    agent2: perf2["avg_completion_time"],
                    "winner": agent1 if perf1["avg_completion_time"] < perf2["avg_completion_time"] else agent2
                },
                "avg_iterations": {
                    agent1: perf1["avg_iterations"],
                    agent2: perf2["avg_iterations"],
                    "winner": agent1 if perf1["avg_iterations"] < perf2["avg_iterations"] else agent2
                }
            },
            "recommendation": self._get_agent_recommendation(perf1, perf2, agent1, agent2)
        }

        return comparison

    def _get_agent_recommendation(
        self,
        perf1: Dict[str, Any],
        perf2: Dict[str, Any],
        agent1: str,
        agent2: str
    ) -> str:
        """Get recommendation based on agent comparison."""
        score1 = (
            perf1["success_rate"] * 10 +
            (1 / perf1["avg_completion_time"]) * 5 +
            (1 / perf1["avg_iterations"]) * 3
        )

        score2 = (
            perf2["success_rate"] * 10 +
            (1 / perf2["avg_completion_time"]) * 5 +
            (1 / perf2["avg_iterations"]) * 3
        )

        if score1 > score2 * 1.2:
            return f"Strongly prefer {agent1} for this task category"
        elif score1 > score2:
            return f"Prefer {agent1} for this task category"
        elif score2 > score1 * 1.2:
            return f"Strongly prefer {agent2} for this task category"
        elif score2 > score1:
            return f"Prefer {agent2} for this task category"
        else:
            return "Both agents perform similarly"

    def get_statistics(self) -> Dict[str, Any]:
        """Get performance optimizer statistics."""
        return {
            "total_metrics": len(self.metrics),
            "total_executions": len(self.execution_history),
            "total_recommendations": len(self.recommendations),
            "by_optimization_type": {
                opt_type.value: len([
                    r for r in self.recommendations.values()
                    if r.optimization_type == opt_type
                ])
                for opt_type in OptimizationType
            },
            "high_priority_recommendations": len([
                r for r in self.recommendations.values()
                if r.priority >= 8
            ]),
            "agents_tracked": len(set(m.agent_type for m in self.metrics.values()))
        }


# Global singleton instance
performance_optimizer = PerformanceOptimizer()
