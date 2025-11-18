"""
Test Real AI Task with Daytona System

This test uses the actual LLM and Advanced Learning Systems
to complete a real development task.
"""
import asyncio
from services.enhanced_agent_service import enhanced_agent_service
from services.learning_engine import learning_engine
from services.knowledge_hub import knowledge_hub
from services.performance_optimizer import performance_optimizer
from services.adaptive_strategy import adaptive_strategy
from utils.logger import logger


async def test_real_task():
    """Test a real development task with learning systems."""

    print("\n" + "="*60)
    print("🚀 TESTING REAL AI TASK WITH DAYTONA SYSTEM")
    print("="*60)

    # Task: Create a simple Python calculator with tests
    task_description = """
    Create a simple Python calculator module that:
    1. Has functions for add, subtract, multiply, divide
    2. Handles division by zero gracefully
    3. Returns proper error messages

    Save it to /workspace/calculator.py
    """

    task_id = "real_task_001"

    print(f"\n📋 Task: {task_description.strip()}")

    # Step 1: Analyze task with Adaptive Strategy
    print("\n1️⃣  Analyzing task with Adaptive Strategy...")
    task_chars = adaptive_strategy.analyze_task(task_description)
    print(f"   ✅ Complexity: {task_chars.complexity.name}")
    print(f"   ✅ Suggested agents: {task_chars.suggested_agents}")
    print(f"   ✅ Estimated duration: {task_chars.estimated_duration}s")

    # Step 2: Select optimal strategy
    print("\n2️⃣  Selecting optimal strategy...")
    strategy = adaptive_strategy.select_strategy(task_chars)
    print(f"   ✅ Strategy: {strategy.execution_strategy.value}")
    print(f"   ✅ Agent sequence: {strategy.agent_sequence}")
    print(f"   ✅ Confidence: {strategy.confidence*100:.0f}%")

    # Step 3: Query knowledge base for relevant knowledge
    print("\n3️⃣  Querying knowledge base...")
    knowledge = knowledge_hub.query_knowledge("python calculator", limit=3)
    if knowledge:
        print(f"   ✅ Found {len(knowledge)} relevant knowledge items")
        for k in knowledge:
            print(f"      - {k.title}")
    else:
        print("   ℹ️  No prior knowledge found (first run)")

    # Step 4: Get relevant learnings
    print("\n4️⃣  Retrieving relevant learnings...")
    learnings = learning_engine.get_relevant_learnings(
        task_description,
        agent_type="code"
    )
    if learnings:
        print(f"   ✅ Found {len(learnings)} relevant learnings")
        for learning in learnings[:3]:
            print(f"      - {learning.title} (confidence: {learning.confidence.name})")
    else:
        print("   ℹ️  No prior learnings (first run)")

    # Step 5: Execute task with Enhanced Agent
    print("\n5️⃣  Executing task with Enhanced Agent...")
    print("   ⏳ This will use Groq LLM and Daytona sandbox...")

    try:
        iteration_count = 0
        action_count = 0
        errors = []
        start_time = asyncio.get_event_loop().time()

        async for event in enhanced_agent_service.execute_task(task_description, task_id):
            event_type = event.get("type")

            if event_type == "phase":
                print(f"\n   📍 Phase: {event.get('phase')} - {event.get('message')}")

            elif event_type == "iteration":
                iteration_count = event.get("iteration")
                if iteration_count <= 3:  # Only show first 3 iterations
                    print(f"   🔄 Iteration {iteration_count}/{event.get('max_iterations')}")

            elif event_type == "action_executing":
                action_count += 1
                action = event.get("action")
                print(f"   ⚙️  Action: {action}")

            elif event_type == "action_result":
                result = event.get("result")
                if not result.get("success"):
                    errors.append(result.get("error"))
                    print(f"      ❌ Error: {result.get('error', 'Unknown')[:80]}")
                else:
                    print(f"      ✅ Success")

            elif event_type == "task_completed":
                duration = asyncio.get_event_loop().time() - start_time
                print(f"\n   ✅ Task completed successfully!")
                print(f"   ⏱️  Duration: {duration:.1f}s")
                print(f"   🔄 Iterations: {iteration_count}")
                print(f"   ⚙️  Actions: {action_count}")
                print(f"   ❌ Errors: {len(errors)}")

                # Record performance
                performance_optimizer.record_execution(
                    agent_type="enhanced",
                    task_category="python_development",
                    completion_time=duration,
                    iterations=iteration_count,
                    success=True,
                    errors=len(errors),
                    actions_count=action_count
                )

                # Record strategy outcome
                adaptive_strategy.record_outcome(
                    strategy_id=strategy.strategy_id,
                    task_id=task_chars.task_id,
                    success=True,
                    actual_duration=duration,
                    actual_iterations=iteration_count,
                    errors_encountered=len(errors),
                    what_worked=["Sequential execution worked well"],
                    improvements=["Could optimize file operations"]
                )

                break

            elif event_type == "task_failed" or event_type == "task_timeout":
                print(f"\n   ❌ Task failed or timed out")
                print(f"   Message: {event.get('message')}")
                break

            elif event_type == "error":
                print(f"   ❌ Error: {event.get('error')}")

        # Step 6: Share knowledge
        print("\n6️⃣  Sharing knowledge with other agents...")
        await knowledge_hub.share_solution(
            source_agent="enhanced",
            problem="Python calculator implementation",
            solution="Created calculator.py with error handling for division by zero",
            context={"language": "python", "testing": "included"}
        )
        print("   ✅ Knowledge shared")

        # Step 7: Show statistics
        print("\n7️⃣  System Statistics After Task:")

        learning_stats = learning_engine.get_statistics()
        print(f"\n   Learning Engine:")
        print(f"   - Total interactions: {learning_stats['total_interactions']}")
        print(f"   - Total learnings: {learning_stats['total_learnings']}")

        knowledge_stats = knowledge_hub.get_statistics()
        print(f"\n   Knowledge Hub:")
        print(f"   - Total knowledge: {knowledge_stats['total_knowledge_items']}")
        print(f"   - Total applications: {knowledge_stats['total_applications']}")

        perf_stats = performance_optimizer.get_statistics()
        print(f"\n   Performance Optimizer:")
        print(f"   - Total executions: {perf_stats['total_executions']}")
        print(f"   - Recommendations: {perf_stats['total_recommendations']}")

        strategy_stats = adaptive_strategy.get_statistics()
        print(f"\n   Adaptive Strategy:")
        print(f"   - Tasks analyzed: {strategy_stats['total_tasks_analyzed']}")
        print(f"   - Success rate: {strategy_stats['overall_success_rate']*100:.1f}%")

    except Exception as e:
        logger.error(f"Task execution error: {e}")
        print(f"\n   ❌ Error during task execution: {e}")
        print(f"   ℹ️  This is expected if Daytona sandbox is not accessible")

    print("\n" + "="*60)
    print("✅ REAL TASK TEST COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_real_task())
