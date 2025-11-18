"""
Agent Registry Initialization - Registers all specialized agents with the orchestrator.

This module bootstraps the multi-agent system by registering:
- Knowledge Agent
- Planner Agent
- Browser Agent
- Future agents (Code, Test, Review, Debug)
"""
from services.agent_orchestrator import (
    orchestrator,
    AgentType,
    AgentCapability
)
from services.knowledge_agent_service import knowledge_agent
from services.planner_service import PlannerService
from services.browser_service import browser_service
from utils.logger import logger


# Agent executors
async def knowledge_agent_executor(description: str, input_data: dict) -> dict:
    """Execute knowledge agent tasks."""
    task_type = input_data.get("type", "search")

    if task_type == "search":
        query = input_data.get("query", description)
        max_results = input_data.get("max_results", 5)
        return await knowledge_agent.search(query, max_results=max_results)

    elif task_type == "research":
        question = input_data.get("question", description)
        depth = input_data.get("depth", "medium")
        max_sources = input_data.get("max_sources", 3)
        return await knowledge_agent.research_question(question, depth, max_sources)

    elif task_type == "verify_fact":
        claim = input_data.get("claim", description)
        context = input_data.get("context")
        return await knowledge_agent.verify_fact(claim, context)

    else:
        # Default: search
        return await knowledge_agent.search(description, max_results=5)


async def planner_agent_executor(description: str, input_data: dict) -> dict:
    """Execute planner agent tasks."""
    planner = PlannerService()
    task = input_data.get("task", description)
    context = input_data.get("context", {})
    return await planner.create_plan(task, context)


async def browser_agent_executor(description: str, input_data: dict) -> dict:
    """Execute browser agent tasks."""
    task_type = input_data.get("type", "task")

    if task_type == "task":
        task = input_data.get("task", description)
        return await browser_service.execute_browser_task(task)

    elif task_type == "structured":
        action = input_data.get("action", {})
        return await browser_service.execute_task(action)

    else:
        return await browser_service.execute_browser_task(description)


def register_all_agents():
    """
    Register all available agents with the orchestrator.

    Call this at application startup to bootstrap the multi-agent system.
    """
    logger.info("🚀 Registering agents with orchestrator...")

    # 1. Knowledge Agent
    orchestrator.register_agent(
        agent_type=AgentType.KNOWLEDGE,
        name="Knowledge Agent",
        description="Specialized agent for web research and information retrieval",
        capabilities=[
            AgentCapability(
                name="web_search",
                description="Search the web for information",
                input_types=["query", "max_results"],
                output_types=["search_results"],
                estimated_time=3.0
            ),
            AgentCapability(
                name="research_question",
                description="Research a question using multiple sources",
                input_types=["question", "depth", "max_sources"],
                output_types=["answer", "key_insights", "confidence"],
                estimated_time=10.0
            ),
            AgentCapability(
                name="verify_fact",
                description="Verify a factual claim with evidence",
                input_types=["claim", "context"],
                output_types=["verdict", "confidence", "evidence"],
                estimated_time=5.0
            )
        ],
        executor=knowledge_agent_executor,
        priority=7
    )

    # 2. Planner Agent
    orchestrator.register_agent(
        agent_type=AgentType.PLANNER,
        name="Planner Agent",
        description="Strategic planning and task decomposition",
        capabilities=[
            AgentCapability(
                name="create_plan",
                description="Break down complex tasks into actionable steps",
                input_types=["task", "context"],
                output_types=["plan", "steps", "risks", "success_criteria"],
                estimated_time=8.0
            )
        ],
        executor=planner_agent_executor,
        priority=8
    )

    # 3. Browser Agent
    orchestrator.register_agent(
        agent_type=AgentType.BROWSER,
        name="Browser Agent",
        description="Web automation and browser interaction",
        capabilities=[
            AgentCapability(
                name="browser_task",
                description="Execute browser automation tasks",
                input_types=["task"],
                output_types=["result", "url", "content"],
                estimated_time=15.0
            ),
            AgentCapability(
                name="structured_action",
                description="Execute structured browser actions (navigate, click, fill, etc.)",
                input_types=["action"],
                output_types=["result"],
                estimated_time=5.0
            )
        ],
        executor=browser_agent_executor,
        priority=6
    )

    # Log summary
    stats = orchestrator.get_statistics()
    logger.info(f"✅ Agent registration complete!")
    logger.info(f"   Registered agents: {stats['registered_agents']}")
    logger.info(f"   Agent types: {', '.join(stats['agent_types'])}")
    logger.info(f"   Total capabilities: {stats['capabilities']}")

    return orchestrator


def get_orchestrator():
    """
    Get the initialized orchestrator.

    Returns:
        Initialized AgentOrchestrator instance
    """
    if not orchestrator.agents:
        register_all_agents()
    return orchestrator


# Auto-register on import (can be disabled if needed)
AUTO_REGISTER = True

if AUTO_REGISTER:
    register_all_agents()
