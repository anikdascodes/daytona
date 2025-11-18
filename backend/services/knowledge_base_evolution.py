"""
Knowledge Base Evolution - Persistent Knowledge Storage and Evolution

Capabilities:
- Persistent knowledge storage
- Knowledge evolution over time
- Knowledge pruning and consolidation
- Version control for knowledge
- Import/export capabilities

Part of Phase 4: Task 4.5 - Advanced Learning Systems
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from utils.logger import logger


class KnowledgeState(Enum):
    """State of knowledge in the evolution lifecycle."""
    EXPERIMENTAL = "experimental"  # New, needs validation
    VALIDATED = "validated"        # Proven to work
    DEPRECATED = "deprecated"      # No longer recommended
    ARCHIVED = "archived"          # Historical record


@dataclass
class KnowledgeVersion:
    """Represents a version of knowledge."""
    version: int
    content: Dict[str, Any]
    updated_at: datetime
    changes: str
    updated_by: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "content": self.content,
            "updated_at": self.updated_at.isoformat(),
            "changes": self.changes,
            "updated_by": self.updated_by
        }


@dataclass
class EvolvingKnowledge:
    """Represents evolving knowledge with version history."""
    knowledge_id: str
    category: str
    title: str

    # Current version
    current_version: int
    current_content: Dict[str, Any]

    # State
    state: KnowledgeState

    # Version history
    versions: List[KnowledgeVersion] = field(default_factory=list)

    # Usage tracking
    usage_count: int = 0
    last_used: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "knowledge_id": self.knowledge_id,
            "category": self.category,
            "title": self.title,
            "current_version": self.current_version,
            "current_content": self.current_content,
            "state": self.state.value,
            "versions": [v.to_dict() for v in self.versions],
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags
        }


class KnowledgeBaseEvolution:
    """
    Knowledge Base Evolution System.

    Manages persistent storage and evolution of agent knowledge.

    Capabilities:
    - Store knowledge persistently
    - Track knowledge versions
    - Evolve knowledge based on usage
    - Prune outdated knowledge
    - Import/export knowledge
    """

    def __init__(self, storage_path: str = "/workspace/knowledge_base"):
        """Initialize knowledge base evolution."""
        self.storage_path = storage_path
        self.knowledge_base: Dict[str, EvolvingKnowledge] = {}
        self.knowledge_counter = 0

        # Categories for organization
        self.categories = {
            "patterns": "Successful patterns and approaches",
            "techniques": "Proven techniques and methods",
            "solutions": "Solutions to common problems",
            "best_practices": "Best practices and guidelines",
            "warnings": "Warnings and pitfalls to avoid",
            "optimizations": "Performance optimizations",
            "strategies": "Execution strategies"
        }

        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)

        logger.info(f"📚 KnowledgeBaseEvolution initialized (storage: {storage_path})")

    def add_knowledge(
        self,
        category: str,
        title: str,
        content: Dict[str, Any],
        tags: Optional[List[str]] = None,
        state: KnowledgeState = KnowledgeState.EXPERIMENTAL
    ) -> EvolvingKnowledge:
        """
        Add new knowledge to the base.

        Args:
            category: Knowledge category
            title: Knowledge title
            content: Knowledge content
            tags: Tags for categorization
            state: Initial state

        Returns:
            EvolvingKnowledge
        """
        self.knowledge_counter += 1
        knowledge_id = f"{category}_{self.knowledge_counter}_{datetime.now().strftime('%Y%m%d')}"

        knowledge = EvolvingKnowledge(
            knowledge_id=knowledge_id,
            category=category,
            title=title,
            current_version=1,
            current_content=content,
            state=state,
            tags=tags or []
        )

        # Add initial version
        version = KnowledgeVersion(
            version=1,
            content=content,
            updated_at=datetime.now(),
            changes="Initial creation",
            updated_by="system"
        )
        knowledge.versions.append(version)

        self.knowledge_base[knowledge_id] = knowledge

        logger.info(f"📝 Added knowledge: {title} ({category}, {state.value})")

        return knowledge

    def update_knowledge(
        self,
        knowledge_id: str,
        new_content: Dict[str, Any],
        changes: str,
        updated_by: str = "system"
    ) -> Optional[EvolvingKnowledge]:
        """
        Update existing knowledge with new version.

        Args:
            knowledge_id: Knowledge ID
            new_content: New content
            changes: Description of changes
            updated_by: Who updated it

        Returns:
            Updated EvolvingKnowledge or None
        """
        knowledge = self.knowledge_base.get(knowledge_id)
        if not knowledge:
            logger.warning(f"Knowledge {knowledge_id} not found")
            return None

        # Create new version
        new_version = knowledge.current_version + 1
        version = KnowledgeVersion(
            version=new_version,
            content=new_content,
            updated_at=datetime.now(),
            changes=changes,
            updated_by=updated_by
        )

        knowledge.versions.append(version)
        knowledge.current_version = new_version
        knowledge.current_content = new_content
        knowledge.updated_at = datetime.now()

        logger.info(f"📝 Updated knowledge: {knowledge.title} (v{new_version})")

        return knowledge

    def record_usage(
        self,
        knowledge_id: str,
        success: bool
    ):
        """
        Record usage of knowledge.

        Args:
            knowledge_id: Knowledge ID
            success: Whether usage was successful
        """
        knowledge = self.knowledge_base.get(knowledge_id)
        if not knowledge:
            return

        knowledge.usage_count += 1
        knowledge.last_used = datetime.now()

        if success:
            knowledge.success_count += 1
        else:
            knowledge.failure_count += 1

        # Evolve state based on usage
        self._evolve_state(knowledge)

    def _evolve_state(self, knowledge: EvolvingKnowledge):
        """Evolve knowledge state based on usage statistics."""
        total_usage = knowledge.success_count + knowledge.failure_count

        if total_usage < 3:
            # Keep as experimental until we have enough data
            return

        success_rate = knowledge.success_count / total_usage

        # Promote to validated if high success rate
        if knowledge.state == KnowledgeState.EXPERIMENTAL and success_rate >= 0.8 and total_usage >= 5:
            knowledge.state = KnowledgeState.VALIDATED
            logger.info(f"✅ Knowledge promoted to VALIDATED: {knowledge.title} ({success_rate*100:.0f}% success)")

        # Deprecate if low success rate
        elif success_rate < 0.4 and total_usage >= 5:
            if knowledge.state != KnowledgeState.DEPRECATED:
                knowledge.state = KnowledgeState.DEPRECATED
                logger.warning(f"⚠️  Knowledge deprecated: {knowledge.title} ({success_rate*100:.0f}% success)")

    def get_knowledge(
        self,
        category: Optional[str] = None,
        state: Optional[KnowledgeState] = None,
        tags: Optional[List[str]] = None,
        min_success_rate: float = 0.0
    ) -> List[EvolvingKnowledge]:
        """
        Get knowledge from the base with filters.

        Args:
            category: Filter by category
            state: Filter by state
            tags: Filter by tags
            min_success_rate: Minimum success rate

        Returns:
            List of matching knowledge items
        """
        results = []

        for knowledge in self.knowledge_base.values():
            # Filter by category
            if category and knowledge.category != category:
                continue

            # Filter by state
            if state and knowledge.state != state:
                continue

            # Filter by tags
            if tags and not any(tag in knowledge.tags for tag in tags):
                continue

            # Filter by success rate
            total_usage = knowledge.success_count + knowledge.failure_count
            if total_usage > 0:
                success_rate = knowledge.success_count / total_usage
                if success_rate < min_success_rate:
                    continue

            results.append(knowledge)

        # Sort by usage count and success rate
        results.sort(
            key=lambda k: (
                k.usage_count,
                k.success_count / max(k.success_count + k.failure_count, 1)
            ),
            reverse=True
        )

        return results

    def get_validated_knowledge(self) -> List[EvolvingKnowledge]:
        """Get all validated knowledge."""
        return self.get_knowledge(state=KnowledgeState.VALIDATED)

    def get_best_practices(self, limit: int = 10) -> List[EvolvingKnowledge]:
        """Get top best practices."""
        best_practices = self.get_knowledge(
            category="best_practices",
            state=KnowledgeState.VALIDATED,
            min_success_rate=0.8
        )
        return best_practices[:limit]

    def prune_outdated_knowledge(self, days_unused: int = 90):
        """
        Prune knowledge that hasn't been used recently.

        Args:
            days_unused: Days since last use to consider outdated
        """
        cutoff_date = datetime.now() - timedelta(days=days_unused)
        pruned = []

        for knowledge_id, knowledge in list(self.knowledge_base.items()):
            # Don't prune validated knowledge
            if knowledge.state == KnowledgeState.VALIDATED:
                continue

            # Check if unused for too long
            if knowledge.last_used and knowledge.last_used < cutoff_date:
                # Archive instead of delete
                if knowledge.state != KnowledgeState.ARCHIVED:
                    knowledge.state = KnowledgeState.ARCHIVED
                    pruned.append(knowledge_id)

        if pruned:
            logger.info(f"🗑️  Archived {len(pruned)} outdated knowledge items")

        return pruned

    def consolidate_knowledge(self):
        """
        Consolidate similar knowledge items.

        Identifies and merges duplicate or very similar knowledge.
        """
        consolidated_count = 0

        # Group by category and title similarity
        for category in self.categories.keys():
            category_knowledge = self.get_knowledge(category=category)

            # Simple consolidation: exact title matches
            title_groups = {}
            for knowledge in category_knowledge:
                title_lower = knowledge.title.lower()
                if title_lower in title_groups:
                    title_groups[title_lower].append(knowledge)
                else:
                    title_groups[title_lower] = [knowledge]

            # Merge groups with multiple items
            for title, group in title_groups.items():
                if len(group) > 1:
                    # Keep the one with most usage
                    primary = max(group, key=lambda k: k.usage_count)

                    # Merge stats from others
                    for other in group:
                        if other.knowledge_id != primary.knowledge_id:
                            primary.usage_count += other.usage_count
                            primary.success_count += other.success_count
                            primary.failure_count += other.failure_count

                            # Remove the duplicate
                            del self.knowledge_base[other.knowledge_id]
                            consolidated_count += 1

        if consolidated_count > 0:
            logger.info(f"🔄 Consolidated {consolidated_count} duplicate knowledge items")

        return consolidated_count

    def export_to_file(self, filename: Optional[str] = None) -> str:
        """
        Export knowledge base to JSON file.

        Args:
            filename: Output filename (optional)

        Returns:
            Path to exported file
        """
        if not filename:
            filename = f"knowledge_base_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = os.path.join(self.storage_path, filename)

        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_items": len(self.knowledge_base),
            "categories": self.categories,
            "knowledge": {
                knowledge_id: knowledge.to_dict()
                for knowledge_id, knowledge in self.knowledge_base.items()
            }
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"💾 Exported {len(self.knowledge_base)} knowledge items to {filepath}")

        return filepath

    def import_from_file(self, filepath: str) -> int:
        """
        Import knowledge base from JSON file.

        Args:
            filepath: Path to import file

        Returns:
            Number of items imported
        """
        if not os.path.exists(filepath):
            logger.error(f"Import file not found: {filepath}")
            return 0

        with open(filepath, 'r') as f:
            import_data = json.load(f)

        knowledge_data = import_data.get("knowledge", {})
        imported_count = 0

        for knowledge_id, data in knowledge_data.items():
            # Convert string dates back to datetime
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
            if data.get("last_used"):
                data["last_used"] = datetime.fromisoformat(data["last_used"])

            data["state"] = KnowledgeState(data["state"])

            # Convert version data
            versions = []
            for v_data in data["versions"]:
                v_data["updated_at"] = datetime.fromisoformat(v_data["updated_at"])
                versions.append(KnowledgeVersion(**v_data))
            data["versions"] = versions

            knowledge = EvolvingKnowledge(**data)
            self.knowledge_base[knowledge_id] = knowledge
            imported_count += 1

        logger.info(f"📥 Imported {imported_count} knowledge items from {filepath}")

        return imported_count

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        total = len(self.knowledge_base)

        by_state = {
            state.value: len([k for k in self.knowledge_base.values() if k.state == state])
            for state in KnowledgeState
        }

        by_category = {
            category: len([k for k in self.knowledge_base.values() if k.category == category])
            for category in self.categories.keys()
        }

        total_usage = sum(k.usage_count for k in self.knowledge_base.values())
        total_successes = sum(k.success_count for k in self.knowledge_base.values())
        total_failures = sum(k.failure_count for k in self.knowledge_base.values())

        return {
            "total_knowledge_items": total,
            "by_state": by_state,
            "by_category": by_category,
            "total_usage": total_usage,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "overall_success_rate": (
                total_successes / (total_successes + total_failures)
                if (total_successes + total_failures) > 0 else 0
            ),
            "validated_knowledge": by_state.get("validated", 0),
            "storage_path": self.storage_path
        }


# Global singleton instance
knowledge_base_evolution = KnowledgeBaseEvolution()
