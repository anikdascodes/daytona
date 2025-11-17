"""
Planner Service - Task decomposition and strategic planning.
Inspired by Manus AI's Planner Agent.
"""
from typing import List, Dict, Any
from litellm import acompletion
from config import settings
from utils.logger import logger


class PlannerService:
    """Service for strategic task planning and decomposition."""

    def __init__(self):
        """Initialize planner service."""
        logger.info("PlannerService initialized")

    def _get_planner_prompt(self) -> str:
        """Get system prompt for planner agent."""
        return """You are a strategic task planner. Your role is to analyze complex tasks and break them down into clear, actionable steps.

CAPABILITIES:
- Analyze task requirements and dependencies
- Decompose complex goals into sub-tasks
- Identify potential challenges and solutions
- Create structured execution plans

PLANNING FORMAT:
Create a detailed plan in this format:

## Task Analysis
[Analyze the task requirements and scope]

## Success Criteria
[Define clear success metrics]

## Execution Plan
1. [Step 1 - Clear, actionable task]
   - Expected output: [What should result]
   - Verification: [How to verify success]
   - Risk: [Potential issues]

2. [Step 2...]
   ...

## Dependencies
[List any dependencies between steps]

## Potential Challenges
[Identify risks and mitigation strategies]

IMPORTANT:
- Be specific and actionable
- Consider edge cases
- Include verification steps
- Think about what could go wrong
- Each step should be testable
"""

    async def create_plan(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a strategic plan for the given task.

        Args:
            task_description: The task to plan
            context: Additional context (previous attempts, constraints, etc.)

        Returns:
            Plan dict with steps, success_criteria, challenges
        """
        try:
            logger.info(f"Creating plan for task: {task_description[:100]}...")

            # Build planner prompt
            messages = [
                {"role": "system", "content": self._get_planner_prompt()},
                {"role": "user", "content": f"Task: {task_description}"}
            ]

            # Add context if provided
            if context:
                context_str = f"\n\nAdditional Context:\n"
                if context.get("previous_attempts"):
                    context_str += f"- Previous attempts: {context['previous_attempts']}\n"
                if context.get("constraints"):
                    context_str += f"- Constraints: {context['constraints']}\n"
                if context.get("resources"):
                    context_str += f"- Available resources: {context['resources']}\n"

                messages[-1]["content"] += context_str

            # Get plan from LLM
            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=messages,
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.3,  # Lower temperature for more focused planning
                max_tokens=4000,
            )

            plan_text = response.choices[0].message.content

            # Parse plan into structured format
            plan = self._parse_plan(plan_text)
            plan["raw_plan"] = plan_text

            logger.info(f"✅ Created plan with {len(plan.get('steps', []))} steps")

            return {
                "success": True,
                "plan": plan,
                "plan_text": plan_text
            }

        except Exception as e:
            logger.error(f"❌ Failed to create plan: {e}")
            return {
                "success": False,
                "error": str(e),
                "plan": None
            }

    def _parse_plan(self, plan_text: str) -> Dict[str, Any]:
        """Parse plan text into structured format."""
        # Simple parsing - extracts numbered steps
        steps = []
        lines = plan_text.split('\n')

        current_step = None
        for line in lines:
            line = line.strip()

            # Check if this is a numbered step (e.g., "1. ", "2. ")
            if line and line[0].isdigit() and '. ' in line[:5]:
                if current_step:
                    steps.append(current_step)

                # Extract step description
                step_text = line.split('. ', 1)[1] if '. ' in line else line
                current_step = {
                    "step_number": len(steps) + 1,
                    "description": step_text,
                    "status": "pending",
                    "verification": None,
                    "risk": None
                }

            elif current_step:
                # Look for verification and risk info
                if "verification:" in line.lower():
                    current_step["verification"] = line.split(':', 1)[1].strip()
                elif "risk:" in line.lower():
                    current_step["risk"] = line.split(':', 1)[1].strip()

        # Add last step
        if current_step:
            steps.append(current_step)

        return {
            "steps": steps,
            "total_steps": len(steps),
            "completed_steps": 0
        }

    async def refine_plan(self, original_plan: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """
        Refine a plan based on execution feedback.

        Args:
            original_plan: The original plan
            feedback: Feedback from execution (errors, issues, learnings)

        Returns:
            Refined plan
        """
        try:
            logger.info("Refining plan based on feedback...")

            messages = [
                {"role": "system", "content": self._get_planner_prompt()},
                {"role": "user", "content": f"""Original Plan:
{original_plan.get('raw_plan', 'No raw plan available')}

Execution Feedback:
{feedback}

Please refine the plan based on this feedback. Focus on:
1. Addressing issues that were encountered
2. Adding missing steps that were discovered
3. Improving verification methods
4. Adjusting for constraints found during execution
"""}
            ]

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=messages,
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.3,
                max_tokens=4000,
            )

            refined_plan_text = response.choices[0].message.content
            refined_plan = self._parse_plan(refined_plan_text)
            refined_plan["raw_plan"] = refined_plan_text
            refined_plan["refinement_reason"] = feedback

            logger.info("✅ Plan refined successfully")

            return {
                "success": True,
                "plan": refined_plan,
                "plan_text": refined_plan_text
            }

        except Exception as e:
            logger.error(f"❌ Failed to refine plan: {e}")
            return {
                "success": False,
                "error": str(e),
                "plan": original_plan  # Return original plan if refinement fails
            }


# Global instance
planner_service = PlannerService()
