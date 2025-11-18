"""
Error Analysis Service - Advanced error analysis and pattern recognition.

Capabilities:
- Error pattern detection
- Root cause analysis
- Automated fix suggestions
- Prevention strategies
- Learning from mistakes
- Error categorization

Part of Phase 3: Advanced Learning
"""
import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
from litellm import acompletion
from config import settings
from utils.logger import logger


@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    error_id: str
    timestamp: datetime
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    action_attempted: Optional[str] = None
    agent_state: Optional[str] = None
    task_description: Optional[str] = None
    iteration: int = 0

    # Analysis fields
    root_cause: Optional[str] = None
    fix_suggestions: List[str] = field(default_factory=list)
    prevention_strategy: Optional[str] = None
    pattern_id: Optional[str] = None
    similar_errors: List[str] = field(default_factory=list)
    learned: bool = False


@dataclass
class ErrorPattern:
    """Detected error pattern."""
    pattern_id: str
    pattern_type: str
    description: str
    occurrences: int
    first_seen: datetime
    last_seen: datetime
    error_ids: List[str] = field(default_factory=list)
    common_root_causes: List[str] = field(default_factory=list)
    effective_fixes: List[str] = field(default_factory=list)
    prevention_strategies: List[str] = field(default_factory=list)


class ErrorAnalysisService:
    """
    Advanced error analysis and learning system.

    Features:
    - Track all errors with context
    - Detect recurring patterns
    - Analyze root causes
    - Suggest fixes automatically
    - Recommend prevention strategies
    - Learn from successful fixes
    """

    def __init__(self):
        """Initialize error analysis service."""
        self.errors: Dict[str, ErrorRecord] = {}
        self.patterns: Dict[str, ErrorPattern] = {}
        self.error_counter = 0
        self.pattern_counter = 0

        # Error type categories
        self.error_categories = {
            "syntax": ["SyntaxError", "IndentationError", "TabError"],
            "runtime": ["RuntimeError", "ValueError", "TypeError", "AttributeError"],
            "import": ["ImportError", "ModuleNotFoundError"],
            "file": ["FileNotFoundError", "PermissionError", "IOError"],
            "network": ["ConnectionError", "TimeoutError", "HTTPError"],
            "command": ["CommandNotFoundError", "CalledProcessError"],
            "api": ["APIError", "AuthenticationError", "RateLimitError"]
        }

        logger.info("ErrorAnalysisService initialized")

    async def record_error(
        self,
        error_message: str,
        error_type: str = "Unknown",
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        action_attempted: Optional[str] = None,
        agent_state: Optional[str] = None,
        task_description: Optional[str] = None,
        iteration: int = 0
    ) -> ErrorRecord:
        """
        Record an error occurrence.

        Args:
            error_message: Error message
            error_type: Type of error
            stack_trace: Stack trace if available
            context: Additional context
            action_attempted: What action was being attempted
            agent_state: Agent state when error occurred
            task_description: Description of task
            iteration: Iteration number

        Returns:
            ErrorRecord with analysis
        """
        self.error_counter += 1
        error_id = f"error_{self.error_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create error record
        error = ErrorRecord(
            error_id=error_id,
            timestamp=datetime.now(),
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            context=context or {},
            action_attempted=action_attempted,
            agent_state=agent_state,
            task_description=task_description,
            iteration=iteration
        )

        self.errors[error_id] = error

        logger.warning(f"❌ Error recorded: {error_id} - {error_type}: {error_message[:100]}")

        # Analyze error asynchronously
        await self._analyze_error(error)

        # Detect patterns
        await self._detect_patterns(error)

        return error

    async def _analyze_error(self, error: ErrorRecord) -> None:
        """
        Analyze an error to determine root cause and suggestions.

        Args:
            error: ErrorRecord to analyze
        """
        try:
            # Build context for LLM
            context = f"""Error Analysis Request:

Error Type: {error.error_type}
Error Message: {error.error_message}
Action Attempted: {error.action_attempted or 'Unknown'}
Agent State: {error.agent_state or 'Unknown'}
Task: {error.task_description or 'Unknown'}
Iteration: {error.iteration}

{f'Stack Trace:\n{error.stack_trace}' if error.stack_trace else ''}

{f'Context:\n{json.dumps(error.context, indent=2)}' if error.context else ''}

Analyze this error and provide:
1. Root cause analysis (why did this happen?)
2. Fix suggestions (3-5 specific steps to fix)
3. Prevention strategy (how to avoid in future)

Return JSON format:
{{
    "root_cause": "explanation of root cause",
    "fix_suggestions": ["fix 1", "fix 2", "fix 3"],
    "prevention_strategy": "strategy to prevent this error"
}}"""

            # Call LLM for analysis
            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": context}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.3,  # Lower temperature for analysis
                max_tokens=1500
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]
                analysis = json.loads(json_str)

                # Update error record
                error.root_cause = analysis.get("root_cause", "Unknown")
                error.fix_suggestions = analysis.get("fix_suggestions", [])
                error.prevention_strategy = analysis.get("prevention_strategy", "")
                error.learned = True

                logger.info(f"✅ Error analyzed: {error.error_id}")
                logger.info(f"   Root cause: {error.root_cause[:100]}...")
                logger.info(f"   Suggestions: {len(error.fix_suggestions)} fixes")

        except Exception as e:
            logger.error(f"Failed to analyze error {error.error_id}: {e}")
            error.root_cause = "Analysis failed"
            error.fix_suggestions = ["Manual investigation required"]
            error.prevention_strategy = "Review error logs"

    async def _detect_patterns(self, error: ErrorRecord) -> None:
        """
        Detect if this error matches existing patterns.

        Args:
            error: ErrorRecord to check for patterns
        """
        # Find similar errors
        similar = self._find_similar_errors(error)

        if similar:
            error.similar_errors = [e.error_id for e in similar]
            logger.info(f"   Found {len(similar)} similar errors")

            # Check if pattern exists
            pattern = self._find_matching_pattern(error, similar)

            if pattern:
                # Update existing pattern
                pattern.occurrences += 1
                pattern.last_seen = error.timestamp
                pattern.error_ids.append(error.error_id)
                error.pattern_id = pattern.pattern_id

                logger.info(f"   Matched pattern: {pattern.pattern_id} ({pattern.occurrences} occurrences)")
            else:
                # Create new pattern
                pattern = await self._create_pattern(error, similar)
                error.pattern_id = pattern.pattern_id

                logger.info(f"   Created new pattern: {pattern.pattern_id}")

    def _find_similar_errors(self, error: ErrorRecord, threshold: float = 0.7) -> List[ErrorRecord]:
        """
        Find similar errors using text similarity.

        Args:
            error: ErrorRecord to compare
            threshold: Similarity threshold (0.0-1.0)

        Returns:
            List of similar ErrorRecords
        """
        similar = []

        for other_error in self.errors.values():
            if other_error.error_id == error.error_id:
                continue

            # Check if same error type
            if error.error_type != other_error.error_type:
                continue

            # Simple similarity: compare error messages
            similarity = self._text_similarity(
                error.error_message,
                other_error.error_message
            )

            if similarity >= threshold:
                similar.append(other_error)

        return similar

    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity (Jaccard similarity).

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0.0-1.0)
        """
        # Tokenize
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        # Jaccard similarity
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _find_matching_pattern(
        self,
        error: ErrorRecord,
        similar_errors: List[ErrorRecord]
    ) -> Optional[ErrorPattern]:
        """
        Find if error matches existing pattern.

        Args:
            error: ErrorRecord to match
            similar_errors: Similar errors

        Returns:
            Matching ErrorPattern or None
        """
        for pattern in self.patterns.values():
            # Check if error type matches
            if pattern.pattern_type != error.error_type:
                continue

            # Check if any similar errors are in this pattern
            for similar in similar_errors:
                if similar.error_id in pattern.error_ids:
                    return pattern

        return None

    async def _create_pattern(
        self,
        error: ErrorRecord,
        similar_errors: List[ErrorRecord]
    ) -> ErrorPattern:
        """
        Create a new error pattern.

        Args:
            error: ErrorRecord
            similar_errors: Similar errors

        Returns:
            New ErrorPattern
        """
        self.pattern_counter += 1
        pattern_id = f"pattern_{self.pattern_counter}"

        # Categorize error type
        category = self._categorize_error(error.error_type)

        # Create pattern description
        description = await self._generate_pattern_description(error, similar_errors)

        pattern = ErrorPattern(
            pattern_id=pattern_id,
            pattern_type=error.error_type,
            description=description,
            occurrences=1 + len(similar_errors),
            first_seen=error.timestamp,
            last_seen=error.timestamp,
            error_ids=[error.error_id] + [e.error_id for e in similar_errors]
        )

        # Collect common elements
        all_errors = [error] + similar_errors
        pattern.common_root_causes = list(set(
            e.root_cause for e in all_errors if e.root_cause
        ))

        # Collect effective fixes from learned errors
        for e in all_errors:
            if e.fix_suggestions:
                pattern.effective_fixes.extend(e.fix_suggestions)
            if e.prevention_strategy:
                pattern.prevention_strategies.append(e.prevention_strategy)

        # Remove duplicates
        pattern.effective_fixes = list(set(pattern.effective_fixes))
        pattern.prevention_strategies = list(set(pattern.prevention_strategies))

        self.patterns[pattern_id] = pattern

        return pattern

    def _categorize_error(self, error_type: str) -> str:
        """
        Categorize error type.

        Args:
            error_type: Error type string

        Returns:
            Category name
        """
        for category, types in self.error_categories.items():
            if any(t in error_type for t in types):
                return category
        return "other"

    async def _generate_pattern_description(
        self,
        error: ErrorRecord,
        similar_errors: List[ErrorRecord]
    ) -> str:
        """
        Generate a description for the error pattern.

        Args:
            error: ErrorRecord
            similar_errors: Similar errors

        Returns:
            Pattern description
        """
        # Simple description for now
        # In production, use LLM to generate better descriptions
        category = self._categorize_error(error.error_type)

        return f"{category.title()} error pattern: {error.error_type} - occurs during {error.action_attempted or 'various actions'}"

    def get_error_by_id(self, error_id: str) -> Optional[ErrorRecord]:
        """Get error record by ID."""
        return self.errors.get(error_id)

    def get_pattern_by_id(self, pattern_id: str) -> Optional[ErrorPattern]:
        """Get pattern by ID."""
        return self.patterns.get(pattern_id)

    def get_recent_errors(self, limit: int = 10) -> List[ErrorRecord]:
        """
        Get most recent errors.

        Args:
            limit: Maximum number to return

        Returns:
            List of recent ErrorRecords
        """
        sorted_errors = sorted(
            self.errors.values(),
            key=lambda e: e.timestamp,
            reverse=True
        )
        return sorted_errors[:limit]

    def get_frequent_patterns(self, limit: int = 5) -> List[ErrorPattern]:
        """
        Get most frequent error patterns.

        Args:
            limit: Maximum number to return

        Returns:
            List of frequent ErrorPatterns
        """
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.occurrences,
            reverse=True
        )
        return sorted_patterns[:limit]

    async def suggest_fix(self, error_id: str) -> Dict[str, Any]:
        """
        Get fix suggestions for an error.

        Args:
            error_id: Error ID

        Returns:
            Fix suggestions with context
        """
        error = self.get_error_by_id(error_id)
        if not error:
            return {"success": False, "error": "Error not found"}

        # Get suggestions from error analysis
        suggestions = {
            "error_id": error_id,
            "error_type": error.error_type,
            "root_cause": error.root_cause,
            "fix_suggestions": error.fix_suggestions,
            "prevention_strategy": error.prevention_strategy
        }

        # Add pattern-based suggestions if available
        if error.pattern_id:
            pattern = self.get_pattern_by_id(error.pattern_id)
            if pattern:
                suggestions["pattern_id"] = pattern.pattern_id
                suggestions["pattern_occurrences"] = pattern.occurrences
                suggestions["effective_fixes"] = pattern.effective_fixes[:5]
                suggestions["prevention_strategies"] = pattern.prevention_strategies[:3]

        return {"success": True, **suggestions}

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get error analysis statistics.

        Returns:
            Statistics dictionary
        """
        # Count by category
        category_counts = defaultdict(int)
        for error in self.errors.values():
            category = self._categorize_error(error.error_type)
            category_counts[category] += 1

        # Count analyzed vs unanalyzed
        analyzed = sum(1 for e in self.errors.values() if e.learned)

        # Most common error types
        type_counts = defaultdict(int)
        for error in self.errors.values():
            type_counts[error.error_type] += 1

        top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_errors": len(self.errors),
            "total_patterns": len(self.patterns),
            "errors_analyzed": analyzed,
            "analysis_rate": (analyzed / len(self.errors) * 100) if self.errors else 0,
            "errors_by_category": dict(category_counts),
            "top_error_types": [{"type": t, "count": c} for t, c in top_types],
            "most_frequent_patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "type": p.pattern_type,
                    "occurrences": p.occurrences,
                    "description": p.description
                }
                for p in self.get_frequent_patterns(3)
            ]
        }

    async def generate_prevention_report(self) -> str:
        """
        Generate a report on how to prevent common errors.

        Returns:
            Prevention report as markdown
        """
        report = ["# Error Prevention Report\n"]
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        stats = self.get_statistics()
        report.append(f"## Overview\n")
        report.append(f"- Total errors tracked: {stats['total_errors']}")
        report.append(f"- Patterns identified: {stats['total_patterns']}")
        report.append(f"- Analysis coverage: {stats['analysis_rate']:.1f}%\n")

        # Top patterns
        report.append("## Most Frequent Error Patterns\n")
        for pattern in self.get_frequent_patterns(5):
            report.append(f"### {pattern.pattern_id}: {pattern.pattern_type}")
            report.append(f"- Occurrences: {pattern.occurrences}")
            report.append(f"- Description: {pattern.description}")

            if pattern.prevention_strategies:
                report.append("- **Prevention:**")
                for strategy in pattern.prevention_strategies[:3]:
                    report.append(f"  - {strategy}")
            report.append("")

        # Category breakdown
        report.append("## Errors by Category\n")
        for category, count in stats['errors_by_category'].items():
            report.append(f"- **{category.title()}**: {count} errors")

        return "\n".join(report)


# Global singleton instance
error_analyzer = ErrorAnalysisService()
