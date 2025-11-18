"""
Test Agent Service - Automated test generation and execution.

Capabilities:
- Generate unit tests automatically
- Create integration tests
- Write end-to-end tests
- Execute tests and analyze results
- Generate test coverage reports
- Identify edge cases

Part of Phase 4: Supreme AI Capabilities
"""
import re
import json
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
from litellm import acompletion
from config import settings
from utils.logger import logger


class TestAgent:
    """
    Specialized agent for automated test generation and execution.

    Features:
    - Unit test generation
    - Integration test creation
    - E2E test writing
    - Test execution
    - Coverage analysis
    - Edge case identification
    """

    def __init__(self):
        """Initialize test agent."""
        self.test_history: List[Dict[str, Any]] = []
        self.test_frameworks = self._load_test_frameworks()
        logger.info("TestAgent initialized")

    def _load_test_frameworks(self) -> Dict[str, Dict[str, str]]:
        """
        Load test framework configurations for different languages.

        Returns:
            Dictionary of test framework configurations
        """
        return {
            "python": {
                "unit": "pytest",
                "integration": "pytest",
                "e2e": "pytest + selenium",
                "coverage": "pytest-cov",
                "patterns": """
- Use pytest fixtures for setup/teardown
- Use parametrize for multiple test cases
- Mock external dependencies
- Use assert statements
- Test one behavior per test
- Clear test names (test_<behavior>_<condition>_<expected>)
                """
            },
            "javascript": {
                "unit": "Jest",
                "integration": "Jest + Supertest",
                "e2e": "Cypress / Playwright",
                "coverage": "Jest --coverage",
                "patterns": """
- Use describe/it blocks
- Use beforeEach/afterEach for setup
- Mock dependencies with jest.mock()
- Use expect() assertions
- Test asynchronous code properly
- Clear test descriptions
                """
            },
            "typescript": {
                "unit": "Jest",
                "integration": "Jest + Supertest",
                "e2e": "Cypress / Playwright",
                "coverage": "Jest --coverage",
                "patterns": """
- Type-safe test setup
- Use proper TypeScript types in tests
- Mock with jest.Mock<T>
- Test type contracts
- Use beforeEach/afterEach
- Clear test descriptions
                """
            },
            "go": {
                "unit": "testing package",
                "integration": "testing + testify",
                "e2e": "testing + httptest",
                "coverage": "go test -cover",
                "patterns": """
- Use t.Run for subtests
- Table-driven tests
- Use testify for assertions
- Mock with interfaces
- Test error cases
- Benchmark with testing.B
                """
            },
            "rust": {
                "unit": "built-in test",
                "integration": "built-in test",
                "e2e": "built-in test",
                "coverage": "cargo tarpaulin",
                "patterns": """
- Use #[test] attribute
- Use #[cfg(test)] module
- Result<()> for tests with ?
- Use assert!, assert_eq!
- Test panic with #[should_panic]
- Mock with mockall
                """
            }
        }

    async def generate_unit_tests(
        self,
        code: str,
        language: str = "python",
        function_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate unit tests for given code.

        Args:
            code: Code to generate tests for
            language: Programming language
            function_name: Specific function to test (optional)
            context: Additional context

        Returns:
            Generated tests with metadata
        """
        logger.info(f"🧪 Generating unit tests for {language} code...")

        try:
            framework_config = self.test_frameworks.get(
                language.lower(),
                self.test_frameworks["python"]
            )

            # Build prompt
            prompt = self._build_test_generation_prompt(
                code=code,
                language=language,
                test_type="unit",
                framework_config=framework_config,
                function_name=function_name,
                context=context
            )

            # Call LLM
            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert test engineer specializing in writing comprehensive, high-quality automated tests."
                    },
                    {"role": "user", "content": prompt}
                ],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.3,
                max_tokens=2500
            )

            content = response.choices[0].message.content.strip()

            # Extract tests
            tests, explanation = self._extract_tests_and_explanation(content, language)

            if not tests:
                return {
                    "success": False,
                    "error": "Failed to generate tests",
                    "raw_response": content
                }

            # Analyze test coverage
            coverage_analysis = self._analyze_test_coverage(code, tests)

            # Store in history
            test_record = {
                "timestamp": datetime.now().isoformat(),
                "test_type": "unit",
                "language": language,
                "code": code[:200],
                "tests": tests,
                "explanation": explanation,
                "coverage": coverage_analysis
            }

            self.test_history.append(test_record)

            logger.info(f"✅ Unit tests generated ({len(tests)} chars, coverage: {coverage_analysis.get('estimated_coverage', 0)}%)")

            return {
                "success": True,
                "tests": tests,
                "explanation": explanation,
                "language": language,
                "test_type": "unit",
                "framework": framework_config["unit"],
                "coverage_analysis": coverage_analysis,
                "metadata": {
                    "lines": tests.count('\n') + 1,
                    "characters": len(tests),
                    "timestamp": test_record["timestamp"]
                }
            }

        except Exception as e:
            logger.error(f"❌ Test generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_integration_tests(
        self,
        components: List[str],
        language: str = "python",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate integration tests for multiple components.

        Args:
            components: List of component descriptions to test together
            language: Programming language
            context: Additional context (API endpoints, database, etc.)

        Returns:
            Generated integration tests
        """
        logger.info(f"🧪 Generating integration tests for {len(components)} components...")

        try:
            framework_config = self.test_frameworks.get(language.lower(), {})

            prompt = f"""Generate integration tests in {language} for the following components:

**Components to Test:**
{chr(10).join([f'{i+1}. {comp}' for i, comp in enumerate(components)])}

**Test Framework:** {framework_config.get('integration', 'standard')}

**Context:** {json.dumps(context, indent=2) if context else 'None'}

**Requirements:**
1. Test interactions between components
2. Test data flow between components
3. Test error handling across components
4. Use appropriate setup/teardown
5. Mock external dependencies
6. Include assertions for integration points
7. Test both success and failure scenarios

**Patterns:**{framework_config.get('patterns', '')}

Format your response as:
```{language}
[Your integration tests here]
```

**Test Coverage:**
[Explain what integration scenarios are covered]
"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.3,
                max_tokens=2500
            )

            content = response.choices[0].message.content.strip()
            tests, explanation = self._extract_tests_and_explanation(content, language)

            if not tests:
                return {"success": False, "error": "Failed to generate integration tests"}

            return {
                "success": True,
                "tests": tests,
                "explanation": explanation,
                "language": language,
                "test_type": "integration",
                "framework": framework_config.get("integration", "standard"),
                "components_tested": len(components)
            }

        except Exception as e:
            logger.error(f"❌ Integration test generation failed: {e}")
            return {"success": False, "error": str(e)}

    async def identify_edge_cases(
        self,
        code: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Identify edge cases that should be tested.

        Args:
            code: Code to analyze for edge cases
            language: Programming language

        Returns:
            List of edge cases with test suggestions
        """
        logger.info(f"🔍 Identifying edge cases for {language} code...")

        try:
            prompt = f"""Analyze this {language} code and identify edge cases that should be tested:

```{language}
{code}
```

Identify edge cases in these categories:
1. **Boundary Conditions**: Min/max values, empty inputs, null/None
2. **Error Cases**: Invalid inputs, exceptions, error conditions
3. **Special Values**: Zero, negative numbers, special characters
4. **State Issues**: Concurrent access, ordering, timing
5. **Resource Limits**: Large inputs, memory constraints

For each edge case, provide:
- Description of the edge case
- Why it's important to test
- Suggested test approach

Format as JSON:
{{
    "edge_cases": [
        {{
            "category": "boundary_conditions",
            "description": "Empty list input",
            "importance": "Function should handle empty input gracefully",
            "test_approach": "Test with empty list, verify returns empty or default"
        }}
    ]
}}
"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.4,
                max_tokens=1500
            )

            content = response.choices[0].message.content.strip()

            # Extract JSON
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                edge_cases_data = json.loads(content[start:end])
                return {
                    "success": True,
                    "edge_cases": edge_cases_data.get("edge_cases", []),
                    "total_cases": len(edge_cases_data.get("edge_cases", []))
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to parse edge cases"
                }

        except Exception as e:
            logger.error(f"❌ Edge case identification failed: {e}")
            return {"success": False, "error": str(e)}

    async def execute_tests(
        self,
        test_file_path: str,
        language: str = "python",
        coverage: bool = True
    ) -> Dict[str, Any]:
        """
        Execute tests and return results.

        Args:
            test_file_path: Path to test file
            language: Programming language
            coverage: Whether to generate coverage report

        Returns:
            Test execution results
        """
        logger.info(f"▶️  Executing tests: {test_file_path}")

        try:
            framework_config = self.test_frameworks.get(language.lower(), {})

            # Build test command
            if language == "python":
                if coverage:
                    command = f"pytest {test_file_path} --cov --cov-report=term-missing"
                else:
                    command = f"pytest {test_file_path} -v"

            elif language in ["javascript", "typescript"]:
                if coverage:
                    command = f"npm test -- {test_file_path} --coverage"
                else:
                    command = f"npm test -- {test_file_path}"

            elif language == "go":
                if coverage:
                    command = f"go test {test_file_path} -cover -v"
                else:
                    command = f"go test {test_file_path} -v"

            elif language == "rust":
                command = "cargo test"

            else:
                return {"success": False, "error": f"Unsupported language: {language}"}

            # Execute tests
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Parse results
            passed = result.returncode == 0
            output = result.stdout + result.stderr

            # Extract test counts (basic parsing)
            test_count = self._extract_test_count(output, language)
            coverage_percent = self._extract_coverage_percent(output) if coverage else None

            return {
                "success": True,
                "tests_passed": passed,
                "test_count": test_count,
                "coverage": coverage_percent,
                "output": output[:1000],  # Limit output
                "command": command,
                "exit_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Test execution timed out (>60s)"
            }
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _build_test_generation_prompt(
        self,
        code: str,
        language: str,
        test_type: str,
        framework_config: Dict[str, str],
        function_name: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build comprehensive test generation prompt."""

        prompt_parts = [
            f"Generate {test_type} tests in {language} for the following code:",
            f"\n**Code to Test:**\n```{language}\n{code}\n```\n",
            f"\n**Test Framework:** {framework_config.get(test_type, 'standard')}",
        ]

        if function_name:
            prompt_parts.append(f"\n**Focus on function:** {function_name}")

        if context:
            prompt_parts.append(f"\n**Context:**\n{json.dumps(context, indent=2)}")

        prompt_parts.extend([
            f"\n**Testing Patterns:**{framework_config.get('patterns', '')}",
            "\n**Requirements:**",
            "1. Test all major code paths",
            "2. Test edge cases (empty input, null, boundary values)",
            "3. Test error handling",
            "4. Use clear, descriptive test names",
            "5. Include setup and teardown if needed",
            "6. Mock external dependencies",
            "7. Make tests independent and repeatable",
            "8. Add comments explaining complex test logic",
            "",
            "**Format your response as:**",
            f"```{language}",
            "[Your test code here]",
            "```",
            "",
            "**Test Coverage Explanation:**",
            "[Explain what scenarios are covered and any important edge cases]"
        ])

        return "\n".join(prompt_parts)

    def _extract_tests_and_explanation(self, content: str, language: str) -> tuple[str, str]:
        """
        Extract test code and explanation from LLM response.

        Args:
            content: LLM response
            language: Programming language

        Returns:
            Tuple of (tests, explanation)
        """
        # Extract test code from markdown blocks
        code_pattern = rf"```{language}?\\n(.*?)```"
        matches = re.findall(code_pattern, content, re.DOTALL | re.IGNORECASE)

        if matches:
            tests = matches[0].strip()
            # Extract explanation (text after code block)
            explanation_match = re.search(
                rf"```{language}?.*?```\\s*(.*)",
                content,
                re.DOTALL | re.IGNORECASE
            )
            explanation = explanation_match.group(1).strip() if explanation_match else ""
        else:
            # No code blocks found
            tests = content.strip()
            explanation = ""

        return tests, explanation

    def _analyze_test_coverage(self, code: str, tests: str) -> Dict[str, Any]:
        """
        Analyze what parts of code are covered by tests.

        Args:
            code: Original code
            tests: Generated tests

        Returns:
            Coverage analysis
        """
        # Simple heuristic-based analysis
        # In production, would use actual coverage tools

        # Count functions in original code
        function_pattern = r"def\s+(\w+)|function\s+(\w+)|func\s+(\w+)|fn\s+(\w+)"
        functions = re.findall(function_pattern, code)
        function_count = len([f for group in functions for f in group if f])

        # Count test functions
        test_pattern = r"def\s+test_|it\(|test\(|#\[test\]"
        test_matches = re.findall(test_pattern, tests)
        test_count = len(test_matches)

        # Estimate coverage (rough heuristic)
        if function_count > 0:
            estimated_coverage = min(100, (test_count / function_count) * 80)
        else:
            estimated_coverage = 0

        return {
            "functions_in_code": function_count,
            "test_functions": test_count,
            "estimated_coverage": round(estimated_coverage, 1),
            "analysis": f"{test_count} tests for {function_count} functions"
        }

    def _extract_test_count(self, output: str, language: str) -> Dict[str, int]:
        """Extract test counts from test output."""
        result = {"passed": 0, "failed": 0, "total": 0}

        if language == "python":
            # pytest format: "5 passed, 2 failed"
            passed_match = re.search(r"(\\d+)\\s+passed", output)
            failed_match = re.search(r"(\\d+)\\s+failed", output)

            if passed_match:
                result["passed"] = int(passed_match.group(1))
            if failed_match:
                result["failed"] = int(failed_match.group(1))

        elif language in ["javascript", "typescript"]:
            # Jest format: "Tests: 5 passed, 5 total"
            passed_match = re.search(r"Tests:\\s+(\\d+)\\s+passed", output)
            total_match = re.search(r"(\\d+)\\s+total", output)

            if passed_match:
                result["passed"] = int(passed_match.group(1))
            if total_match:
                result["total"] = int(total_match.group(1))

        result["total"] = max(result["total"], result["passed"] + result["failed"])
        return result

    def _extract_coverage_percent(self, output: str) -> Optional[float]:
        """Extract coverage percentage from output."""
        # Look for coverage percentage
        coverage_match = re.search(r"(\\d+)%\\s+coverage", output, re.IGNORECASE)
        if coverage_match:
            return float(coverage_match.group(1))

        # Alternative format: "TOTAL 85%"
        total_match = re.search(r"TOTAL.*?(\\d+)%", output)
        if total_match:
            return float(total_match.group(1))

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get test generation statistics.

        Returns:
            Statistics dictionary
        """
        if not self.test_history:
            return {
                "total_tests_generated": 0,
                "test_types": {},
                "languages": {}
            }

        # Count by type and language
        type_counts = {}
        lang_counts = {}

        for record in self.test_history:
            test_type = record.get("test_type", "unknown")
            language = record.get("language", "unknown")

            type_counts[test_type] = type_counts.get(test_type, 0) + 1
            lang_counts[language] = lang_counts.get(language, 0) + 1

        return {
            "total_tests_generated": len(self.test_history),
            "test_types": type_counts,
            "languages": lang_counts,
            "recent_tests": [
                {
                    "test_type": t["test_type"],
                    "language": t["language"],
                    "coverage": t.get("coverage", {}).get("estimated_coverage", 0),
                    "timestamp": t["timestamp"]
                }
                for t in self.test_history[-5:]
            ]
        }


# Global singleton instance
test_agent = TestAgent()
