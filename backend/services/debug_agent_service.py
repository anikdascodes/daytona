"""
Debug Agent Service - Automated issue resolution and debugging.

Capabilities:
- Error analysis and root cause identification
- Stack trace parsing and interpretation
- Fix generation with step-by-step solutions
- Debugging strategy recommendations
- Integration with error analysis service

Part of Phase 4: Supreme AI Capabilities
"""
import re
import json
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime
from litellm import acompletion
from config import settings
from utils.logger import logger


class DebugAgent:
    """
    Specialized agent for debugging and issue resolution.

    Features:
    - Parse and interpret error messages
    - Analyze stack traces
    - Identify root causes
    - Generate fixes with explanations
    - Suggest debugging strategies
    - Learn from error patterns
    """

    def __init__(self):
        """Initialize debug agent."""
        self.debug_history: List[Dict[str, Any]] = []
        self.error_patterns = self._load_error_patterns()
        logger.info("DebugAgent initialized")

    def _load_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Load common error patterns and solutions.

        Returns:
            Dictionary of error patterns
        """
        return {
            "python": {
                "AttributeError": {
                    "pattern": r"AttributeError: .* has no attribute '(\w+)'",
                    "common_causes": [
                        "Typo in attribute name",
                        "Object not initialized properly",
                        "Wrong object type",
                        "Missing import"
                    ],
                    "debugging_steps": [
                        "Check object type with type(obj)",
                        "Verify object initialization",
                        "Use dir(obj) to see available attributes",
                        "Check for typos in attribute name"
                    ]
                },
                "KeyError": {
                    "pattern": r"KeyError: '(\w+)'",
                    "common_causes": [
                        "Key doesn't exist in dictionary",
                        "Typo in key name",
                        "Data structure not as expected"
                    ],
                    "debugging_steps": [
                        "Print dictionary keys",
                        "Use .get() with default value",
                        "Check data source/API response",
                        "Validate data structure"
                    ]
                },
                "IndexError": {
                    "pattern": r"IndexError: list index out of range",
                    "common_causes": [
                        "List is empty",
                        "Index exceeds list length",
                        "Off-by-one error"
                    ],
                    "debugging_steps": [
                        "Check list length",
                        "Add bounds checking",
                        "Use enumerate() for safe iteration",
                        "Handle empty list case"
                    ]
                },
                "TypeError": {
                    "pattern": r"TypeError: (.*)",
                    "common_causes": [
                        "Wrong number of arguments",
                        "Incompatible types",
                        "None value where object expected",
                        "Missing required parameter"
                    ],
                    "debugging_steps": [
                        "Check function signature",
                        "Verify argument types",
                        "Add type hints and validation",
                        "Check for None values"
                    ]
                },
                "ImportError": {
                    "pattern": r"ImportError: (.*)|ModuleNotFoundError: (.*)",
                    "common_causes": [
                        "Module not installed",
                        "Wrong module name",
                        "Circular import",
                        "Python path issue"
                    ],
                    "debugging_steps": [
                        "Install missing package",
                        "Check module name spelling",
                        "Review import structure",
                        "Verify PYTHONPATH"
                    ]
                }
            },
            "javascript": {
                "TypeError": {
                    "pattern": r"TypeError: (.*)",
                    "common_causes": [
                        "Undefined is not a function",
                        "Cannot read property of undefined",
                        "Wrong type passed"
                    ],
                    "debugging_steps": [
                        "Add null/undefined checks",
                        "Use optional chaining (?.)",
                        "Verify object initialization",
                        "Check async/await usage"
                    ]
                },
                "ReferenceError": {
                    "pattern": r"ReferenceError: (.*) is not defined",
                    "common_causes": [
                        "Variable not declared",
                        "Typo in variable name",
                        "Scope issue",
                        "Missing import"
                    ],
                    "debugging_steps": [
                        "Check variable declaration",
                        "Verify scope",
                        "Add missing import",
                        "Check for typos"
                    ]
                }
            }
        }

    async def debug_error(
        self,
        error_message: str,
        stack_trace: Optional[str] = None,
        code_context: Optional[str] = None,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Debug an error and provide solutions.

        Args:
            error_message: The error message
            stack_trace: Stack trace (if available)
            code_context: Relevant code context
            language: Programming language

        Returns:
            Debug analysis with solutions
        """
        logger.info(f"🐛 Debugging error: {error_message[:50]}...")

        try:
            # Parse error
            error_info = self._parse_error(error_message, stack_trace, language)

            # Identify root cause
            root_cause = await self._identify_root_cause(
                error_message, stack_trace, code_context, language
            )

            # Generate fixes
            fixes = await self._generate_fixes(
                error_message, stack_trace, code_context, language, root_cause
            )

            # Get debugging strategy
            strategy = self._get_debugging_strategy(error_info, language)

            # Check for known patterns
            pattern_match = self._match_error_pattern(error_message, language)

            result = {
                "error_info": error_info,
                "root_cause": root_cause,
                "fixes": fixes,
                "debugging_strategy": strategy,
                "pattern_match": pattern_match,
                "severity": self._assess_severity(error_message, stack_trace),
                "timestamp": datetime.now().isoformat()
            }

            # Store in history
            self.debug_history.append({
                "timestamp": result["timestamp"],
                "error_type": error_info.get("error_type"),
                "language": language,
                "severity": result["severity"],
                "fixes_provided": len(fixes)
            })

            logger.info(f"✅ Debug analysis complete: {len(fixes)} fixes generated")

            return {
                "success": True,
                "debug_result": result
            }

        except Exception as e:
            logger.error(f"❌ Debug failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_error(
        self,
        error_message: str,
        stack_trace: Optional[str],
        language: str
    ) -> Dict[str, Any]:
        """
        Parse error message and extract information.

        Args:
            error_message: Error message
            stack_trace: Stack trace
            language: Programming language

        Returns:
            Parsed error information
        """
        # Extract error type
        error_type = "Unknown"

        if language == "python":
            # Python: "ErrorType: message"
            match = re.match(r"(\w+Error|\w+Exception):", error_message)
            if match:
                error_type = match.group(1)

        elif language in ["javascript", "typescript"]:
            # JavaScript: "ErrorType: message"
            match = re.match(r"(\w+Error):", error_message)
            if match:
                error_type = match.group(1)

        # Extract file and line number from stack trace
        file_info = None
        if stack_trace:
            file_info = self._extract_file_info(stack_trace, language)

        return {
            "error_type": error_type,
            "error_message": error_message,
            "file_info": file_info,
            "has_stack_trace": stack_trace is not None
        }

    def _extract_file_info(self, stack_trace: str, language: str) -> Optional[Dict[str, Any]]:
        """Extract file and line information from stack trace."""
        if language == "python":
            # Python: 'File "/path/file.py", line 42'
            match = re.search(r'File "([^"]+)", line (\d+)', stack_trace)
            if match:
                return {
                    "file": match.group(1),
                    "line": int(match.group(2))
                }

        elif language in ["javascript", "typescript"]:
            # JavaScript: "at function (/path/file.js:42:10)"
            match = re.search(r'at .* \(([^:]+):(\d+):\d+\)', stack_trace)
            if match:
                return {
                    "file": match.group(1),
                    "line": int(match.group(2))
                }

        return None

    async def _identify_root_cause(
        self,
        error_message: str,
        stack_trace: Optional[str],
        code_context: Optional[str],
        language: str
    ) -> Dict[str, Any]:
        """
        Use AI to identify root cause of error.

        Args:
            error_message: Error message
            stack_trace: Stack trace
            code_context: Code context
            language: Programming language

        Returns:
            Root cause analysis
        """
        try:
            prompt = f"""Analyze this {language} error and identify the root cause:

**Error Message:**
{error_message}

**Stack Trace:**
{stack_trace[:1000] if stack_trace else 'Not available'}

**Code Context:**
```{language}
{code_context[:800] if code_context else 'Not available'}
```

Provide root cause analysis:
1. What is the immediate cause of the error?
2. What is the underlying root cause?
3. Why did this happen?
4. What code path led to this error?

Format as JSON:
{{
    "immediate_cause": "Description of immediate cause",
    "root_cause": "Underlying root cause",
    "explanation": "Why this happened",
    "code_path": "Path that led to error"
}}
"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.2,
                max_tokens=1000
            )

            content = response.choices[0].message.content.strip()

            # Extract JSON
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                analysis = json.loads(content[start:end])
                return analysis
            else:
                return {
                    "immediate_cause": "Could not determine",
                    "root_cause": "Analysis failed",
                    "explanation": content[:200]
                }

        except Exception as e:
            logger.error(f"Root cause analysis failed: {e}")
            return {
                "immediate_cause": "AI analysis unavailable",
                "root_cause": "Manual analysis required",
                "error": str(e)
            }

    async def _generate_fixes(
        self,
        error_message: str,
        stack_trace: Optional[str],
        code_context: Optional[str],
        language: str,
        root_cause: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate potential fixes for the error.

        Args:
            error_message: Error message
            stack_trace: Stack trace
            code_context: Code context
            language: Programming language
            root_cause: Root cause analysis

        Returns:
            List of potential fixes
        """
        try:
            prompt = f"""Generate fixes for this {language} error:

**Error:** {error_message}

**Root Cause:** {root_cause.get('root_cause', 'Unknown')}

**Code Context:**
```{language}
{code_context[:800] if code_context else 'Not available'}
```

Provide 3-5 potential fixes, ordered by likelihood of success:

For each fix:
1. Title (brief description)
2. Explanation (why this fix works)
3. Code changes (specific changes to make)
4. Confidence (high/medium/low)
5. Side effects (any potential issues)

Format as JSON:
{{
    "fixes": [
        {{
            "title": "Fix title",
            "explanation": "Why this works",
            "code_changes": "Specific code changes",
            "confidence": "high",
            "side_effects": "None" or "Description"
        }}
    ]
}}
"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.3,
                max_tokens=1500
            )

            content = response.choices[0].message.content.strip()

            # Extract JSON
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                result = json.loads(content[start:end])
                return result.get("fixes", [])
            else:
                return []

        except Exception as e:
            logger.error(f"Fix generation failed: {e}")
            return []

    def _get_debugging_strategy(
        self,
        error_info: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """
        Get debugging strategy for this error type.

        Args:
            error_info: Parsed error information
            language: Programming language

        Returns:
            Debugging strategy
        """
        error_type = error_info.get("error_type", "Unknown")

        # Get pattern-based strategy
        patterns = self.error_patterns.get(language, {})
        pattern_info = patterns.get(error_type, {})

        strategy = {
            "error_type": error_type,
            "debugging_steps": pattern_info.get("debugging_steps", [
                "Add print/log statements",
                "Use debugger to step through code",
                "Check variable values",
                "Verify assumptions"
            ]),
            "tools": self._get_debugging_tools(language),
            "logging_points": [
                "Before the error occurs",
                "At function entry/exit",
                "At key decision points",
                "When data is transformed"
            ]
        }

        return strategy

    def _get_debugging_tools(self, language: str) -> List[str]:
        """Get recommended debugging tools for language."""
        tools = {
            "python": [
                "pdb (Python debugger)",
                "print() / logging module",
                "ipdb (enhanced debugger)",
                "PyCharm debugger",
                "VS Code debugger"
            ],
            "javascript": [
                "Chrome DevTools",
                "console.log()",
                "debugger statement",
                "VS Code debugger",
                "Node.js inspector"
            ],
            "typescript": [
                "Chrome DevTools",
                "VS Code debugger",
                "Source maps",
                "ts-node debugger"
            ],
            "go": [
                "Delve debugger",
                "fmt.Printf()",
                "GoLand debugger",
                "VS Code debugger"
            ],
            "rust": [
                "rust-lldb / rust-gdb",
                "println! macro",
                "dbg! macro",
                "VS Code debugger"
            ]
        }

        return tools.get(language, ["Standard debugger", "Print statements"])

    def _match_error_pattern(
        self,
        error_message: str,
        language: str
    ) -> Optional[Dict[str, Any]]:
        """
        Match error against known patterns.

        Args:
            error_message: Error message
            language: Programming language

        Returns:
            Pattern match information if found
        """
        patterns = self.error_patterns.get(language, {})

        for error_type, pattern_info in patterns.items():
            pattern = pattern_info.get("pattern", "")
            if re.search(pattern, error_message, re.IGNORECASE):
                return {
                    "error_type": error_type,
                    "common_causes": pattern_info.get("common_causes", []),
                    "debugging_steps": pattern_info.get("debugging_steps", [])
                }

        return None

    def _assess_severity(
        self,
        error_message: str,
        stack_trace: Optional[str]
    ) -> str:
        """
        Assess error severity.

        Args:
            error_message: Error message
            stack_trace: Stack trace

        Returns:
            Severity level (critical/high/medium/low)
        """
        error_lower = error_message.lower()

        # Critical errors
        critical_keywords = [
            "segmentation fault", "segfault", "core dumped",
            "out of memory", "stackoverflow",
            "database connection", "cannot connect"
        ]

        for keyword in critical_keywords:
            if keyword in error_lower:
                return "critical"

        # High severity
        high_keywords = [
            "exception", "fatal", "panic",
            "assertion failed", "null pointer"
        ]

        for keyword in high_keywords:
            if keyword in error_lower:
                return "high"

        # Has stack trace suggests runtime error
        if stack_trace and len(stack_trace) > 100:
            return "medium"

        return "low"

    async def suggest_debugging_approach(
        self,
        error_type: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Suggest general debugging approach for error type.

        Args:
            error_type: Type of error
            language: Programming language

        Returns:
            Debugging approach suggestions
        """
        patterns = self.error_patterns.get(language, {})
        pattern_info = patterns.get(error_type, {})

        return {
            "error_type": error_type,
            "language": language,
            "common_causes": pattern_info.get("common_causes", []),
            "debugging_steps": pattern_info.get("debugging_steps", []),
            "tools": self._get_debugging_tools(language),
            "best_practices": [
                "Reproduce the error consistently",
                "Isolate the problem (divide and conquer)",
                "Check assumptions",
                "Use version control to track changes",
                "Write tests to prevent regression"
            ]
        }

    async def analyze_stack_trace(
        self,
        stack_trace: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Analyze stack trace and provide insights.

        Args:
            stack_trace: Stack trace to analyze
            language: Programming language

        Returns:
            Stack trace analysis
        """
        logger.info("📚 Analyzing stack trace...")

        try:
            # Parse stack trace
            frames = self._parse_stack_trace(stack_trace, language)

            # Identify relevant frames
            relevant_frames = [
                f for f in frames
                if not self._is_library_frame(f.get("file", ""))
            ]

            # AI analysis
            prompt = f"""Analyze this {language} stack trace:

```
{stack_trace[:1500]}
```

Provide analysis:
1. What is the execution path?
2. Which frame is most likely the source of the error?
3. What should the developer focus on?

Keep response concise (< 200 words).
"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.3,
                max_tokens=500
            )

            analysis = response.choices[0].message.content.strip()

            return {
                "success": True,
                "total_frames": len(frames),
                "relevant_frames": relevant_frames,
                "analysis": analysis,
                "recommendation": self._get_stack_trace_recommendation(frames)
            }

        except Exception as e:
            logger.error(f"Stack trace analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_stack_trace(self, stack_trace: str, language: str) -> List[Dict[str, Any]]:
        """Parse stack trace into frames."""
        frames = []

        if language == "python":
            # Python stack trace format
            pattern = r'File "([^"]+)", line (\d+), in (\w+)'
            matches = re.finditer(pattern, stack_trace)

            for match in matches:
                frames.append({
                    "file": match.group(1),
                    "line": int(match.group(2)),
                    "function": match.group(3)
                })

        elif language in ["javascript", "typescript"]:
            # JavaScript stack trace format
            pattern = r'at (\w+) \(([^:]+):(\d+):\d+\)'
            matches = re.finditer(pattern, stack_trace)

            for match in matches:
                frames.append({
                    "function": match.group(1),
                    "file": match.group(2),
                    "line": int(match.group(3))
                })

        return frames

    def _is_library_frame(self, file_path: str) -> bool:
        """Check if frame is from a library (not user code)."""
        library_indicators = [
            "site-packages", "node_modules", "/usr/lib",
            "venv/", ".venv/", "lib/python"
        ]

        return any(indicator in file_path for indicator in library_indicators)

    def _get_stack_trace_recommendation(self, frames: List[Dict[str, Any]]) -> str:
        """Get recommendation based on stack trace."""
        if not frames:
            return "Stack trace could not be parsed"

        user_frames = [f for f in frames if not self._is_library_frame(f.get("file", ""))]

        if user_frames:
            first_user = user_frames[0]
            return f"Focus on: {first_user.get('file')}:{first_user.get('line')} in {first_user.get('function')}"
        else:
            return "Error appears to be in library code, check your usage"

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get debugging statistics.

        Returns:
            Statistics dictionary
        """
        if not self.debug_history:
            return {
                "total_debugs": 0,
                "by_severity": {},
                "by_language": {}
            }

        severity_counts = {}
        lang_counts = {}

        for record in self.debug_history:
            severity = record.get("severity", "unknown")
            language = record.get("language", "unknown")

            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            lang_counts[language] = lang_counts.get(language, 0) + 1

        return {
            "total_debugs": len(self.debug_history),
            "by_severity": severity_counts,
            "by_language": lang_counts,
            "recent_debugs": [
                {
                    "error_type": d["error_type"],
                    "severity": d["severity"],
                    "fixes": d["fixes_provided"],
                    "timestamp": d["timestamp"]
                }
                for d in self.debug_history[-5:]
            ]
        }


# Global singleton instance
debug_agent = DebugAgent()
