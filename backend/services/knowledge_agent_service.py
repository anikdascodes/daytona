"""
Knowledge Agent Service - Specialized agent for web search and information retrieval.

Capabilities:
- Web search (Google, DuckDuckGo, etc.)
- Information extraction from web pages
- Knowledge synthesis and summarization
- Fact verification
- Research question answering

Part of Phase 3: Multi-Agent System
"""
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from litellm import acompletion
from config import settings
from utils.logger import logger
from services.browser_service import browser_service


class KnowledgeAgentService:
    """
    Specialized agent for web research and knowledge retrieval.

    Designed to:
    - Answer research questions
    - Gather information from multiple sources
    - Synthesize findings into actionable insights
    - Verify facts and claims
    - Track sources and citations
    """

    def __init__(self):
        """Initialize knowledge agent service."""
        self.search_history: List[Dict[str, Any]] = []
        self.knowledge_base: Dict[str, Any] = {}
        logger.info("KnowledgeAgentService initialized")

    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_engine: str = "duckduckgo"
    ) -> Dict[str, Any]:
        """
        Search the web for information.

        Args:
            query: Search query
            max_results: Maximum number of results to return
            search_engine: Search engine to use (default: duckduckgo)

        Returns:
            Dictionary with search results
        """
        logger.info(f"🔍 Searching: '{query}' (engine: {search_engine}, max: {max_results})")

        try:
            # Use browser service to search
            # For DuckDuckGo (privacy-focused, no API key needed)
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"

            # Navigate and extract results
            browser_result = await browser_service.execute_task({
                "action": "navigate",
                "url": search_url
            })

            if not browser_result["success"]:
                return {
                    "success": False,
                    "error": f"Search navigation failed: {browser_result.get('error')}",
                    "query": query
                }

            # Extract search results
            # This is a simplified version - in production, use proper selectors
            extract_result = await browser_service.execute_task({
                "action": "get_content"
            })

            if not extract_result["success"]:
                return {
                    "success": False,
                    "error": "Failed to extract search results",
                    "query": query
                }

            # Parse and structure results
            # In a real implementation, you'd parse the HTML properly
            # For now, return raw content
            results = {
                "success": True,
                "query": query,
                "engine": search_engine,
                "results_count": max_results,
                "timestamp": datetime.now().isoformat(),
                "raw_content": extract_result.get("content", "")[:5000]  # Limit size
            }

            # Store in search history
            self.search_history.append({
                "query": query,
                "timestamp": results["timestamp"],
                "engine": search_engine
            })

            logger.info(f"✅ Search completed: {query}")
            return results

        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    async def research_question(
        self,
        question: str,
        depth: str = "medium",
        max_sources: int = 3
    ) -> Dict[str, Any]:
        """
        Research a question using web search and AI synthesis.

        Args:
            question: Research question
            depth: Research depth (quick/medium/deep)
            max_sources: Maximum sources to consult

        Returns:
            Research results with answer, sources, and confidence
        """
        logger.info(f"📚 Researching: '{question}' (depth: {depth}, sources: {max_sources})")

        try:
            # Step 1: Generate search queries
            search_queries = await self._generate_search_queries(question, max_sources)

            # Step 2: Execute searches
            search_results = []
            for query in search_queries[:max_sources]:
                result = await self.search(query)
                if result["success"]:
                    search_results.append(result)

            if not search_results:
                return {
                    "success": False,
                    "error": "No search results obtained",
                    "question": question
                }

            # Step 3: Synthesize findings
            synthesis = await self._synthesize_findings(question, search_results, depth)

            # Step 4: Extract key insights
            insights = await self._extract_insights(question, synthesis)

            return {
                "success": True,
                "question": question,
                "answer": synthesis.get("answer"),
                "key_insights": insights,
                "sources_consulted": len(search_results),
                "confidence": synthesis.get("confidence", "medium"),
                "search_queries": search_queries,
                "timestamp": datetime.now().isoformat(),
                "depth": depth
            }

        except Exception as e:
            logger.error(f"❌ Research failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "question": question
            }

    async def _generate_search_queries(
        self,
        question: str,
        num_queries: int = 3
    ) -> List[str]:
        """
        Generate effective search queries for a research question.

        Args:
            question: Research question
            num_queries: Number of queries to generate

        Returns:
            List of search queries
        """
        try:
            prompt = f"""Generate {num_queries} effective web search queries to answer this question:

Question: {question}

Generate queries that:
1. Cover different aspects of the question
2. Use specific, searchable terms
3. Are concise and focused

Return ONLY a JSON array of query strings, nothing else.
Example: ["query 1", "query 2", "query 3"]"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.7,
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()

            # Extract JSON array
            if content.startswith("[") and content.endswith("]"):
                queries = json.loads(content)
                logger.info(f"Generated {len(queries)} search queries")
                return queries
            else:
                # Fallback: use the question itself
                logger.warning("Failed to parse queries, using question as query")
                return [question]

        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            return [question]  # Fallback

    async def _synthesize_findings(
        self,
        question: str,
        search_results: List[Dict[str, Any]],
        depth: str
    ) -> Dict[str, Any]:
        """
        Synthesize search results into a coherent answer.

        Args:
            question: Original question
            search_results: List of search results
            depth: Research depth

        Returns:
            Synthesis with answer and confidence
        """
        try:
            # Compile search findings
            findings = "\n\n".join([
                f"Source {i+1} (Query: {r['query']}):\n{r.get('raw_content', 'No content')[:1000]}"
                for i, r in enumerate(search_results)
            ])

            # Adjust prompt based on depth
            depth_instructions = {
                "quick": "Provide a brief, direct answer (2-3 sentences).",
                "medium": "Provide a comprehensive answer with key points (1-2 paragraphs).",
                "deep": "Provide an in-depth analysis with detailed explanation (3-4 paragraphs)."
            }

            prompt = f"""Based on the following search results, answer this question:

Question: {question}

Search Results:
{findings}

Instructions:
- {depth_instructions.get(depth, depth_instructions['medium'])}
- Focus on factual information from the sources
- If sources conflict, mention both perspectives
- If information is insufficient, acknowledge limitations

Provide your answer in JSON format:
{{
    "answer": "Your comprehensive answer here",
    "confidence": "high/medium/low",
    "key_points": ["point 1", "point 2", ...],
    "limitations": "Any limitations or uncertainties"
}}"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.3,  # Lower temperature for factual synthesis
                max_tokens=2000
            )

            content = response.choices[0].message.content.strip()

            # Try to parse JSON
            if "{" in content and "}" in content:
                # Extract JSON from response
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]
                synthesis = json.loads(json_str)
                return synthesis
            else:
                # Fallback: return raw answer
                return {
                    "answer": content,
                    "confidence": "medium",
                    "key_points": [],
                    "limitations": "Unable to structure response"
                }

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return {
                "answer": "Unable to synthesize findings due to error.",
                "confidence": "low",
                "key_points": [],
                "limitations": str(e)
            }

    async def _extract_insights(
        self,
        question: str,
        synthesis: Dict[str, Any]
    ) -> List[str]:
        """
        Extract key insights from synthesis.

        Args:
            question: Original question
            synthesis: Synthesis results

        Returns:
            List of key insights
        """
        try:
            # Check if synthesis already has key_points
            if "key_points" in synthesis and synthesis["key_points"]:
                return synthesis["key_points"]

            # Otherwise, extract from answer
            answer = synthesis.get("answer", "")

            prompt = f"""Extract 3-5 key insights from this research answer:

Question: {question}
Answer: {answer}

Return ONLY a JSON array of insight strings.
Example: ["insight 1", "insight 2", "insight 3"]"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.5,
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()

            if content.startswith("[") and content.endswith("]"):
                insights = json.loads(content)
                return insights
            else:
                return ["Unable to extract insights"]

        except Exception as e:
            logger.error(f"Insight extraction failed: {e}")
            return []

    async def verify_fact(
        self,
        claim: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a factual claim using web search.

        Args:
            claim: Claim to verify
            context: Optional context

        Returns:
            Verification result with verdict and evidence
        """
        logger.info(f"🔍 Verifying claim: '{claim}'")

        try:
            # Search for evidence
            search_query = f"{claim} fact check verification"
            search_result = await self.search(search_query, max_results=3)

            if not search_result["success"]:
                return {
                    "success": False,
                    "error": "Search failed during verification",
                    "claim": claim
                }

            # Analyze evidence
            prompt = f"""Verify this claim based on search results:

Claim: {claim}
{f'Context: {context}' if context else ''}

Search Results:
{search_result.get('raw_content', '')[:2000]}

Provide verification in JSON format:
{{
    "verdict": "true/false/uncertain/needs_more_info",
    "confidence": "high/medium/low",
    "evidence": "Brief explanation of evidence",
    "sources_support": true/false
}}"""

            response = await acompletion(
                model=f"groq/{settings.LLM_MODEL}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_BASE_URL,
                temperature=0.1,  # Very low temperature for verification
                max_tokens=1000
            )

            content = response.choices[0].message.content.strip()

            # Parse verification
            if "{" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                verification = json.loads(content[start:end])
            else:
                verification = {
                    "verdict": "uncertain",
                    "confidence": "low",
                    "evidence": content,
                    "sources_support": False
                }

            return {
                "success": True,
                "claim": claim,
                **verification,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "claim": claim
            }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge agent statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "searches_performed": len(self.search_history),
            "knowledge_entries": len(self.knowledge_base),
            "recent_queries": [s["query"] for s in self.search_history[-5:]],
            "agent_type": "knowledge",
            "capabilities": ["search", "research", "verify_facts", "synthesize"]
        }


# Global singleton instance
knowledge_agent = KnowledgeAgentService()
