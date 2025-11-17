"""
Enhanced Agent Service - Autonomous agent with planning, learning, and self-improvement.
Implements patterns from Manus AI and OpenHands research.
"""
import re
import json
from typing import Dict, Any, List, AsyncGenerator
from litellm import acompletion
from config import settings
from utils.logger import logger
from services.daytona_service import DaytonaService
from services.planner_service import PlannerService


class EnhancedAgentService:
    """
    Enhanced autonomous agent with:
    - Strategic planning (todo.md pattern)
    - Do-try-test loop (verification and validation)
    - Error learning (mistake preservation and reflection)
    - Self-improvement (logic refinement)
    """

    def __init__(self):
        """Initialize enhanced agent service."""
        self.daytona = DaytonaService()
        self.planner = PlannerService()
        self.conversation_history: List[Dict[str, Any]] = []
        self.error_memory: List[Dict[str, Any]] = []  # Learn from mistakes
        self.session_learnings: List[str] = []  # Session-level learnings
        logger.info("EnhancedAgentService initialized")

    def _get_system_prompt(self) -> str:
        """Get enhanced system prompt with planning and learning capabilities."""
        return """You are an autonomous AI agent with advanced planning and learning capabilities.

CORE CAPABILITIES:
1. Strategic Planning: Break down complex tasks into clear steps
2. Execution: Run commands, edit files, read data in a secure sandbox
3. Verification: Test your work to ensure correctness
4. Learning: Remember mistakes and improve your approach
5. Self-Reflection: Analyze results and refine your strategy

AVAILABLE ACTIONS:
1. CREATE_FILE - Create or write a file
   FORMAT:
   ACTION: CREATE_FILE
   PATH: /workspace/filename.py
   CONTENT:
   [file content here]
   ---END---

2. READ_FILE - Read a file's contents
   FORMAT:
   ACTION: READ_FILE
   PATH: /workspace/filename.py
   ---END---

3. EXECUTE - Run shell commands
   FORMAT:
   ACTION: EXECUTE
   COMMAND: python test.py
   ---END---

4. LIST_FILES - List files in directory
   FORMAT:
   ACTION: LIST_FILES
   PATH: /workspace
   ---END---

5. UPDATE_TODO - Update the task plan (todo.md pattern)
   FORMAT:
   ACTION: UPDATE_TODO
   CONTENT:
   ## Current Progress
   - ✅ Step 1: Complete
   - 🔄 Step 2: In progress
   - ⬜ Step 3: Not started
   ---END---

6. VERIFY - Verify that something works correctly
   FORMAT:
   ACTION: VERIFY
   WHAT: The Python script runs without errors
   HOW: Run: python script.py
   ---END---

WORKFLOW (VERY IMPORTANT):
1. PLAN FIRST:
   - Understand the full task
   - Break it into clear steps
   - Identify potential issues
   - Create todo.md to track progress

2. EXECUTE WITH VERIFICATION:
   - Do one step at a time
   - After each step, VERIFY it worked
   - If something fails, LEARN why and try again
   - Update todo.md after each step

3. TEST YOUR WORK:
   - Always test code before marking complete
   - Run with different inputs if applicable
   - Check edge cases

4. LEARN FROM MISTAKES:
   - If something fails, analyze WHY
   - Don't repeat the same error
   - Adjust your approach based on failures

5. SELF-REFLECT:
   - After completing task, reflect on what worked/didn't work
   - Identify improvements for future tasks

EXAMPLE WORKFLOW:
Task: "Create a Python calculator and test it"

Step 1 - PLAN:
"Let me create a plan for this task:
1. Create calculator.py with basic operations
2. Create test cases
3. Run tests and verify
4. Fix any bugs found
5. Document usage"

ACTION: UPDATE_TODO
CONTENT:
## Calculator Task
- ⬜ Create calculator.py
- ⬜ Create tests
- ⬜ Run tests
- ⬜ Fix bugs
- ⬜ Document
---END---

Step 2 - EXECUTE & VERIFY:
"Creating calculator.py..."

ACTION: CREATE_FILE
PATH: /workspace/calculator.py
CONTENT:
def add(a, b): return a + b
def subtract(a, b): return a - b
---END---

"Now let me verify the file was created..."

ACTION: VERIFY
WHAT: calculator.py exists and has correct content
HOW: cat /workspace/calculator.py
---END---

Step 3 - TEST:
ACTION: CREATE_FILE
PATH: /workspace/test_calculator.py
CONTENT:
from calculator import add, subtract
assert add(2, 3) == 5
assert subtract(5, 3) == 2
print("All tests passed!")
---END---

ACTION: EXECUTE
COMMAND: python /workspace/test_calculator.py
---END---

Step 4 - LEARN (if test fails):
"The test failed because [reason]. I learned that I need to [correction].
Let me fix this..."

[Fix and re-test]

Step 5 - UPDATE PROGRESS:
ACTION: UPDATE_TODO
CONTENT:
## Calculator Task
- ✅ Create calculator.py
- ✅ Create tests
- ✅ Run tests
- ⬜ Document
---END---

Step 6 - COMPLETE:
"TASK_COMPLETED: Created and tested calculator successfully.

REFLECTION:
- What worked: Writing tests before manual testing caught bugs early
- What I learned: Always verify file creation before proceeding
- Improvement for next time: Could add more edge case tests"

CRITICAL RULES:
1. ALWAYS plan before executing
2. ALWAYS verify each step
3. ALWAYS test your code
4. ALWAYS learn from errors (don't hide them!)
5. ALWAYS update todo.md to track progress
6. ALWAYS reflect at the end

When you complete the task, respond with:
TASK_COMPLETED: [summary]

REFLECTION:
- What worked: [...]
- What I learned: [...]
- Mistakes made: [...]
- Improvements: [...]
"""

    async def execute_task(
        self,
        task_description: str,
        task_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a task with planning, testing, and learning.

        Phase 1: PLAN - Create strategic plan
        Phase 2: EXECUTE - Do-try-test loop
        Phase 3: LEARN - Reflect and improve
        """
        try:
            logger.info(f"🚀 Starting enhanced task execution: {task_id}")

            # Initialize Daytona sandbox
            if not self.daytona.sandbox:
                yield {"type": "status", "message": "⚙️  Initializing secure sandbox..."}
                await self.daytona.initialize()
                yield {"type": "status", "message": "✅ Sandbox ready"}

            # PHASE 1: PLANNING
            yield {"type": "phase", "phase": "planning", "message": "📋 Creating strategic plan..."}

            plan_result = await self.planner.create_plan(
                task_description,
                context={
                    "previous_attempts": len(self.error_memory),
                    "learnings": self.session_learnings
                }
            )

            if plan_result["success"]:
                plan = plan_result["plan"]
                yield {
                    "type": "plan_created",
                    "plan": plan,
                    "plan_text": plan_result["plan_text"]
                }

                # Create todo.md in sandbox
                todo_content = self._generate_todo_md(plan, task_description)
                await self.daytona.write_file("/workspace/todo.md", todo_content)
                yield {"type": "status", "message": "✅ Plan created and saved to todo.md"}
            else:
                yield {"type": "warning", "message": "⚠️  Planning failed, proceeding with direct execution"}
                plan = None

            # PHASE 2: EXECUTION with Do-Try-Test Loop
            yield {"type": "phase", "phase": "execution", "message": "🔨 Executing plan..."}

            # Initialize conversation with enhanced prompt
            self.conversation_history = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"""Task: {task_description}

Your plan has been created and saved to /workspace/todo.md.

IMPORTANT: Follow the workflow:
1. Read todo.md to see your plan
2. Execute one step at a time
3. Verify each step works
4. Update todo.md as you progress
5. Learn from any failures
6. Test thoroughly
7. Reflect at the end

Begin execution now!"""}
            ]

            # Add previous learnings to context
            if self.session_learnings:
                learnings_str = "\n".join([f"- {learning}" for learning in self.session_learnings])
                self.conversation_history.append({
                    "role": "system",
                    "content": f"Previous learnings from this session:\n{learnings_str}"
                })

            max_iterations = settings.AGENT_MAX_ITERATIONS
            iteration = 0
            verification_count = 0
            test_count = 0

            while iteration < max_iterations:
                iteration += 1

                yield {
                    "type": "iteration",
                    "iteration": iteration,
                    "max_iterations": max_iterations
                }

                # Get AI response
                try:
                    response = await acompletion(
                        model=f"groq/{settings.LLM_MODEL}",
                        messages=self.conversation_history,
                        api_key=settings.LLM_API_KEY,
                        api_base=settings.LLM_BASE_URL,
                        temperature=settings.LLM_TEMPERATURE,
                        max_tokens=settings.LLM_MAX_TOKENS,
                    )

                    ai_message = response.choices[0].message.content

                    # Add to conversation history (APPEND-ONLY for KV-cache)
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": ai_message
                    })

                    # Send AI message to user
                    yield {
                        "type": "agent_message",
                        "message": ai_message,
                        "iteration": iteration
                    }

                    # Check for completion
                    if "TASK_COMPLETED" in ai_message:
                        # Extract reflection
                        reflection = self._extract_reflection(ai_message)
                        if reflection:
                            self.session_learnings.extend(reflection.get("learnings", []))

                        yield {
                            "type": "task_completed",
                            "task_id": task_id,
                            "message": ai_message,
                            "reflection": reflection,
                            "iterations": iteration,
                            "verifications": verification_count,
                            "tests": test_count
                        }
                        break

                    # Parse and execute actions
                    actions = self._parse_actions(ai_message)

                    if not actions:
                        # No actions, ask AI to continue
                        self.conversation_history.append({
                            "role": "user",
                            "content": "Please continue with the next step. Remember to use ACTION: format."
                        })
                        continue

                    # Execute actions
                    for action in actions:
                        yield {
                            "type": "action_executing",
                            "action": action["type"],
                            "iteration": iteration
                        }

                        result = await self._execute_action(action)

                        # Track verifications and tests
                        if action["type"] == "VERIFY":
                            verification_count += 1
                        if "test" in action.get("command", "").lower():
                            test_count += 1

                        yield {
                            "type": "action_result",
                            "action": action["type"],
                            "result": result,
                            "iteration": iteration
                        }

                        # Provide feedback to agent (CRITICAL for learning)
                        feedback = self._generate_feedback(action, result)
                        self.conversation_history.append({
                            "role": "user",
                            "content": feedback
                        })

                        # If action failed, record error for learning
                        if not result.get("success"):
                            self.error_memory.append({
                                "action": action,
                                "error": result.get("error"),
                                "iteration": iteration,
                                "task": task_description
                            })

                except Exception as e:
                    logger.error(f"❌ Error in iteration {iteration}: {e}")
                    yield {
                        "type": "error",
                        "error": str(e),
                        "iteration": iteration
                    }
                    break

            # PHASE 3: REFLECTION & LEARNING
            if iteration >= max_iterations:
                yield {
                    "type": "task_timeout",
                    "task_id": task_id,
                    "message": f"Task reached maximum iterations ({max_iterations})",
                    "iterations": iteration
                }

                # Still try to extract learnings
                self._extract_learnings_from_errors()

        except Exception as e:
            logger.error(f"❌ Task execution error: {e}")
            yield {
                "type": "task_failed",
                "task_id": task_id,
                "error": str(e)
            }

    def _generate_todo_md(self, plan: Dict[str, Any], task: str) -> str:
        """Generate todo.md content from plan (Manus AI pattern)."""
        content = f"""# Task: {task}

## Progress Tracker

"""
        if plan and plan.get("steps"):
            for step in plan["steps"]:
                content += f"- ⬜ Step {step['step_number']}: {step['description']}\n"
        else:
            content += "- ⬜ Complete the task\n"

        content += f"""

## Instructions
1. Read this file before each step
2. Update status as you progress (⬜ → 🔄 → ✅)
3. Add notes about issues or learnings
4. Keep this file updated!

## Notes
[Add notes about challenges, solutions, etc.]
"""
        return content

    def _generate_feedback(self, action: Dict[str, Any], result: Dict[str, Any]) -> str:
        """Generate detailed feedback for the agent (enables learning)."""
        action_type = action["type"]

        if result.get("success"):
            # Positive feedback
            feedback = f"✅ {action_type} succeeded.\n"

            if action_type == "EXECUTE":
                if result.get("stdout"):
                    feedback += f"Output:\n{result['stdout']}\n"
                if result.get("stderr"):
                    feedback += f"Warnings:\n{result['stderr']}\n"
                feedback += f"Exit code: {result.get('exit_code', 0)}\n"

            elif action_type == "READ_FILE":
                content = result.get("content", "")
                if len(content) > 500:
                    feedback += f"File content (first 500 chars):\n{content[:500]}...\n"
                else:
                    feedback += f"File content:\n{content}\n"

            elif action_type == "CREATE_FILE":
                feedback += f"File created at: {result.get('path')}\n"

            elif action_type == "LIST_FILES":
                files = result.get("files", [])
                feedback += f"Found {len(files)} files/directories:\n{json.dumps(files, indent=2)}\n"

            feedback += "\nWhat's the next step?"

        else:
            # Error feedback with learning guidance
            feedback = f"❌ {action_type} failed.\n"
            feedback += f"Error: {result.get('error', 'Unknown error')}\n\n"
            feedback += "IMPORTANT: Learn from this error!\n"
            feedback += "- Why did it fail?\n"
            feedback += "- What should you do differently?\n"
            feedback += "- How can you fix this?\n\n"
            feedback += "Try again with a corrected approach. Don't repeat the same mistake!"

        return feedback

    def _parse_actions(self, message: str) -> List[Dict[str, Any]]:
        """Parse actions from AI message (enhanced with UPDATE_TODO and VERIFY)."""
        actions = []

        # Find all ACTION blocks
        action_pattern = r"ACTION:\s*(\w+)(.*?)(?=ACTION:|---END---|$)"
        matches = re.finditer(action_pattern, message, re.DOTALL | re.IGNORECASE)

        for match in matches:
            action_type = match.group(1).strip().upper()
            action_content = match.group(2).strip()

            if action_type == "CREATE_FILE":
                path_match = re.search(r"PATH:\s*(.+?)(?:\n|$)", action_content)
                content_match = re.search(r"CONTENT:\s*\n(.*)", action_content, re.DOTALL)

                if path_match and content_match:
                    actions.append({
                        "type": "CREATE_FILE",
                        "path": path_match.group(1).strip(),
                        "content": content_match.group(1).strip()
                    })

            elif action_type == "READ_FILE":
                path_match = re.search(r"PATH:\s*(.+?)(?:\n|$)", action_content)

                if path_match:
                    actions.append({
                        "type": "READ_FILE",
                        "path": path_match.group(1).strip()
                    })

            elif action_type == "EXECUTE":
                command_match = re.search(r"COMMAND:\s*(.+?)(?:\n|$)", action_content)

                if command_match:
                    actions.append({
                        "type": "EXECUTE",
                        "command": command_match.group(1).strip()
                    })

            elif action_type == "LIST_FILES":
                path_match = re.search(r"PATH:\s*(.+?)(?:\n|$)", action_content)

                actions.append({
                    "type": "LIST_FILES",
                    "path": path_match.group(1).strip() if path_match else "/workspace"
                })

            elif action_type == "UPDATE_TODO":
                content_match = re.search(r"CONTENT:\s*\n(.*)", action_content, re.DOTALL)

                if content_match:
                    actions.append({
                        "type": "UPDATE_TODO",
                        "content": content_match.group(1).strip()
                    })

            elif action_type == "VERIFY":
                what_match = re.search(r"WHAT:\s*(.+?)(?:\n|$)", action_content)
                how_match = re.search(r"HOW:\s*(.+?)(?:\n|$)", action_content)

                if what_match and how_match:
                    actions.append({
                        "type": "VERIFY",
                        "what": what_match.group(1).strip(),
                        "how": how_match.group(1).strip()
                    })

        return actions

    async def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action."""
        action_type = action["type"]

        logger.info(f"Executing action: {action_type}")

        try:
            if action_type == "CREATE_FILE":
                result = await self.daytona.write_file(
                    action["path"],
                    action["content"]
                )
                return {
                    "action": "CREATE_FILE",
                    "path": action["path"],
                    "success": result["success"],
                    "message": result.get("message", "File created")
                }

            elif action_type == "READ_FILE":
                result = await self.daytona.read_file(action["path"])
                return {
                    "action": "READ_FILE",
                    "path": action["path"],
                    "success": result["success"],
                    "content": result.get("content", "")
                }

            elif action_type == "EXECUTE":
                result = await self.daytona.execute_command(action["command"])
                return {
                    "action": "EXECUTE",
                    "command": action["command"],
                    "success": result["success"],
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                    "exit_code": result.get("exit_code", 0)
                }

            elif action_type == "LIST_FILES":
                result = await self.daytona.list_files(action["path"])
                return {
                    "action": "LIST_FILES",
                    "path": action["path"],
                    "success": result["success"],
                    "files": result.get("files", [])
                }

            elif action_type == "UPDATE_TODO":
                # Update todo.md file
                result = await self.daytona.write_file(
                    "/workspace/todo.md",
                    action["content"]
                )
                return {
                    "action": "UPDATE_TODO",
                    "success": result["success"],
                    "message": "Updated todo.md"
                }

            elif action_type == "VERIFY":
                # Execute verification command
                result = await self.daytona.execute_command(action["how"])
                return {
                    "action": "VERIFY",
                    "what": action["what"],
                    "success": result["success"] and result.get("exit_code", 0) == 0,
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                    "verification_passed": result.get("exit_code", 0) == 0
                }

            else:
                return {
                    "action": action_type,
                    "success": False,
                    "error": f"Unknown action type: {action_type}"
                }

        except Exception as e:
            logger.error(f"Action execution error: {e}")
            return {
                "action": action_type,
                "success": False,
                "error": str(e)
            }

    def _extract_reflection(self, message: str) -> Dict[str, Any]:
        """Extract reflection from completion message."""
        reflection = {
            "what_worked": [],
            "learnings": [],
            "mistakes": [],
            "improvements": []
        }

        # Look for REFLECTION section
        if "REFLECTION:" in message:
            reflection_text = message.split("REFLECTION:")[1]

            # Parse reflection items
            if "what worked:" in reflection_text.lower():
                worked = re.search(r"what worked:(.*?)(?=what i learned:|mistakes made:|improvements:|$)", reflection_text, re.IGNORECASE | re.DOTALL)
                if worked:
                    reflection["what_worked"].append(worked.group(1).strip())

            if "what i learned:" in reflection_text.lower():
                learned = re.search(r"what i learned:(.*?)(?=what worked:|mistakes made:|improvements:|$)", reflection_text, re.IGNORECASE | re.DOTALL)
                if learned:
                    reflection["learnings"].append(learned.group(1).strip())

            if "mistakes made:" in reflection_text.lower():
                mistakes = re.search(r"mistakes made:(.*?)(?=what worked:|what i learned:|improvements:|$)", reflection_text, re.IGNORECASE | re.DOTALL)
                if mistakes:
                    reflection["mistakes"].append(mistakes.group(1).strip())

            if "improvements:" in reflection_text.lower():
                improvements = re.search(r"improvements:(.*?)(?=what worked:|what i learned:|mistakes made:|$)", reflection_text, re.IGNORECASE | re.DOTALL)
                if improvements:
                    reflection["improvements"].append(improvements.group(1).strip())

        return reflection

    def _extract_learnings_from_errors(self):
        """Extract learnings from error memory."""
        if self.error_memory:
            # Analyze common error patterns
            for error in self.error_memory[-5:]:  # Last 5 errors
                learning = f"Avoid: {error.get('error')} when doing {error.get('action', {}).get('type')}"
                if learning not in self.session_learnings:
                    self.session_learnings.append(learning)


# Global instance
enhanced_agent_service = EnhancedAgentService()
