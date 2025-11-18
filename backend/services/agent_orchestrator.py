"""
Agent Orchestrator - Coordinates multiple specialized agents working together.

Capabilities:
- Agent registry and discovery
- Task delegation to specialized agents
- Sequential and parallel execution
- Result aggregation
- Inter-agent communication

Part of Phase 3: Multi-Agent System
"""
import asyncio
from typing import Dict, Any, List, Optional, Callable, Set
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
from utils.logger import logger


class AgentType(Enum):
    """Types of specialized agents."""
    MAIN = "main"                    # Main controller agent
    KNOWLEDGE = "knowledge"          # Research and information retrieval
    CODE = "code"                    # Code implementation
    TEST = "test"                    # Testing and verification
    REVIEW = "review"                # Code review
    DEBUG = "debug"                  # Debugging and troubleshooting
    PLANNER = "planner"              # Strategic planning
    BROWSER = "browser"              # Web automation
    SANDBOX = "sandbox"              # Sandbox operations


class TaskStatus(Enum):
    """Status of a delegated task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionMode(Enum):
    """Execution modes for multi-agent tasks."""
    SEQUENTIAL = "sequential"        # Execute one after another
    PARALLEL = "parallel"            # Execute simultaneously
    HIERARCHICAL = "hierarchical"    # Main delegates to sub-agents
    CONSENSUS = "consensus"          # Multiple agents vote on decision


@dataclass
class AgentCapability:
    """Describes what an agent can do."""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    estimated_time: float = 0.0      # Seconds
    cost_estimate: float = 0.0       # USD


@dataclass
class RegisteredAgent:
    """A registered agent in the system."""
    agent_type: AgentType
    name: str
    description: str
    capabilities: List[AgentCapability]
    executor: Callable                # Async function to execute tasks
    priority: int = 5                 # 1-10, higher = more priority
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DelegatedTask:
    """A task delegated to an agent."""
    task_id: str
    agent_type: AgentType
    description: str
    input_data: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parent_task_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentOrchestrator:
    """
    Orchestrates multiple specialized agents.

    Responsibilities:
    - Register and manage agents
    - Route tasks to appropriate agents
    - Execute tasks in various patterns (sequential, parallel, etc.)
    - Aggregate results from multiple agents
    - Handle inter-agent communication
    """

    def __init__(self):
        """Initialize the orchestrator."""
        self.agents: Dict[AgentType, RegisteredAgent] = {}
        self.tasks: Dict[str, DelegatedTask] = {}
        self.task_counter = 0
        logger.info("AgentOrchestrator initialized")

    def register_agent(
        self,
        agent_type: AgentType,
        name: str,
        description: str,
        capabilities: List[AgentCapability],
        executor: Callable,
        priority: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a specialized agent.

        Args:
            agent_type: Type of agent
            name: Agent name
            description: Agent description
            capabilities: List of agent capabilities
            executor: Async function to execute tasks
            priority: Priority level (1-10)
            metadata: Optional metadata
        """
        agent = RegisteredAgent(
            agent_type=agent_type,
            name=name,
            description=description,
            capabilities=capabilities,
            executor=executor,
            priority=priority,
            metadata=metadata or {}
        )

        self.agents[agent_type] = agent
        logger.info(f"✅ Registered agent: {name} ({agent_type.value})")

    def unregister_agent(self, agent_type: AgentType) -> bool:
        """
        Unregister an agent.

        Args:
            agent_type: Type of agent to unregister

        Returns:
            True if agent was unregistered, False if not found
        """
        if agent_type in self.agents:
            agent = self.agents[agent_type]
            del self.agents[agent_type]
            logger.info(f"Unregistered agent: {agent.name}")
            return True
        return False

    def get_agent(self, agent_type: AgentType) -> Optional[RegisteredAgent]:
        """
        Get a registered agent by type.

        Args:
            agent_type: Type of agent

        Returns:
            RegisteredAgent or None if not found
        """
        return self.agents.get(agent_type)

    def get_all_agents(self) -> List[RegisteredAgent]:
        """
        Get all registered agents.

        Returns:
            List of all registered agents
        """
        return list(self.agents.values())

    def find_agent_for_task(self, task_description: str) -> Optional[AgentType]:
        """
        Find the best agent for a task based on capabilities.

        Args:
            task_description: Description of the task

        Returns:
            AgentType or None if no suitable agent found
        """
        # Simple keyword matching for now
        # In production, use ML-based task classification
        keywords = task_description.lower()

        if any(kw in keywords for kw in ["search", "research", "find", "lookup", "web"]):
            return AgentType.KNOWLEDGE
        elif any(kw in keywords for kw in ["code", "implement", "write", "create", "build"]):
            return AgentType.CODE
        elif any(kw in keywords for kw in ["test", "verify", "check", "validate"]):
            return AgentType.TEST
        elif any(kw in keywords for kw in ["review", "analyze", "inspect", "audit"]):
            return AgentType.REVIEW
        elif any(kw in keywords for kw in ["debug", "fix", "error", "bug", "issue"]):
            return AgentType.DEBUG
        elif any(kw in keywords for kw in ["plan", "strategy", "approach", "design"]):
            return AgentType.PLANNER
        elif any(kw in keywords for kw in ["browse", "navigate", "click", "web automation"]):
            return AgentType.BROWSER

        return None

    async def delegate_task(
        self,
        agent_type: AgentType,
        description: str,
        input_data: Dict[str, Any],
        parent_task_id: Optional[str] = None
    ) -> DelegatedTask:
        """
        Delegate a task to a specialized agent.

        Args:
            agent_type: Type of agent to delegate to
            description: Task description
            input_data: Input data for the task
            parent_task_id: Optional parent task ID

        Returns:
            DelegatedTask with results
        """
        # Generate task ID
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create task
        task = DelegatedTask(
            task_id=task_id,
            agent_type=agent_type,
            description=description,
            input_data=input_data,
            parent_task_id=parent_task_id
        )

        self.tasks[task_id] = task

        logger.info(f"📤 Delegating task {task_id} to {agent_type.value}: {description}")

        # Check if agent exists
        agent = self.get_agent(agent_type)
        if not agent:
            task.status = TaskStatus.FAILED
            task.error = f"Agent {agent_type.value} not registered"
            logger.error(f"❌ {task.error}")
            return task

        if not agent.active:
            task.status = TaskStatus.FAILED
            task.error = f"Agent {agent_type.value} is not active"
            logger.error(f"❌ {task.error}")
            return task

        # Execute task
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()

        try:
            # Call agent's executor
            result = await agent.executor(description, input_data)

            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()

            duration = (task.completed_at - task.started_at).total_seconds()
            logger.info(f"✅ Task {task_id} completed in {duration:.2f}s")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()

            logger.error(f"❌ Task {task_id} failed: {e}")

        return task

    async def execute_sequential(
        self,
        tasks: List[Dict[str, Any]],
        parent_task_id: Optional[str] = None
    ) -> List[DelegatedTask]:
        """
        Execute tasks sequentially (one after another).

        Args:
            tasks: List of task definitions
                   [{"agent_type": AgentType.KNOWLEDGE, "description": "...", "input": {...}}, ...]
            parent_task_id: Optional parent task ID

        Returns:
            List of completed tasks
        """
        logger.info(f"🔄 Executing {len(tasks)} tasks sequentially")

        results = []
        for i, task_def in enumerate(tasks):
            logger.info(f"  Step {i+1}/{len(tasks)}: {task_def['description'][:50]}...")

            task = await self.delegate_task(
                agent_type=task_def["agent_type"],
                description=task_def["description"],
                input_data=task_def.get("input", {}),
                parent_task_id=parent_task_id
            )

            results.append(task)

            # If task failed and we're in strict mode, stop
            if task.status == TaskStatus.FAILED and task_def.get("strict", False):
                logger.error(f"Sequential execution stopped at step {i+1} due to failure")
                break

        logger.info(f"✅ Sequential execution complete: {len(results)} tasks")
        return results

    async def execute_parallel(
        self,
        tasks: List[Dict[str, Any]],
        parent_task_id: Optional[str] = None
    ) -> List[DelegatedTask]:
        """
        Execute tasks in parallel (simultaneously).

        Args:
            tasks: List of task definitions
            parent_task_id: Optional parent task ID

        Returns:
            List of completed tasks
        """
        logger.info(f"⚡ Executing {len(tasks)} tasks in parallel")

        # Create all delegation coroutines
        task_coroutines = [
            self.delegate_task(
                agent_type=task_def["agent_type"],
                description=task_def["description"],
                input_data=task_def.get("input", {}),
                parent_task_id=parent_task_id
            )
            for task_def in tasks
        ]

        # Execute all in parallel
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create failed task
                self.task_counter += 1
                task_id = f"task_{self.task_counter}_failed"
                failed_task = DelegatedTask(
                    task_id=task_id,
                    agent_type=tasks[i]["agent_type"],
                    description=tasks[i]["description"],
                    input_data=tasks[i].get("input", {}),
                    status=TaskStatus.FAILED,
                    error=str(result)
                )
                processed_results.append(failed_task)
            else:
                processed_results.append(result)

        logger.info(f"✅ Parallel execution complete: {len(processed_results)} tasks")
        return processed_results

    async def execute_hierarchical(
        self,
        main_task: str,
        subtasks: List[Dict[str, Any]],
        aggregation_strategy: str = "concat"
    ) -> Dict[str, Any]:
        """
        Execute hierarchical task delegation.

        Main task is broken into subtasks, each handled by specialized agents.
        Results are aggregated back to the main task.

        Args:
            main_task: Main task description
            subtasks: List of subtask definitions
            aggregation_strategy: How to aggregate results (concat, vote, merge)

        Returns:
            Aggregated results
        """
        logger.info(f"🏗️  Hierarchical execution: {main_task}")
        logger.info(f"   Subtasks: {len(subtasks)}")

        # Generate parent task ID
        self.task_counter += 1
        parent_task_id = f"task_{self.task_counter}_hierarchical"

        # Execute subtasks in parallel
        subtask_results = await self.execute_parallel(subtasks, parent_task_id=parent_task_id)

        # Aggregate results
        aggregated = self._aggregate_results(subtask_results, aggregation_strategy)

        logger.info(f"✅ Hierarchical execution complete")

        return {
            "main_task": main_task,
            "parent_task_id": parent_task_id,
            "subtasks_count": len(subtasks),
            "successful": sum(1 for t in subtask_results if t.status == TaskStatus.COMPLETED),
            "failed": sum(1 for t in subtask_results if t.status == TaskStatus.FAILED),
            "results": aggregated,
            "subtask_details": [
                {
                    "task_id": t.task_id,
                    "agent": t.agent_type.value,
                    "status": t.status.value,
                    "result": t.result
                }
                for t in subtask_results
            ]
        }

    async def execute_consensus(
        self,
        task: str,
        agents: List[AgentType],
        input_data: Dict[str, Any],
        min_agreement: float = 0.6
    ) -> Dict[str, Any]:
        """
        Execute consensus decision making across multiple agents.

        Multiple agents work on the same task and vote on the result.

        Args:
            task: Task description
            agents: List of agent types to consult
            input_data: Input data
            min_agreement: Minimum agreement threshold (0.0-1.0)

        Returns:
            Consensus result with agreement level
        """
        logger.info(f"🗳️  Consensus execution with {len(agents)} agents")
        logger.info(f"   Minimum agreement: {min_agreement*100}%")

        # Create task for each agent
        tasks = [
            {
                "agent_type": agent_type,
                "description": task,
                "input": input_data
            }
            for agent_type in agents
        ]

        # Execute in parallel
        results = await self.execute_parallel(tasks)

        # Analyze consensus
        successful = [r for r in results if r.status == TaskStatus.COMPLETED]
        if not successful:
            return {
                "consensus": False,
                "agreement": 0.0,
                "error": "No agents completed successfully"
            }

        # Simple voting: compare results
        # In production, use more sophisticated consensus algorithms
        result_votes = {}
        for task_result in successful:
            result_key = str(task_result.result)  # Simple string comparison
            result_votes[result_key] = result_votes.get(result_key, 0) + 1

        # Find most common result
        winner = max(result_votes.items(), key=lambda x: x[1])
        agreement = winner[1] / len(successful)

        consensus_reached = agreement >= min_agreement

        logger.info(f"   Agreement: {agreement*100:.1f}%")
        logger.info(f"   Consensus: {'✅ Reached' if consensus_reached else '⛔ Not reached'}")

        return {
            "consensus": consensus_reached,
            "agreement": agreement,
            "winning_result": winner[0],
            "votes": result_votes,
            "total_agents": len(agents),
            "successful_agents": len(successful),
            "individual_results": [
                {
                    "agent": r.agent_type.value,
                    "result": r.result
                }
                for r in successful
            ]
        }

    def _aggregate_results(
        self,
        tasks: List[DelegatedTask],
        strategy: str
    ) -> Any:
        """
        Aggregate results from multiple tasks.

        Args:
            tasks: List of completed tasks
            strategy: Aggregation strategy (concat, vote, merge)

        Returns:
            Aggregated result
        """
        successful = [t for t in tasks if t.status == TaskStatus.COMPLETED]

        if strategy == "concat":
            # Concatenate all results
            return [t.result for t in successful]

        elif strategy == "vote":
            # Return most common result
            if not successful:
                return None
            result_counts = {}
            for task in successful:
                key = str(task.result)
                result_counts[key] = result_counts.get(key, 0) + 1
            return max(result_counts.items(), key=lambda x: x[1])[0]

        elif strategy == "merge":
            # Merge all results into one dict
            merged = {}
            for task in successful:
                if isinstance(task.result, dict):
                    merged.update(task.result)
            return merged

        else:
            return [t.result for t in successful]

    def get_task_status(self, task_id: str) -> Optional[DelegatedTask]:
        """
        Get status of a delegated task.

        Args:
            task_id: Task ID

        Returns:
            DelegatedTask or None if not found
        """
        return self.tasks.get(task_id)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get orchestrator statistics.

        Returns:
            Statistics dictionary
        """
        total_tasks = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        in_progress = sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS)

        return {
            "registered_agents": len(self.agents),
            "agent_types": [a.agent_type.value for a in self.agents.values()],
            "total_tasks": total_tasks,
            "tasks_completed": completed,
            "tasks_failed": failed,
            "tasks_in_progress": in_progress,
            "success_rate": (completed / total_tasks * 100) if total_tasks > 0 else 0,
            "capabilities": sum(len(a.capabilities) for a in self.agents.values())
        }


# Global singleton instance
orchestrator = AgentOrchestrator()
