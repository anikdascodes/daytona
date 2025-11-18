# Knowledge Agent - Web Research & Information Retrieval

## Overview

The Knowledge Agent is a specialized AI agent designed for web research, information retrieval, and knowledge synthesis. Part of the Phase 3 multi-agent system.

## Capabilities

### 1. Web Search
- Search the web using privacy-focused search engines (DuckDuckGo by default)
- Retrieve and parse search results
- Track search history

### 2. Research Questions
- Answer complex research questions
- Consult multiple sources
- Synthesize findings into coherent answers
- Provide confidence levels

### 3. Fact Verification
- Verify factual claims
- Find supporting/contradicting evidence
- Provide verdict with confidence level

### 4. Knowledge Synthesis
- Extract key insights from research
- Summarize complex information
- Identify patterns and trends

## Architecture

```
Knowledge Agent
├── Web Search
│   ├── Query generation
│   ├── Search execution (DuckDuckGo)
│   ├── Result extraction
│   └── History tracking
│
├── Research Pipeline
│   ├── Question analysis
│   ├── Multi-source search
│   ├── Information synthesis
│   └── Insight extraction
│
└── Fact Verification
    ├── Evidence gathering
    ├── Claim analysis
    ├── Verdict determination
    └── Confidence scoring
```

## Usage

### From Enhanced Agent

The Knowledge Agent is integrated with the Enhanced Agent via the `SEARCH_WEB` action:

```
ACTION: SEARCH_WEB
QUERY: Python async best practices 2024
MAX_RESULTS: 5
---END---
```

### Direct Usage

```python
from services.knowledge_agent_service import knowledge_agent

# Web search
result = await knowledge_agent.search(
    query="machine learning fundamentals",
    max_results=5,
    search_engine="duckduckgo"
)

# Research question
result = await knowledge_agent.research_question(
    question="What are the best practices for async Python in 2024?",
    depth="medium",  # quick/medium/deep
    max_sources=3
)

# Verify fact
result = await knowledge_agent.verify_fact(
    claim="Python 3.12 introduces async comprehensions",
    context="Python version 3.12 features"
)

# Get statistics
stats = knowledge_agent.get_statistics()
```

## API Reference

### search(query, max_results=5, search_engine="duckduckgo")

Execute a web search.

**Parameters:**
- `query` (str): Search query
- `max_results` (int): Maximum results to return (default: 5)
- `search_engine` (str): Search engine to use (default: "duckduckgo")

**Returns:**
```python
{
    "success": True,
    "query": "python async",
    "engine": "duckduckgo",
    "results_count": 5,
    "timestamp": "2024-01-15T10:30:00",
    "raw_content": "..." # Search results content
}
```

### research_question(question, depth="medium", max_sources=3)

Research a question using AI synthesis.

**Parameters:**
- `question` (str): Research question
- `depth` (str): Research depth - "quick", "medium", or "deep"
  - **quick**: Brief answer (2-3 sentences)
  - **medium**: Comprehensive answer (1-2 paragraphs)
  - **deep**: In-depth analysis (3-4 paragraphs)
- `max_sources` (int): Maximum sources to consult (default: 3)

**Returns:**
```python
{
    "success": True,
    "question": "What are...",
    "answer": "Comprehensive answer based on sources...",
    "key_insights": ["insight 1", "insight 2", ...],
    "sources_consulted": 3,
    "confidence": "high",  # high/medium/low
    "search_queries": ["query 1", "query 2", ...],
    "timestamp": "2024-01-15T10:30:00",
    "depth": "medium"
}
```

### verify_fact(claim, context=None)

Verify a factual claim.

**Parameters:**
- `claim` (str): Claim to verify
- `context` (str, optional): Additional context

**Returns:**
```python
{
    "success": True,
    "claim": "Python 3.12 introduces...",
    "verdict": "true",  # true/false/uncertain/needs_more_info
    "confidence": "high",  # high/medium/low
    "evidence": "Brief explanation...",
    "sources_support": True,
    "timestamp": "2024-01-15T10:30:00"
}
```

## Integration with Tool Masking

The Knowledge Agent respects the tool masking system:

| State | SEARCH_WEB Available |
|-------|---------------------|
| PLANNING | ✅ |
| EXECUTING | ✅ |
| VERIFYING | ⛔ |
| BROWSING | ⛔ |
| LEARNING | ✅ |

This ensures:
- Planning phase can research requirements
- Execution phase can gather needed information
- Learning phase can research improvements
- Verification phase focuses on testing (no external searches)

## Example Workflows

### 1. Research Before Implementation

```
Agent in PLANNING state:

ACTION: SEARCH_WEB
QUERY: React hooks best practices 2024
MAX_RESULTS: 3
---END---

Result:
✅ Found 3 sources
📄 Key insights: useState for simple state, useEffect for side effects...

Agent uses research to inform implementation plan.
```

### 2. Fact Checking During Development

```
Agent in EXECUTING state:

Task: "Verify the claim that async/await improves performance"

ACTION: SEARCH_WEB
QUERY: async await performance benefits Python
MAX_RESULTS: 5
---END---

Result:
✅ Verdict: True
🔍 Confidence: High
📝 Evidence: Async/await allows concurrent execution...
```

### 3. Learning from Errors

```
Agent in LEARNING state:

Error occurred: "Import error with asyncio"

ACTION: SEARCH_WEB
QUERY: Python asyncio import error common causes
MAX_RESULTS: 3
---END---

Result:
✅ Found solutions
💡 Key insights:
   - Check Python version >= 3.7
   - Verify event loop initialization
   - Common mistake: mixing sync/async code
```

## Search Engine Options

### DuckDuckGo (Default)
- **Privacy**: No tracking, anonymous searches
- **API**: No API key required
- **Rate Limits**: Reasonable for moderate use
- **Coverage**: Good general search results

### Future Support
- **Google**: Requires API key, excellent results
- **Bing**: Microsoft search API
- **Brave Search**: Privacy-focused alternative
- **Local/Enterprise**: Custom search solutions

## Research Quality

The Knowledge Agent provides confidence levels based on:

1. **Source Quantity**: More sources = higher confidence
2. **Source Agreement**: Consensus across sources
3. **Information Completeness**: All aspects covered
4. **Source Recency**: Recent information preferred

**Confidence Levels:**
- **High**: Multiple sources agree, comprehensive information
- **Medium**: Some sources agree, good information
- **Low**: Limited sources, partial information, conflicts

## Performance Considerations

### Search Optimization

```python
# Quick search (1-2 sources)
result = await knowledge_agent.research_question(
    question="Quick Python syntax question",
    depth="quick",
    max_sources=1
)

# Deep research (5+ sources)
result = await knowledge_agent.research_question(
    question="Complex architectural decision",
    depth="deep",
    max_sources=5
)
```

### Caching

Search results are tracked in search history for potential caching:

```python
stats = knowledge_agent.get_statistics()
# {
#     "searches_performed": 42,
#     "recent_queries": ["query1", "query2", ...]
# }
```

### Rate Limiting

To avoid overwhelming search engines:
- Implement delays between searches
- Batch related queries
- Cache frequently accessed information
- Use appropriate `max_results` limits

## Multi-Agent Coordination

The Knowledge Agent can be used by other agents:

```python
# Main Agent delegates to Knowledge Agent
ACTION: DELEGATE
AGENT_TYPE: knowledge
TASK: Research best practices for error handling in async Python
---END---

# Knowledge Agent processes research
# Returns synthesized findings to Main Agent
```

## Error Handling

The Knowledge Agent handles errors gracefully:

```python
{
    "success": False,
    "error": "Search timeout - network unavailable",
    "query": "original query",
    # Fallback mechanisms:
    # - Retry with exponential backoff
    # - Use cached results if available
    # - Return partial results
}
```

## Privacy & Ethics

### Privacy Considerations
- Uses DuckDuckGo for privacy by default
- No personal information in search queries
- Search history stored locally only
- No telemetry or tracking

### Ethical Use
- ✅ Research for legitimate development tasks
- ✅ Fact checking and verification
- ✅ Learning and education
- ⚠️ Be mindful of copyright in scraped content
- ⛔ Don't use for surveillance or tracking
- ⛔ Don't scrape at high volume

## Statistics & Monitoring

```python
stats = knowledge_agent.get_statistics()

{
    "searches_performed": 156,
    "knowledge_entries": 42,
    "recent_queries": [
        "python async patterns",
        "react hooks useState",
        "docker compose networking",
        ...
    ],
    "agent_type": "knowledge",
    "capabilities": [
        "search",
        "research",
        "verify_facts",
        "synthesize"
    ]
}
```

## Future Enhancements

### Phase 3+
- [ ] Advanced web scraping with rate limiting
- [ ] Multi-engine search aggregation
- [ ] Knowledge base persistence (vector DB)
- [ ] Citation tracking and formatting
- [ ] Source credibility scoring
- [ ] Real-time fact checking
- [ ] Semantic search capabilities
- [ ] PDF/document parsing
- [ ] Knowledge graph construction

### Phase 4
- [ ] Integration with academic databases
- [ ] Patent search capabilities
- [ ] Code repository search (GitHub, GitLab)
- [ ] Stack Overflow integration
- [ ] Documentation search (MDN, Python docs)
- [ ] API documentation lookup

## Testing

```bash
cd /home/user/daytona/backend

# Test search functionality
python -c "
import asyncio
from services.knowledge_agent_service import knowledge_agent

async def test():
    result = await knowledge_agent.search('Python asyncio')
    print(f'Search: {result[\"success\"]}')

    stats = knowledge_agent.get_statistics()
    print(f'Stats: {stats}')

asyncio.run(test())
"
```

## Troubleshooting

### Common Issues

**Search returns no results:**
- Check internet connectivity
- Verify search engine URL is accessible
- Try different search query phrasing

**Slow search responses:**
- Reduce `max_results`
- Use "quick" depth for research
- Check network latency

**LLM synthesis errors:**
- Verify LLM API key is configured
- Check LLM service status
- Reduce complexity of research question

## Status

✅ **IMPLEMENTED** - Phase 3, Task 3.2
✅ **INTEGRATED** - Enhanced Agent + Tool Masking
✅ **TESTED** - Basic search functionality verified
🚧 **IN PROGRESS** - Advanced features (caching, multi-engine)

---

*Implementation Date: Phase 3 (Advanced Learning & Multi-Agent Orchestration)*
*Next: Multi-Agent Orchestration System (Task 3.3)*
