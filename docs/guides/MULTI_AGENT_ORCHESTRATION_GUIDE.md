# Multi-Agent Orchestration System

## Overview

The Multi-Agent Orchestration System enables coordination of multiple specialized AI agents working together to solve complex tasks. Part of Phase 3 implementation.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         Agent Orchestrator (Coordinator)            │
│  ┌──────────────────────────────────────────────┐  │
│  │  Agent Registry                               │  │
│  │  - Knowledge Agent (research & retrieval)     │  │
│  │  - Planner Agent (strategic planning)         │  │
│  │  - Browser Agent (web automation)             │  │
│  │  - Code Agent (implementation)                │  │
│  │  - Test Agent (verification)                  │  │
│  │  - Review Agent (code review)                 │  │
│  │  - Debug Agent (troubleshooting)              │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
         ↓              ↓              ↓
   ┌─────────┐    ┌─────────┐    ┌─────────┐
   │Knowledge│    │ Planner │    │ Browser │
   │  Agent  │    │  Agent  │    │  Agent  │
   └─────────┘    └─────────┘    └─────────┘
```

## Core Concepts

### 1. Agent Types

The system supports multiple specialized agent types:

| Agent Type | Purpose | Status |
|------------|---------|--------|
| **MAIN** | Main controller agent | ✅ Active |
| **KNOWLEDGE** | Research and information retrieval | ✅ Active |
| **PLANNER** | Strategic planning and task decomposition | ✅ Active |
| **BROWSER** | Web automation and interaction | ✅ Active |
| **CODE** | Code implementation | 🔜 Future |
| **TEST** | Testing and verification | 🔜 Future |
| **REVIEW** | Code review and analysis | 🔜 Future |
| **DEBUG** | Debugging and troubleshooting | 🔜 Future |

### 2. Execution Modes

Four primary execution patterns:

#### Sequential
Tasks execute one after another (A → B → C)
- **Use when:** Tasks have dependencies
- **Benefits:** Clear order, error handling
- **Example:** Research → Plan → Implement

#### Parallel
Tasks execute simultaneously (A || B || C)
- **Use when:** Tasks are independent
- **Benefits:** Speed, efficiency
- **Example:** Search multiple sources at once

#### Hierarchical
Main task delegates to specialized sub-agents
- **Use when:** Complex tasks need specialization
- **Benefits:** Division of labor, expertise
- **Example:** Main task → Research + Plan + Build

#### Consensus
Multiple agents vote on decisions
- **Use when:** Need confidence in results
- **Benefits:** Reliability, verification
- **Example:** Multiple agents recommend best framework

### 3. Task Delegation

Tasks flow through the system:

```
1. Main Agent receives task
2. Orchestrator identifies best agent
3. Task delegated to specialized agent
4. Agent executes and returns result
5. Result aggregated back to main agent
```

## API Reference

### Agent Registration

```python
from services.agent_orchestrator import orchestrator, AgentType, AgentCapability

# Register an agent
orchestrator.register_agent(
    agent_type=AgentType.KNOWLEDGE,
    name="Knowledge Agent",
    description="Research and information retrieval",
    capabilities=[
        AgentCapability(
            name="web_search",
            description="Search the web",
            input_types=["query", "max_results"],
            output_types=["search_results"],
            estimated_time=3.0
        )
    ],
    executor=my_executor_function,
    priority=7
)
```

### Task Delegation

```python
# Delegate a single task
task = await orchestrator.delegate_task(
    agent_type=AgentType.KNOWLEDGE,
    description="Research Python async patterns",
    input_data={"type": "search", "query": "Python async"}
)

print(f"Status: {task.status}")
print(f"Result: {task.result}")
```

### Sequential Execution

```python
tasks = [
    {
        "agent_type": AgentType.KNOWLEDGE,
        "description": "Research topic",
        "input": {"query": "async Python"}
    },
    {
        "agent_type": AgentType.PLANNER,
        "description": "Create plan",
        "input": {"task": "Build async app"}
    }
]

results = await orchestrator.execute_sequential(tasks)
```

### Parallel Execution

```python
tasks = [
    {"agent_type": AgentType.KNOWLEDGE, "description": "Research A", "input": {}},
    {"agent_type": AgentType.KNOWLEDGE, "description": "Research B", "input": {}},
    {"agent_type": AgentType.PLANNER, "description": "Plan C", "input": {}}
]

# All execute simultaneously
results = await orchestrator.execute_parallel(tasks)
```

### Hierarchical Execution

```python
result = await orchestrator.execute_hierarchical(
    main_task="Build web application",
    subtasks=[
        {"agent_type": AgentType.KNOWLEDGE, "description": "Research frameworks", "input": {}},
        {"agent_type": AgentType.PLANNER, "description": "Create plan", "input": {}},
        {"agent_type": AgentType.KNOWLEDGE, "description": "Research databases", "input": {}}
    ],
    aggregation_strategy="concat"  # or "vote", "merge"
)
```

### Consensus Decision

```python
result = await orchestrator.execute_consensus(
    task="What is the best Python web framework?",
    agents=[AgentType.KNOWLEDGE, AgentType.KNOWLEDGE, AgentType.KNOWLEDGE],
    input_data={"type": "research", "question": "..."},
    min_agreement=0.6  # 60% agreement required
)

if result['consensus']:
    print(f"Winner: {result['winning_result']}")
    print(f"Agreement: {result['agreement']*100}%")
```

## Integration with Enhanced Agent

The orchestration system is integrated via the `DELEGATE` action:

### From User Prompt

```
User: "Research Python async patterns and create an implementation plan"

Enhanced Agent:
  1. Uses DELEGATE action to send research to Knowledge Agent
  2. Uses DELEGATE action to send planning to Planner Agent
  3. Aggregates results and proceeds
```

### Action Syntax

```
ACTION: DELEGATE
AGENT_TYPE: knowledge
TASK: Research the best Python async libraries for web scraping
---END---
```

**Available Agent Types:**
- `knowledge` - Research and information retrieval
- `planner` - Strategic planning
- `browser` - Web automation
- `code` - Code implementation (future)
- `test` - Testing (future)
- `review` - Code review (future)
- `debug` - Debugging (future)

### Tool Masking Integration

DELEGATE action is available in:
- ✅ EXECUTING state
- ⛔ PLANNING state (agents should plan first, then delegate)
- ⛔ VERIFYING state (focused on testing)
- ⛔ LEARNING state (reflection only)

This ensures delegation happens during execution, not during planning or learning.

## Example Workflows

### 1. Research + Plan + Implement

```python
# Sequential workflow
tasks = [
    {
        "agent_type": AgentType.KNOWLEDGE,
        "description": "Research FastAPI best practices",
        "input": {"type": "research", "question": "FastAPI best practices"}
    },
    {
        "agent_type": AgentType.PLANNER,
        "description": "Plan FastAPI application",
        "input": {"task": "Build REST API with FastAPI"}
    },
    {
        "agent_type": AgentType.CODE,  # Future
        "description": "Implement the plan",
        "input": {"plan": "<plan from previous step>"}
    }
]

results = await orchestrator.execute_sequential(tasks)
```

### 2. Parallel Research

```python
# Multiple sources researched simultaneously
tasks = [
    {"agent_type": AgentType.KNOWLEDGE, "description": "Research React", "input": {}},
    {"agent_type": AgentType.KNOWLEDGE, "description": "Research Vue", "input": {}},
    {"agent_type": AgentType.KNOWLEDGE, "description": "Research Angular", "input": {}}
]

results = await orchestrator.execute_parallel(tasks)
# Compare frameworks from all three results
```

### 3. Hierarchical Complex Task

```python
# Break down complex task into specialized subtasks
result = await orchestrator.execute_hierarchical(
    main_task="Build production-ready web application",
    subtasks=[
        # Research phase
        {"agent_type": AgentType.KNOWLEDGE, "description": "Research stack", "input": {}},
        # Planning phase
        {"agent_type": AgentType.PLANNER, "description": "Create architecture", "input": {}},
        # Implementation phase
        {"agent_type": AgentType.CODE, "description": "Implement backend", "input": {}},
        # Testing phase
        {"agent_type": AgentType.TEST, "description": "Write tests", "input": {}},
        # Review phase
        {"agent_type": AgentType.REVIEW, "description": "Code review", "input": {}}
    ],
    aggregation_strategy="merge"
)
```

### 4. Consensus Verification

```python
# Get multiple opinions on a decision
result = await orchestrator.execute_consensus(
    task="Is Python 3.12 production-ready?",
    agents=[AgentType.KNOWLEDGE, AgentType.KNOWLEDGE, AgentType.KNOWLEDGE],
    input_data={"type": "verify_fact", "claim": "Python 3.12 is production-ready"},
    min_agreement=0.7
)

if result['consensus']:
    print("Consensus reached! Majority says:", result['winning_result'])
```

## Agent Capabilities

Each agent can declare its capabilities:

```python
AgentCapability(
    name="web_search",
    description="Search the web for information",
    input_types=["query", "max_results"],
    output_types=["search_results"],
    estimated_time=3.0,  # seconds
    cost_estimate=0.01   # USD
)
```

Benefits:
- **Discovery**: Find agents that can handle specific tasks
- **Planning**: Estimate time and cost before execution
- **Routing**: Automatically route tasks to capable agents

## Task Status Tracking

```python
# Delegate task
task = await orchestrator.delegate_task(...)

# Check status later
task_status = orchestrator.get_task_status(task.task_id)

print(f"Status: {task_status.status.value}")
# Possible values: pending, in_progress, completed, failed, cancelled

if task_status.status == TaskStatus.COMPLETED:
    print(f"Result: {task_status.result}")
elif task_status.status == TaskStatus.FAILED:
    print(f"Error: {task_status.error}")
```

## Statistics and Monitoring

```python
stats = orchestrator.get_statistics()

{
    "registered_agents": 3,
    "agent_types": ["knowledge", "planner", "browser"],
    "total_tasks": 47,
    "tasks_completed": 42,
    "tasks_failed": 5,
    "tasks_in_progress": 0,
    "success_rate": 89.36,
    "capabilities": 8
}
```

## Error Handling

### Agent Not Found

```python
task = await orchestrator.delegate_task(
    agent_type=AgentType.CODE,  # Not registered yet
    description="Write code",
    input_data={}
)

# task.status will be FAILED
# task.error will be "Agent code not registered"
```

### Task Failure

```python
# If an agent fails, task is marked as failed
task = await orchestrator.delegate_task(...)

if task.status == TaskStatus.FAILED:
    logger.error(f"Task failed: {task.error}")
    # Handle failure (retry, fallback, etc.)
```

### Sequential Strict Mode

```python
tasks = [
    {"agent_type": AgentType.KNOWLEDGE, "description": "...", "strict": True},
    {"agent_type": AgentType.PLANNER, "description": "..."},
]

# If first task fails and strict=True, execution stops
results = await orchestrator.execute_sequential(tasks)
```

## Performance Considerations

### Parallel vs Sequential

**Parallel:**
- ⚡ Faster for independent tasks
- 💰 May use more API calls simultaneously
- 🎯 Best for: research, data gathering

**Sequential:**
- 🐢 Slower but ordered
- 💰 Lower concurrent API usage
- 🎯 Best for: dependent tasks, workflows

### Task Granularity

**Fine-grained:**
```python
# Many small tasks
tasks = [
    {"agent_type": AgentType.KNOWLEDGE, "description": "Search A"},
    {"agent_type": AgentType.KNOWLEDGE, "description": "Search B"},
    {"agent_type": AgentType.KNOWLEDGE, "description": "Search C"},
    # ... 20 more tasks
]
# Overhead from delegation, but good parallelization
```

**Coarse-grained:**
```python
# Few large tasks
tasks = [
    {"agent_type": AgentType.KNOWLEDGE, "description": "Research everything about topic X"}
]
# Less delegation overhead, but less parallelization
```

**Recommendation:** Balance based on task complexity and independence.

## Best Practices

### 1. Choose the Right Pattern

- **Sequential:** Tasks with dependencies (A needs result from B)
- **Parallel:** Independent tasks that can run simultaneously
- **Hierarchical:** Complex tasks that benefit from specialization
- **Consensus:** Decisions requiring high confidence

### 2. Handle Failures Gracefully

```python
result = await orchestrator.delegate_task(...)

if result.status == TaskStatus.FAILED:
    # Implement retry logic
    result = await orchestrator.delegate_task(...)  # Retry

    if result.status == TaskStatus.FAILED:
        # Fallback to alternative approach
        result = await fallback_method()
```

### 3. Use Appropriate Agent Types

Don't use Knowledge Agent for code implementation - use Code Agent when available.

### 4. Monitor Performance

```python
stats = orchestrator.get_statistics()
if stats['success_rate'] < 80:
    logger.warning("Low success rate - investigate failures")
```

### 5. Set Realistic Timeouts

```python
# For long-running tasks
task = await asyncio.wait_for(
    orchestrator.delegate_task(...),
    timeout=300  # 5 minutes
)
```

## Future Enhancements

### Phase 4+

- [ ] **Code Agent**: Automated code implementation
- [ ] **Test Agent**: Automated test generation
- [ ] **Review Agent**: Automated code review
- [ ] **Debug Agent**: Automated debugging
- [ ] **Agent Learning**: Agents improve from experience
- [ ] **Dynamic Routing**: ML-based task-to-agent matching
- [ ] **Resource Management**: Agent pool with load balancing
- [ ] **Agent Marketplace**: Pluggable third-party agents

## Testing

```bash
cd /home/user/daytona/backend

# Run multi-agent demo
python demo_multi_agent.py
```

Expected output:
```
MULTI-AGENT ORCHESTRATION SYSTEM - DEMONSTRATION
=================================================================

1. SEQUENTIAL EXECUTION
Tasks execute one after another (A → B → C)
...

2. PARALLEL EXECUTION
Tasks execute simultaneously (A || B || C)
...

3. HIERARCHICAL EXECUTION
Main task → Sub-agents → Aggregated result
...

4. CONSENSUS DECISION MAKING
Multiple agents vote on the best approach
...
```

## Troubleshooting

### Issue: Agent not found

**Solution:** Ensure agent is registered:
```python
from services.agent_registry_init import register_all_agents
register_all_agents()
```

### Issue: Tasks failing

**Check:**
1. LLM API key configured: `LLM_API_KEY` in .env
2. Internet connectivity for web searches
3. Agent executor functions working correctly

### Issue: Slow execution

**Solutions:**
1. Use parallel execution for independent tasks
2. Reduce task complexity
3. Implement caching for repeated queries

## Status

✅ **IMPLEMENTED** - Phase 3, Task 3.3
✅ **TESTED** - Demo verification
✅ **INTEGRATED** - Enhanced Agent DELEGATE action
✅ **DOCUMENTED** - Complete guide
✅ **PRODUCTION READY** - Core functionality complete

---

*Implementation Date: Phase 3 (Advanced Learning & Multi-Agent Orchestration)*
*Next: Advanced Error Analysis & Pattern Recognition (Task 3.4)*
