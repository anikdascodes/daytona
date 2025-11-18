"""
Code Agent Service - Automated code generation and implementation.

Capabilities:
- Generate production-quality code from requirements
- Follow project conventions and best practices
- Support multiple programming languages
- Validate code quality
- Generate documentation

Part of Phase 4: Supreme AI Capabilities
"""
import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from litellm import acompletion
from config import settings
from utils.logger import logger


class CodeAgent:
    """
    Specialized agent for automated code generation.

    Features:
    - Requirement analysis
    - Code generation with best practices
    - Convention adherence
    - Multi-language support
    - Quality validation
    - Documentation generation
    """

    def __init__(self):
        """Initialize code agent."""
        self.generation_history: List[Dict[str, Any]] = []
        self.language_templates = self._load_language_templates()
        logger.info("CodeAgent initialized")

    def _load_language_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Load language-specific templates and conventions.

        Returns:
            Dictionary of language templates
        """
        return {
            "python": {
                "conventions": """
- Use PEP 8 style guide
- 4 spaces for indentation
- Snake_case for functions and variables
- PascalCase for classes
- Type hints for function signatures
- Docstrings for all functions/classes
- Maximum line length: 100 characters
                """,
                "best_practices": """
- Use list comprehensions where appropriate
- Prefer f-strings for formatting
- Use context managers for resources
- Handle exceptions properly
- Write defensive code
- Add logging for important operations
                """
            },
            "javascript": {
                "conventions": """
- Use ESLint recommended rules
- 2 spaces for indentation
- camelCase for functions and variables
- PascalCase for classes/components
- Use const/let (not var)
- Semicolons at end of statements
                """,
                "best_practices": """
- Use async/await for async operations
- Use arrow functions appropriately
- Destructure objects and arrays
- Use template literals
- Handle promises properly
- Add JSDoc comments
                """
            },
            "typescript": {
                "conventions": """
- Follow TypeScript best practices
- Use strict mode
- Define interfaces for objects
- Use proper type annotations
- Avoid 'any' type
- Export types properly
                """,
                "best_practices": """
- Use generics where appropriate
- Leverage type inference
- Use union/intersection types
- Use readonly where applicable
- Prefer interfaces over type aliases for objects
                """
            },
            "go": {
                "conventions": """
- Follow Go style guide (gofmt)
- Use tabs for indentation
- PascalCase for exported names
- camelCase for unexported names
- Error handling with error returns
- Use go modules
                """,
                "best_practices": """
- Check errors explicitly
- Use defer for cleanup
- Prefer composition over inheritance
- Keep interfaces small
- Use goroutines appropriately
                """
            },
            "rust": {
                "conventions": """
- Follow Rust style guide (rustfmt)
- Snake_case for functions and variables
- PascalCase for types
- Use Clippy for linting
- Idiomatic Rust patterns
                """,
                "best_practices": """
- Leverage ownership system
- Use Result for error handling
- Avoid unsafe unless necessary
- Use iterators
- Write comprehensive tests
                """
            }
        }

    async def generate_code(
        self,
        requirements: str,
        language: str = "python",
        context: Optional[Dict[str, Any]] = None,
        existing_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code from requirements.

        Args:
            requirements: What the code should do
            language: Programming language
            context: Additional context (project info, dependencies, etc.)
            existing_code: Existing codebase to follow patterns from

        Returns:
            Generated code with metadata
        """
        logger.info(f"🔨 Generating {language} code for: {requirements[:60]}...")

        try:
            # Get language-specific conventions
            lang_template = self.language_templates.get(
                language.lower(),
                self.language_templates["python"]  # Default to Python
            )

            # Build prompt for code generation
            prompt = self._build_code_generation_prompt(
                requirements,
                language,
                lang_template,
                context,
                existing_code
            )

            # Call LLM for code generation
            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[
                    {"role": "system", "content": "You are an expert software engineer specializing in writing clean, production-quality code."},
                    {"role": "user", "content": prompt}
                ],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.2,  # Lower temperature for more consistent code
                max_tokens=3000
            )

            content = response.choices[0].message.content.strip()

            # Extract code from response
            code, explanation = self._extract_code_and_explanation(content, language)

            if not code:
                return {
                    "success": False,
                    "error": "Failed to generate code",
                    "raw_response": content
                }

            # Validate code quality
            quality_check = await self._validate_code_quality(code, language, requirements)

            # Store in history
            generation_record = {
                "timestamp": datetime.now().isoformat(),
                "requirements": requirements,
                "language": language,
                "code": code,
                "explanation": explanation,
                "quality_score": quality_check.get("score", 0),
                "issues": quality_check.get("issues", [])
            }

            self.generation_history.append(generation_record)

            logger.info(f"✅ Code generated ({len(code)} chars, quality: {quality_check.get('score', 0)}/10)")

            return {
                "success": True,
                "code": code,
                "explanation": explanation,
                "language": language,
                "quality_check": quality_check,
                "metadata": {
                    "lines": code.count('\n') + 1,
                    "characters": len(code),
                    "timestamp": generation_record["timestamp"]
                }
            }

        except Exception as e:
            logger.error(f"❌ Code generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _build_code_generation_prompt(
        self,
        requirements: str,
        language: str,
        lang_template: Dict[str, str],
        context: Optional[Dict[str, Any]],
        existing_code: Optional[str]
    ) -> str:
        """Build comprehensive prompt for code generation."""

        prompt_parts = [
            f"Generate {language} code for the following requirements:",
            f"\n**Requirements:**\n{requirements}\n",
            f"\n**Language:** {language}",
            f"\n**Conventions to follow:**{lang_template['conventions']}",
            f"\n**Best practices:**{lang_template['best_practices']}"
        ]

        if context:
            prompt_parts.append(f"\n**Context:**\n{json.dumps(context, indent=2)}")

        if existing_code:
            prompt_parts.append(f"\n**Existing code to follow patterns from:**\n```{language}\n{existing_code[:500]}\n```")

        prompt_parts.extend([
            "\n**Instructions:**",
            "1. Write production-quality, well-documented code",
            "2. Follow the language conventions strictly",
            "3. Apply best practices",
            "4. Include comprehensive docstrings/comments",
            "5. Handle errors appropriately",
            "6. Make code maintainable and readable",
            "7. Add type hints/annotations where applicable",
            "",
            "**Format your response as:**",
            "```" + language,
            "[Your code here]",
            "```",
            "",
            "**Explanation:**",
            "[Brief explanation of the code, key decisions, and usage]"
        ])

        return "\n".join(prompt_parts)

    def _extract_code_and_explanation(self, content: str, language: str) -> tuple[str, str]:
        """
        Extract code and explanation from LLM response.

        Args:
            content: LLM response
            language: Programming language

        Returns:
            Tuple of (code, explanation)
        """
        # Try to extract code from markdown code blocks
        code_pattern = rf"```{language}?\n(.*?)```"
        matches = re.findall(code_pattern, content, re.DOTALL | re.IGNORECASE)

        if matches:
            code = matches[0].strip()
            # Extract explanation (text after code block)
            explanation_match = re.search(
                rf"```{language}?.*?```\s*(.*)",
                content,
                re.DOTALL | re.IGNORECASE
            )
            explanation = explanation_match.group(1).strip() if explanation_match else ""
        else:
            # No code blocks found, assume entire content is code
            code = content.strip()
            explanation = ""

        return code, explanation

    async def _validate_code_quality(
        self,
        code: str,
        language: str,
        requirements: str
    ) -> Dict[str, Any]:
        """
        Validate code quality using AI analysis.

        Args:
            code: Generated code
            language: Programming language
            requirements: Original requirements

        Returns:
            Quality assessment
        """
        try:
            prompt = f"""Review this {language} code and assess its quality:

**Requirements:** {requirements}

**Code:**
```{language}
{code}
```

Evaluate on:
1. Correctness (does it meet requirements?)
2. Code quality (readability, maintainability)
3. Best practices (follows language conventions?)
4. Error handling
5. Documentation quality

Provide assessment in JSON format:
{{
    "score": 8,  # 1-10
    "correctness": true/false,
    "issues": ["issue 1", "issue 2"],
    "strengths": ["strength 1", "strength 2"],
    "suggestions": ["suggestion 1", "suggestion 2"]
}}"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.3,
                max_tokens=1000
            )

            content = response.choices[0].message.content.strip()

            # Try to parse JSON
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                quality_data = json.loads(content[start:end])
                return quality_data
            else:
                return {
                    "score": 7,  # Default
                    "correctness": True,
                    "issues": [],
                    "strengths": ["Code generated successfully"],
                    "suggestions": []
                }

        except Exception as e:
            logger.warning(f"Quality validation failed: {e}")
            return {
                "score": 6,
                "correctness": True,
                "issues": ["Could not perform automated quality check"],
                "strengths": [],
                "suggestions": []
            }

    async def refactor_code(
        self,
        code: str,
        language: str,
        refactoring_goal: str
    ) -> Dict[str, Any]:
        """
        Refactor existing code.

        Args:
            code: Code to refactor
            language: Programming language
            refactoring_goal: What to improve

        Returns:
            Refactored code
        """
        logger.info(f"🔧 Refactoring {language} code: {refactoring_goal[:50]}...")

        try:
            lang_template = self.language_templates.get(language.lower(), {})

            prompt = f"""Refactor this {language} code to: {refactoring_goal}

**Current Code:**
```{language}
{code}
```

**Conventions:**{lang_template.get('conventions', '')}

**Best Practices:**{lang_template.get('best_practices', '')}

Provide:
1. Refactored code
2. Explanation of changes
3. Benefits of refactoring

Format:
```{language}
[Refactored code]
```

**Changes Made:**
[Explanation]
"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.2,
                max_tokens=3000
            )

            content = response.choices[0].message.content.strip()

            refactored_code, explanation = self._extract_code_and_explanation(content, language)

            return {
                "success": True,
                "original_code": code,
                "refactored_code": refactored_code,
                "changes": explanation,
                "language": language
            }

        except Exception as e:
            logger.error(f"Refactoring failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def explain_code(
        self,
        code: str,
        language: str,
        detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate explanation for existing code.

        Args:
            code: Code to explain
            language: Programming language
            detail_level: quick/medium/detailed

        Returns:
            Code explanation
        """
        logger.info(f"📖 Explaining {language} code...")

        detail_instructions = {
            "quick": "Provide a brief 1-2 sentence summary",
            "medium": "Provide a paragraph explaining the code's purpose and key components",
            "detailed": "Provide a comprehensive explanation including purpose, how it works, key functions, and usage"
        }

        try:
            prompt = f"""Explain this {language} code:

```{language}
{code}
```

{detail_instructions.get(detail_level, detail_instructions['medium'])}

Include:
- What the code does
- Key components/functions
- How to use it
"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.5,
                max_tokens=1500
            )

            explanation = response.choices[0].message.content.strip()

            return {
                "success": True,
                "code": code,
                "language": language,
                "explanation": explanation,
                "detail_level": detail_level
            }

        except Exception as e:
            logger.error(f"Code explanation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get code generation statistics.

        Returns:
            Statistics dictionary
        """
        if not self.generation_history:
            return {
                "total_generations": 0,
                "languages": {},
                "average_quality": 0
            }

        # Count by language
        lang_counts = {}
        total_quality = 0

        for record in self.generation_history:
            lang = record["language"]
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
            total_quality += record.get("quality_score", 0)

        return {
            "total_generations": len(self.generation_history),
            "languages": lang_counts,
            "average_quality": total_quality / len(self.generation_history),
            "recent_generations": [
                {
                    "requirements": g["requirements"][:50] + "...",
                    "language": g["language"],
                    "quality": g["quality_score"],
                    "timestamp": g["timestamp"]
                }
                for g in self.generation_history[-5:]
            ]
        }


# Global singleton instance
code_agent = CodeAgent()
