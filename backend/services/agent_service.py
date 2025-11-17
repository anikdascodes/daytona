"""
AI Agent Service - Manages AI agent that executes development tasks.
"""
import json
import re
from typing import AsyncGenerator, Dict, Any, List
from litellm import acompletion
from utils.logger import logger
from config import settings
from services.daytona_service import daytona_service


class AgentService:
    """AI Agent that can execute development tasks autonomously."""

    def __init__(self):
        """Initialize Agent service."""
        self.daytona = daytona_service
        self.conversation_history: List[Dict[str, str]] = []
        logger.info("AgentService initialized")

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI agent."""
        return """You are an expert software developer AI agent with full control over a development workspace.

You can perform these actions:
1. CREATE_FILE: Create or write a file
2. READ_FILE: Read a file's contents
3. EXECUTE: Run shell commands
4. LIST_FILES: List files in a directory

When the user gives you a task, think step by step and use these actions to complete it.

IMPORTANT RULES:
- Always respond with your reasoning first, then the action
- Use actions by specifying them in this format:
  ACTION: <action_name>
  <action_parameters>

For example:
ACTION: CREATE_FILE
PATH: /workspace/hello.py
CONTENT:
print("Hello World!")
---END---

ACTION: EXECUTE
COMMAND: python /workspace/hello.py
---END---

After each action, I'll give you the result, and you can continue with the next step.
When the task is complete, respond with "TASK_COMPLETED" followed by a summary."""

    async def execute_task(
        self,
        task_description: str,
        task_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a task with the AI agent.
        Yields events as they occur.
        """
        try:
            logger.info(f"Starting task {task_id}: {task_description}")

            # Send initial status
            yield {
                "type": "task_started",
                "task_id": task_id,
                "message": f"🤖 Starting task: {task_description}"
            }

            # Initialize conversation
            self.conversation_history = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"Task: {task_description}"}
            ]

            max_iterations = settings.AGENT_MAX_ITERATIONS
            iteration = 0

            while iteration < max_iterations:
                iteration += 1

                yield {
                    "type": "agent_thinking",
                    "task_id": task_id,
                    "message": f"🧠 Thinking... (iteration {iteration}/{max_iterations})"
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

                    logger.info(f"AI Response: {ai_message[:200]}...")

                    # Add to conversation history
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": ai_message
                    })

                    # Send AI message to user
                    yield {
                        "type": "agent_message",
                        "task_id": task_id,
                        "message": ai_message
                    }

                    # Check if task is completed
                    if "TASK_COMPLETED" in ai_message:
                        yield {
                            "type": "task_completed",
                            "task_id": task_id,
                            "message": "✅ Task completed successfully!"
                        }
                        break

                    # Parse and execute actions
                    actions = self._parse_actions(ai_message)

                    if not actions:
                        # No actions found, ask AI to continue
                        self.conversation_history.append({
                            "role": "user",
                            "content": "Please specify an action to perform, or respond with TASK_COMPLETED if done."
                        })
                        continue

                    # Execute each action
                    for action in actions:
                        result = await self._execute_action(action)

                        yield {
                            "type": "action_executed",
                            "task_id": task_id,
                            "action": action["type"],
                            "result": result
                        }

                        # Add result to conversation
                        self.conversation_history.append({
                            "role": "user",
                            "content": f"Action result:\n{json.dumps(result, indent=2)}"
                        })

                except Exception as e:
                    logger.error(f"Error in agent iteration: {e}")
                    yield {
                        "type": "agent_error",
                        "task_id": task_id,
                        "error": str(e)
                    }

                    # Add error to conversation
                    self.conversation_history.append({
                        "role": "user",
                        "content": f"Error occurred: {str(e)}. Please try a different approach."
                    })

            if iteration >= max_iterations:
                yield {
                    "type": "task_failed",
                    "task_id": task_id,
                    "message": f"⚠️ Task stopped: reached maximum iterations ({max_iterations})"
                }

        except Exception as e:
            logger.error(f"Task execution error: {e}")
            yield {
                "type": "task_failed",
                "task_id": task_id,
                "error": str(e)
            }

    def _parse_actions(self, message: str) -> List[Dict[str, Any]]:
        """Parse actions from AI message."""
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
                    "content": result.get("content", "")[:1000]  # Limit content length
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


# Global instance
agent_service = AgentService()
