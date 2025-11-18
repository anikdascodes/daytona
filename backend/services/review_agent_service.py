"""
Review Agent Service - Automated code review and quality analysis.

Capabilities:
- Security vulnerability detection
- Performance analysis
- Best practices validation
- Code smell detection
- Refactoring suggestions
- Issue prioritization

Part of Phase 4: Supreme AI Capabilities
"""
import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from litellm import acompletion
from config import settings
from utils.logger import logger


class ReviewAgent:
    """
    Specialized agent for automated code review and quality analysis.

    Features:
    - Security vulnerability detection (OWASP, injection, XSS, etc.)
    - Performance analysis (complexity, bottlenecks)
    - Best practices validation (language-specific)
    - Code smell detection (duplicates, complexity, coupling)
    - Refactoring suggestions (prioritized)
    - Issue categorization and severity scoring
    """

    def __init__(self):
        """Initialize review agent."""
        self.review_history: List[Dict[str, Any]] = []
        self.security_patterns = self._load_security_patterns()
        self.best_practices = self._load_best_practices()
        logger.info("ReviewAgent initialized")

    def _load_security_patterns(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Load common security vulnerability patterns.

        Returns:
            Dictionary of security patterns by category
        """
        return {
            "sql_injection": [
                {
                    "pattern": r"execute\(['\"].*\+.*['\"]",
                    "severity": "critical",
                    "description": "Potential SQL injection via string concatenation"
                },
                {
                    "pattern": r"cursor\.execute\(.*%.*\)",
                    "severity": "high",
                    "description": "SQL injection risk with string formatting"
                }
            ],
            "xss": [
                {
                    "pattern": r"innerHTML\s*=\s*[^'\"]*\+",
                    "severity": "high",
                    "description": "XSS vulnerability via innerHTML with concatenation"
                },
                {
                    "pattern": r"dangerouslySetInnerHTML",
                    "severity": "medium",
                    "description": "Potential XSS with dangerouslySetInnerHTML"
                }
            ],
            "hardcoded_secrets": [
                {
                    "pattern": r"password\s*=\s*['\"][^'\"]+['\"]",
                    "severity": "critical",
                    "description": "Hardcoded password detected"
                },
                {
                    "pattern": r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]",
                    "severity": "critical",
                    "description": "Hardcoded API key detected"
                },
                {
                    "pattern": r"secret\s*=\s*['\"][^'\"]+['\"]",
                    "severity": "high",
                    "description": "Hardcoded secret detected"
                }
            ],
            "command_injection": [
                {
                    "pattern": r"os\.system\([^)]*\+[^)]*\)",
                    "severity": "critical",
                    "description": "Command injection via os.system with string concatenation"
                },
                {
                    "pattern": r"subprocess\.(call|run)\([^)]*shell=True",
                    "severity": "high",
                    "description": "Shell injection risk with shell=True"
                }
            ]
        }

    def _load_best_practices(self) -> Dict[str, List[str]]:
        """
        Load best practices for different languages.

        Returns:
            Dictionary of best practices by language
        """
        return {
            "python": [
                "Use type hints for function signatures",
                "Write docstrings for all public functions and classes",
                "Follow PEP 8 style guide",
                "Use list comprehensions instead of map/filter where appropriate",
                "Use context managers for resource management",
                "Avoid bare except clauses",
                "Use f-strings for string formatting",
                "Keep functions small and focused (< 50 lines)",
                "Use meaningful variable names",
                "Avoid global variables"
            ],
            "javascript": [
                "Use const/let instead of var",
                "Use async/await instead of callbacks",
                "Use arrow functions appropriately",
                "Use template literals for string interpolation",
                "Use destructuring for objects and arrays",
                "Avoid using eval()",
                "Use strict mode",
                "Handle promise rejections",
                "Use meaningful variable names",
                "Keep functions pure when possible"
            ],
            "typescript": [
                "Enable strict mode in tsconfig",
                "Avoid using 'any' type",
                "Use interfaces for object shapes",
                "Use generics for reusable components",
                "Use union types instead of enums when appropriate",
                "Use readonly for immutable properties",
                "Prefer type inference where clear",
                "Use discriminated unions for state",
                "Export types properly",
                "Use utility types (Partial, Required, etc.)"
            ],
            "go": [
                "Handle all errors explicitly",
                "Use defer for cleanup",
                "Keep interfaces small",
                "Use meaningful error messages",
                "Avoid global state",
                "Use goroutines carefully",
                "Close channels when done",
                "Use context for cancellation",
                "Write table-driven tests",
                "Export only what's necessary"
            ],
            "rust": [
                "Use Result for error handling",
                "Prefer borrowing over ownership transfer",
                "Use iterators instead of loops",
                "Avoid unsafe code unless necessary",
                "Use Option instead of null",
                "Write comprehensive tests",
                "Use cargo clippy for linting",
                "Document public APIs",
                "Use type system to enforce invariants",
                "Prefer composition over inheritance"
            ]
        }

    async def review_code(
        self,
        code: str,
        language: str = "python",
        context: Optional[Dict[str, Any]] = None,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive code review.

        Args:
            code: Code to review
            language: Programming language
            context: Additional context
            focus_areas: Specific areas to focus on (security, performance, etc.)

        Returns:
            Comprehensive review results
        """
        logger.info(f"🔍 Reviewing {language} code...")

        try:
            # Determine focus areas
            if not focus_areas:
                focus_areas = ["security", "performance", "best_practices", "code_smells"]

            # Run all review checks
            results = {
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "code_length": len(code),
                "lines": code.count('\n') + 1
            }

            # Security analysis
            if "security" in focus_areas:
                results["security"] = await self._analyze_security(code, language)

            # Performance analysis
            if "performance" in focus_areas:
                results["performance"] = await self._analyze_performance(code, language)

            # Best practices check
            if "best_practices" in focus_areas:
                results["best_practices"] = await self._check_best_practices(code, language, context)

            # Code smells detection
            if "code_smells" in focus_areas:
                results["code_smells"] = await self._detect_code_smells(code, language)

            # Generate refactoring suggestions
            results["refactoring"] = await self._generate_refactoring_suggestions(
                code, language, results
            )

            # Calculate overall score and prioritize issues
            results["summary"] = self._generate_summary(results)

            # Store in history
            self.review_history.append({
                "timestamp": results["timestamp"],
                "language": language,
                "code_length": results["code_length"],
                "issues_found": results["summary"]["total_issues"],
                "severity_breakdown": results["summary"]["by_severity"]
            })

            logger.info(f"✅ Review complete: {results['summary']['total_issues']} issues found")

            return {
                "success": True,
                "review": results
            }

        except Exception as e:
            logger.error(f"❌ Code review failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _analyze_security(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Analyze code for security vulnerabilities.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Security analysis results
        """
        logger.info("🔒 Analyzing security vulnerabilities...")

        # Pattern-based detection
        pattern_issues = []
        for category, patterns in self.security_patterns.items():
            for pattern_info in patterns:
                matches = re.finditer(pattern_info["pattern"], code, re.IGNORECASE)
                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1
                    pattern_issues.append({
                        "category": category,
                        "severity": pattern_info["severity"],
                        "description": pattern_info["description"],
                        "line": line_num,
                        "code_snippet": match.group(0)
                    })

        # AI-powered security analysis
        ai_analysis = await self._ai_security_analysis(code, language)

        return {
            "pattern_based_issues": pattern_issues,
            "ai_analysis": ai_analysis,
            "total_issues": len(pattern_issues) + len(ai_analysis.get("issues", []))
        }

    async def _ai_security_analysis(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Use AI for deep security analysis.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            AI-powered security analysis
        """
        try:
            prompt = f"""Analyze this {language} code for security vulnerabilities:

```{language}
{code[:1500]}  # Limit code length
```

Identify security issues in these categories:
1. **Injection Vulnerabilities**: SQL, command, code injection
2. **Authentication/Authorization**: Weak auth, missing access control
3. **Sensitive Data**: Hardcoded secrets, exposed data
4. **Cryptography**: Weak encryption, insecure random
5. **Input Validation**: Missing validation, unsafe deserialization

For each issue found, provide:
- Category
- Severity (critical/high/medium/low)
- Description
- Line number (estimate if needed)
- Remediation

Format as JSON:
{{
    "issues": [
        {{
            "category": "sql_injection",
            "severity": "high",
            "description": "SQL query uses string concatenation",
            "line": 15,
            "remediation": "Use parameterized queries"
        }}
    ]
}}
"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.2,
                max_tokens=1500
            )

            content = response.choices[0].message.content.strip()

            # Extract JSON
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                analysis = json.loads(content[start:end])
                return analysis
            else:
                return {"issues": []}

        except Exception as e:
            logger.error(f"AI security analysis failed: {e}")
            return {"issues": [], "error": str(e)}

    async def _analyze_performance(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Analyze code for performance issues.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Performance analysis results
        """
        logger.info("⚡ Analyzing performance...")

        try:
            prompt = f"""Analyze this {language} code for performance issues:

```{language}
{code[:1500]}
```

Identify performance concerns:
1. **Complexity**: O(n²) or worse algorithms
2. **Memory**: Unnecessary allocations, memory leaks
3. **I/O**: Blocking operations, missing async
4. **Database**: N+1 queries, missing indexes
5. **Caching**: Missing caching opportunities

For each issue:
- Type (complexity/memory/io/database/caching)
- Severity (critical/high/medium/low)
- Description
- Current complexity (if applicable)
- Suggested optimization
- Expected improvement

Format as JSON:
{{
    "issues": [
        {{
            "type": "complexity",
            "severity": "high",
            "description": "Nested loops cause O(n²) complexity",
            "current_complexity": "O(n²)",
            "optimization": "Use hash map for O(n) lookup",
            "improvement": "O(n²) → O(n)"
        }}
    ]
}}
"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.2,
                max_tokens=1500
            )

            content = response.choices[0].message.content.strip()

            # Extract JSON
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                analysis = json.loads(content[start:end])
                return analysis
            else:
                return {"issues": []}

        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {"issues": [], "error": str(e)}

    async def _check_best_practices(
        self,
        code: str,
        language: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check code against best practices.

        Args:
            code: Code to check
            language: Programming language
            context: Additional context

        Returns:
            Best practices check results
        """
        logger.info("📋 Checking best practices...")

        practices = self.best_practices.get(language.lower(), [])

        try:
            prompt = f"""Review this {language} code against best practices:

```{language}
{code[:1500]}
```

**Best Practices to Check:**
{chr(10).join([f'{i+1}. {p}' for i, p in enumerate(practices[:10])])}

For each violation found:
- Practice violated
- Severity (high/medium/low)
- Location (line number)
- Current code
- Suggested fix
- Rationale

Format as JSON:
{{
    "violations": [
        {{
            "practice": "Use type hints",
            "severity": "medium",
            "line": 5,
            "current": "def process(data):",
            "suggested": "def process(data: List[str]) -> bool:",
            "rationale": "Type hints improve code clarity and enable static analysis"
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
                analysis = json.loads(content[start:end])
                return analysis
            else:
                return {"violations": []}

        except Exception as e:
            logger.error(f"Best practices check failed: {e}")
            return {"violations": [], "error": str(e)}

    async def _detect_code_smells(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Detect code smells and anti-patterns.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Code smells detection results
        """
        logger.info("👃 Detecting code smells...")

        try:
            prompt = f"""Identify code smells and anti-patterns in this {language} code:

```{language}
{code[:1500]}
```

Look for these code smells:
1. **Long Functions**: Functions > 50 lines
2. **Complex Conditions**: Deeply nested if/else
3. **Duplicate Code**: Repeated logic
4. **Large Classes**: Classes with too many responsibilities
5. **Magic Numbers**: Unexplained constants
6. **Dead Code**: Unused variables/functions
7. **Tight Coupling**: High dependencies
8. **God Objects**: Classes that do too much

For each smell:
- Type
- Severity (high/medium/low)
- Location
- Description
- Refactoring suggestion

Format as JSON:
{{
    "smells": [
        {{
            "type": "long_function",
            "severity": "medium",
            "location": "lines 10-85",
            "description": "Function has 75 lines, should be < 50",
            "refactoring": "Split into smaller functions: parse_data(), validate_data(), process_data()"
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
                analysis = json.loads(content[start:end])
                return analysis
            else:
                return {"smells": []}

        except Exception as e:
            logger.error(f"Code smell detection failed: {e}")
            return {"smells": [], "error": str(e)}

    async def _generate_refactoring_suggestions(
        self,
        code: str,
        language: str,
        review_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate prioritized refactoring suggestions.

        Args:
            code: Original code
            language: Programming language
            review_results: Results from all review checks

        Returns:
            Prioritized refactoring suggestions
        """
        # Collect all issues
        all_issues = []

        # Add security issues
        if "security" in review_results:
            for issue in review_results["security"].get("pattern_based_issues", []):
                all_issues.append({
                    "category": "security",
                    "severity": issue["severity"],
                    "description": issue["description"],
                    "line": issue.get("line")
                })
            for issue in review_results["security"].get("ai_analysis", {}).get("issues", []):
                all_issues.append({
                    "category": "security",
                    "severity": issue["severity"],
                    "description": issue["description"],
                    "remediation": issue.get("remediation")
                })

        # Add performance issues
        if "performance" in review_results:
            for issue in review_results["performance"].get("issues", []):
                all_issues.append({
                    "category": "performance",
                    "severity": issue["severity"],
                    "description": issue["description"],
                    "optimization": issue.get("optimization")
                })

        # Prioritize issues
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_issues.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 3))

        # Top 10 suggestions
        suggestions = all_issues[:10]

        return {
            "total_suggestions": len(all_issues),
            "top_priority": suggestions,
            "by_category": self._group_by_category(all_issues)
        }

    def _group_by_category(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group issues by category."""
        categories = {}
        for issue in issues:
            cat = issue.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1
        return categories

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate overall review summary.

        Args:
            results: All review results

        Returns:
            Summary with score and priorities
        """
        total_issues = 0
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        # Count security issues
        if "security" in results:
            total_issues += results["security"].get("total_issues", 0)
            for issue in results["security"].get("pattern_based_issues", []):
                severity = issue.get("severity", "low")
                by_severity[severity] = by_severity.get(severity, 0) + 1

        # Count performance issues
        if "performance" in results:
            perf_issues = results["performance"].get("issues", [])
            total_issues += len(perf_issues)
            for issue in perf_issues:
                severity = issue.get("severity", "low")
                by_severity[severity] = by_severity.get(severity, 0) + 1

        # Count best practice violations
        if "best_practices" in results:
            violations = results["best_practices"].get("violations", [])
            total_issues += len(violations)
            for violation in violations:
                severity = violation.get("severity", "low")
                by_severity[severity] = by_severity.get(severity, 0) + 1

        # Count code smells
        if "code_smells" in results:
            smells = results["code_smells"].get("smells", [])
            total_issues += len(smells)
            for smell in smells:
                severity = smell.get("severity", "low")
                by_severity[severity] = by_severity.get(severity, 0) + 1

        # Calculate quality score (0-100)
        # Deduct points based on severity
        score = 100
        score -= by_severity["critical"] * 20
        score -= by_severity["high"] * 10
        score -= by_severity["medium"] * 5
        score -= by_severity["low"] * 2
        score = max(0, score)

        # Determine overall grade
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        return {
            "total_issues": total_issues,
            "by_severity": by_severity,
            "quality_score": score,
            "grade": grade,
            "recommendation": self._get_recommendation(score, by_severity)
        }

    def _get_recommendation(self, score: int, by_severity: Dict[str, int]) -> str:
        """Get recommendation based on score and issues."""
        if by_severity["critical"] > 0:
            return "CRITICAL: Address security vulnerabilities immediately before deployment"
        elif score >= 90:
            return "EXCELLENT: Code meets high quality standards, minor improvements possible"
        elif score >= 80:
            return "GOOD: Code is production-ready with some improvements recommended"
        elif score >= 70:
            return "FAIR: Address high-priority issues before deployment"
        elif score >= 60:
            return "NEEDS WORK: Significant refactoring recommended"
        else:
            return "POOR: Major issues found, extensive refactoring required"

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get review statistics.

        Returns:
            Statistics dictionary
        """
        if not self.review_history:
            return {
                "total_reviews": 0,
                "languages": {},
                "average_issues": 0
            }

        lang_counts = {}
        total_issues = 0

        for record in self.review_history:
            lang = record.get("language", "unknown")
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
            total_issues += record.get("issues_found", 0)

        return {
            "total_reviews": len(self.review_history),
            "languages": lang_counts,
            "average_issues": total_issues / len(self.review_history),
            "recent_reviews": [
                {
                    "language": r["language"],
                    "issues": r["issues_found"],
                    "timestamp": r["timestamp"]
                }
                for r in self.review_history[-5:]
            ]
        }


# Global singleton instance
review_agent = ReviewAgent()
