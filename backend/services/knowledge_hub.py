"""
Knowledge Hub - Cross-Agent Knowledge Sharing System

Capabilities:
- Real-time knowledge sharing between agents
- Broadcasting important discoveries
- Collaborative problem solving
- Knowledge synchronization
- Cross-agent learning

Part of Phase 4: Task 4.5 - Advanced Learning Systems
"""
import asyncio
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
from utils.logger import logger


class KnowledgeType(Enum):
    """Types of knowledge that can be shared."""
    SOLUTION = "solution"               # Solution to a problem
    TECHNIQUE = "technique"             # Useful technique
    PATTERN = "pattern"                 # Discovered pattern
    WARNING = "warning"                 # Warning about pitfalls
    OPTIMIZATION = "optimization"       # Optimization opportunity
    DISCOVERY = "discovery"             # New discovery
    QUESTION = "question"               # Question for other agents
    ANSWER = "answer"                   # Answer to a question


class KnowledgePriority(Enum):
    """Priority levels for knowledge items."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class KnowledgeItem:
    """Represents a piece of knowledge to be shared."""
    knowledge_id: str
    knowledge_type: KnowledgeType
    priority: KnowledgePriority

    # Content
    title: str
    content: str
    context: Dict[str, Any]

    # Source
    source_agent: str
    source_interaction_id: Optional[str] = None

    # Distribution
    target_agents: Set[str] = field(default_factory=lambda: {"all"})  # "all" means broadcast
    subscribers: Set[str] = field(default_factory=set)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    tags: Set[str] = field(default_factory=set)

    # Engagement
    views: int = 0
    useful_votes: int = 0
    not_useful_votes: int = 0
    applied_count: int = 0  # How many times this knowledge was applied

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['knowledge_type'] = self.knowledge_type.value
        data['priority'] = self.priority.value
        data['created_at'] = self.created_at.isoformat()
        data['target_agents'] = list(self.target_agents)
        data['subscribers'] = list(self.subscribers)
        data['tags'] = list(self.tags)
        return data


@dataclass
class KnowledgeChannel:
    """Represents a knowledge channel for specific topics."""
    channel_id: str
    name: str
    description: str
    subscribers: Set[str] = field(default_factory=set)
    knowledge_items: List[str] = field(default_factory=list)  # Knowledge IDs
    created_at: datetime = field(default_factory=datetime.now)


class KnowledgeHub:
    """
    Central hub for cross-agent knowledge sharing.

    Capabilities:
    - Share knowledge between agents in real-time
    - Subscribe to specific knowledge channels
    - Broadcast important discoveries
    - Query knowledge from other agents
    - Collaborative learning
    """

    def __init__(self):
        """Initialize knowledge hub."""
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self.channels: Dict[str, KnowledgeChannel] = {}
        self.knowledge_counter = 0

        # Subscriptions: agent_type -> set of channel_ids
        self.agent_subscriptions: Dict[str, Set[str]] = defaultdict(set)

        # Listeners: agent_type -> list of callback functions
        self.knowledge_listeners: Dict[str, List[Callable]] = defaultdict(list)

        # Create default channels
        self._create_default_channels()

        logger.info("🌐 KnowledgeHub initialized")

    def _create_default_channels(self):
        """Create default knowledge channels."""
        default_channels = [
            {
                "channel_id": "general",
                "name": "General Knowledge",
                "description": "General knowledge and discoveries"
            },
            {
                "channel_id": "solutions",
                "name": "Solutions",
                "description": "Successful solutions to problems"
            },
            {
                "channel_id": "warnings",
                "name": "Warnings",
                "description": "Warnings about common pitfalls and mistakes"
            },
            {
                "channel_id": "optimizations",
                "name": "Optimizations",
                "description": "Performance and efficiency optimizations"
            },
            {
                "channel_id": "code",
                "name": "Code Knowledge",
                "description": "Code-related knowledge and patterns"
            },
            {
                "channel_id": "testing",
                "name": "Testing",
                "description": "Testing strategies and techniques"
            },
            {
                "channel_id": "debugging",
                "name": "Debugging",
                "description": "Debugging techniques and error resolutions"
            }
        ]

        for channel_info in default_channels:
            channel = KnowledgeChannel(**channel_info)
            self.channels[channel.channel_id] = channel

    async def share_knowledge(
        self,
        source_agent: str,
        knowledge_type: KnowledgeType,
        title: str,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        priority: KnowledgePriority = KnowledgePriority.MEDIUM,
        target_agents: Optional[Set[str]] = None,
        tags: Optional[Set[str]] = None,
        channel_id: str = "general"
    ) -> KnowledgeItem:
        """
        Share knowledge with other agents.

        Args:
            source_agent: Agent sharing the knowledge
            knowledge_type: Type of knowledge
            title: Knowledge title
            content: Knowledge content
            context: Additional context
            priority: Priority level
            target_agents: Specific agents to target (None = broadcast)
            tags: Tags for categorization
            channel_id: Channel to share in

        Returns:
            KnowledgeItem
        """
        self.knowledge_counter += 1
        knowledge_id = f"knowledge_{self.knowledge_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        knowledge = KnowledgeItem(
            knowledge_id=knowledge_id,
            knowledge_type=knowledge_type,
            priority=priority,
            title=title,
            content=content,
            context=context or {},
            source_agent=source_agent,
            target_agents=target_agents or {"all"},
            tags=tags or set()
        )

        self.knowledge_items[knowledge_id] = knowledge

        # Add to channel
        if channel_id in self.channels:
            self.channels[channel_id].knowledge_items.append(knowledge_id)

        logger.info(f"📢 {source_agent} shared: {title} (type: {knowledge_type.value}, priority: {priority.name})")

        # Notify subscribers
        await self._notify_subscribers(knowledge, channel_id)

        return knowledge

    async def _notify_subscribers(self, knowledge: KnowledgeItem, channel_id: str):
        """Notify subscribers about new knowledge."""
        channel = self.channels.get(channel_id)
        if not channel:
            return

        # Notify all subscribers to this channel
        for agent_type in channel.subscribers:
            if agent_type in self.knowledge_listeners:
                # Call all listeners for this agent
                for listener in self.knowledge_listeners[agent_type]:
                    try:
                        await listener(knowledge)
                    except Exception as e:
                        logger.error(f"Error notifying {agent_type}: {e}")

        # Also notify specifically targeted agents
        if "all" not in knowledge.target_agents:
            for target_agent in knowledge.target_agents:
                if target_agent in self.knowledge_listeners:
                    for listener in self.knowledge_listeners[target_agent]:
                        try:
                            await listener(knowledge)
                        except Exception as e:
                            logger.error(f"Error notifying {target_agent}: {e}")

    def subscribe_to_channel(self, agent_type: str, channel_id: str) -> bool:
        """
        Subscribe an agent to a knowledge channel.

        Args:
            agent_type: Type of agent
            channel_id: Channel ID

        Returns:
            True if subscribed successfully
        """
        if channel_id not in self.channels:
            logger.error(f"Channel {channel_id} does not exist")
            return False

        self.channels[channel_id].subscribers.add(agent_type)
        self.agent_subscriptions[agent_type].add(channel_id)

        logger.info(f"✅ {agent_type} subscribed to channel: {channel_id}")
        return True

    def register_listener(self, agent_type: str, callback: Callable):
        """
        Register a callback to listen for new knowledge.

        Args:
            agent_type: Type of agent
            callback: Async function to call when new knowledge arrives
        """
        self.knowledge_listeners[agent_type].append(callback)
        logger.info(f"✅ Registered listener for {agent_type}")

    def get_channel_knowledge(
        self,
        channel_id: str,
        limit: int = 20,
        knowledge_type: Optional[KnowledgeType] = None
    ) -> List[KnowledgeItem]:
        """
        Get knowledge from a specific channel.

        Args:
            channel_id: Channel ID
            limit: Maximum number of items to return
            knowledge_type: Filter by knowledge type

        Returns:
            List of knowledge items
        """
        channel = self.channels.get(channel_id)
        if not channel:
            return []

        knowledge_list = [
            self.knowledge_items[kid]
            for kid in channel.knowledge_items[-limit:]
            if kid in self.knowledge_items
        ]

        if knowledge_type:
            knowledge_list = [k for k in knowledge_list if k.knowledge_type == knowledge_type]

        # Sort by priority and recency
        knowledge_list.sort(
            key=lambda k: (k.priority.value, k.created_at),
            reverse=True
        )

        return knowledge_list

    def query_knowledge(
        self,
        query: str,
        agent_type: Optional[str] = None,
        knowledge_type: Optional[KnowledgeType] = None,
        min_priority: KnowledgePriority = KnowledgePriority.LOW,
        limit: int = 10
    ) -> List[KnowledgeItem]:
        """
        Query knowledge base.

        Args:
            query: Search query
            agent_type: Filter by source agent
            knowledge_type: Filter by knowledge type
            min_priority: Minimum priority
            limit: Maximum results

        Returns:
            List of matching knowledge items
        """
        query_lower = query.lower()
        results = []

        for knowledge in self.knowledge_items.values():
            # Filter by priority
            if knowledge.priority.value < min_priority.value:
                continue

            # Filter by agent type
            if agent_type and knowledge.source_agent != agent_type:
                continue

            # Filter by knowledge type
            if knowledge_type and knowledge.knowledge_type != knowledge_type:
                continue

            # Calculate relevance
            relevance = 0

            if query_lower in knowledge.title.lower():
                relevance += 10

            if query_lower in knowledge.content.lower():
                relevance += 5

            for tag in knowledge.tags:
                if query_lower in tag.lower():
                    relevance += 3

            # Boost by priority
            relevance += knowledge.priority.value

            # Boost by usefulness
            if knowledge.useful_votes > 0:
                usefulness_ratio = knowledge.useful_votes / max(knowledge.useful_votes + knowledge.not_useful_votes, 1)
                relevance += usefulness_ratio * 2

            if relevance > 0:
                results.append((relevance, knowledge))

        # Sort by relevance
        results.sort(key=lambda x: x[0], reverse=True)

        return [knowledge for _, knowledge in results[:limit]]

    def mark_as_viewed(self, knowledge_id: str, agent_type: str):
        """Mark knowledge as viewed by an agent."""
        if knowledge_id in self.knowledge_items:
            self.knowledge_items[knowledge_id].views += 1

    def vote_useful(self, knowledge_id: str, agent_type: str):
        """Vote knowledge as useful."""
        if knowledge_id in self.knowledge_items:
            self.knowledge_items[knowledge_id].useful_votes += 1
            logger.info(f"👍 {agent_type} found {knowledge_id} useful")

    def vote_not_useful(self, knowledge_id: str, agent_type: str):
        """Vote knowledge as not useful."""
        if knowledge_id in self.knowledge_items:
            self.knowledge_items[knowledge_id].not_useful_votes += 1

    def mark_as_applied(self, knowledge_id: str, agent_type: str):
        """Mark knowledge as applied in practice."""
        if knowledge_id in self.knowledge_items:
            self.knowledge_items[knowledge_id].applied_count += 1
            logger.info(f"✅ {agent_type} applied knowledge: {knowledge_id}")

    def get_popular_knowledge(self, limit: int = 10) -> List[KnowledgeItem]:
        """Get most popular knowledge items."""
        knowledge_list = list(self.knowledge_items.values())

        # Sort by usefulness and application count
        knowledge_list.sort(
            key=lambda k: (k.useful_votes, k.applied_count, k.views),
            reverse=True
        )

        return knowledge_list[:limit]

    def get_recent_knowledge(
        self,
        agent_type: Optional[str] = None,
        limit: int = 20
    ) -> List[KnowledgeItem]:
        """Get recent knowledge items."""
        knowledge_list = list(self.knowledge_items.values())

        # Filter by agent if specified
        if agent_type:
            # Get knowledge from subscribed channels
            subscribed_channels = self.agent_subscriptions.get(agent_type, set())
            if subscribed_channels:
                knowledge_list = [
                    k for k in knowledge_list
                    if any(
                        k.knowledge_id in self.channels[ch].knowledge_items
                        for ch in subscribed_channels
                        if ch in self.channels
                    )
                ]

        # Sort by recency
        knowledge_list.sort(key=lambda k: k.created_at, reverse=True)

        return knowledge_list[:limit]

    def get_agent_contributions(self, agent_type: str) -> Dict[str, Any]:
        """Get statistics on agent's knowledge contributions."""
        contributions = [
            k for k in self.knowledge_items.values()
            if k.source_agent == agent_type
        ]

        total_useful_votes = sum(k.useful_votes for k in contributions)
        total_applied = sum(k.applied_count for k in contributions)

        return {
            "agent_type": agent_type,
            "total_contributions": len(contributions),
            "by_type": {
                ktype.value: len([k for k in contributions if k.knowledge_type == ktype])
                for ktype in KnowledgeType
            },
            "total_useful_votes": total_useful_votes,
            "total_applied": total_applied,
            "avg_usefulness": total_useful_votes / len(contributions) if contributions else 0,
            "impact_score": total_useful_votes + (total_applied * 2)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge hub statistics."""
        return {
            "total_knowledge_items": len(self.knowledge_items),
            "by_type": {
                ktype.value: len([k for k in self.knowledge_items.values() if k.knowledge_type == ktype])
                for ktype in KnowledgeType
            },
            "by_priority": {
                priority.name: len([k for k in self.knowledge_items.values() if k.priority == priority])
                for priority in KnowledgePriority
            },
            "total_channels": len(self.channels),
            "total_subscriptions": sum(len(subs) for subs in self.agent_subscriptions.values()),
            "total_views": sum(k.views for k in self.knowledge_items.values()),
            "total_useful_votes": sum(k.useful_votes for k in self.knowledge_items.values()),
            "total_applications": sum(k.applied_count for k in self.knowledge_items.values()),
            "most_active_agents": self._get_most_active_agents()
        }

    def _get_most_active_agents(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most active knowledge contributors."""
        agent_contributions = defaultdict(int)

        for knowledge in self.knowledge_items.values():
            agent_contributions[knowledge.source_agent] += 1

        sorted_agents = sorted(
            agent_contributions.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {"agent": agent, "contributions": count}
            for agent, count in sorted_agents[:limit]
        ]

    async def broadcast_discovery(
        self,
        source_agent: str,
        title: str,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Broadcast an important discovery to all agents."""
        await self.share_knowledge(
            source_agent=source_agent,
            knowledge_type=KnowledgeType.DISCOVERY,
            title=title,
            content=content,
            context=context,
            priority=KnowledgePriority.HIGH,
            target_agents={"all"},
            channel_id="general"
        )

        logger.info(f"📣 BROADCAST from {source_agent}: {title}")

    async def broadcast_warning(
        self,
        source_agent: str,
        title: str,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Broadcast a warning to all agents."""
        await self.share_knowledge(
            source_agent=source_agent,
            knowledge_type=KnowledgeType.WARNING,
            title=title,
            content=content,
            context=context,
            priority=KnowledgePriority.CRITICAL,
            target_agents={"all"},
            channel_id="warnings"
        )

        logger.warning(f"⚠️  WARNING from {source_agent}: {title}")

    async def share_solution(
        self,
        source_agent: str,
        problem: str,
        solution: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Share a successful solution."""
        await self.share_knowledge(
            source_agent=source_agent,
            knowledge_type=KnowledgeType.SOLUTION,
            title=f"Solution: {problem}",
            content=solution,
            context=context,
            priority=KnowledgePriority.MEDIUM,
            channel_id="solutions"
        )


# Global singleton instance
knowledge_hub = KnowledgeHub()
