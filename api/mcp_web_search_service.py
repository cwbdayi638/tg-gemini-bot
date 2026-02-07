"""
MCP Web Search Service
Integrates with open-webSearch MCP server (https://github.com/Aas-ee/open-webSearch)
for advanced web search capabilities.
"""

import requests
import json
from typing import List, Dict, Optional
from .config import MCP_WEB_SEARCH_URL


class MCPSearchResult:
    """Represents a search result from MCP web search."""
    
    def __init__(self, title: str, url: str, description: str = "", source: str = "", engine: str = ""):
        self.title = title
        self.url = url
        self.description = description
        self.source = source
        self.engine = engine
    
    def to_dict(self):
        return {
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "source": self.source,
            "engine": self.engine
        }


def mcp_web_search(query: str, limit: int = 10, engines: Optional[List[str]] = None) -> List[MCPSearchResult]:
    """
    Perform web search using open-webSearch MCP server.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 10)
        engines: List of search engines to use (default: ["bing"])
                 Supported: bing, duckduckgo, exa, brave, baidu, csdn, juejin
        
    Returns:
        List of MCPSearchResult objects
    """
    if not query or not query.strip():
        return []
    
    if not MCP_WEB_SEARCH_URL:
        print("MCP_WEB_SEARCH_URL not configured")
        return []
    
    if engines is None:
        engines = ["bing"]
    
    try:
        # Prepare MCP request payload
        payload = {
            "method": "tools/call",
            "params": {
                "name": "search",
                "arguments": {
                    "query": query.strip(),
                    "limit": limit,
                    "engines": engines
                }
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Make request to MCP server
        response = requests.post(
            f"{MCP_WEB_SEARCH_URL.rstrip('/')}/mcp",
            json=payload,
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        # Extract results from MCP response
        results = []
        if "content" in data:
            # MCP returns results in content field
            content = data["content"]
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        # Parse the JSON string in text field
                        try:
                            search_results = json.loads(item["text"])
                            if isinstance(search_results, list):
                                for result in search_results:
                                    results.append(MCPSearchResult(
                                        title=result.get("title", ""),
                                        url=result.get("url", ""),
                                        description=result.get("description", ""),
                                        source=result.get("source", ""),
                                        engine=result.get("engine", "")
                                    ))
                        except json.JSONDecodeError:
                            pass
        
        return results[:limit]
        
    except requests.exceptions.RequestException as e:
        print(f"MCP web search error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in MCP web search: {e}")
        return []


def mcp_news_search(topic: str, limit: int = 5, engines: Optional[List[str]] = None) -> str:
    """
    Search for news articles using MCP web search.
    
    Args:
        topic: News topic to search for
        limit: Maximum number of results to return
        engines: Search engines to use
        
    Returns:
        Formatted news results string
    """
    if not topic:
        topic = "latest news"
    
    # Add news-specific search terms
    search_query = f"{topic} news"
    
    try:
        results = mcp_web_search(search_query, limit=limit, engines=engines)
        
        if not results:
            return f"🔍 No news results found for: {topic}"
        
        lines = [
            f"📰 News Search Results: {topic}",
            f"Found {len(results)} articles:\n"
        ]
        lines.append("─" * 40)
        
        for i, result in enumerate(results, 1):
            lines.append(f"\n{i}. {result.title}")
            lines.append(f"🔗 {result.url}")
            if result.description:
                # Limit description to 150 characters
                desc = result.description[:150] + "..." if len(result.description) > 150 else result.description
                lines.append(f"📝 {desc}")
            if result.engine:
                lines.append(f"🔍 Source: {result.engine}")
            lines.append("")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"❌ Failed to search news: {e}"


def format_mcp_search_results(results: List[MCPSearchResult], query: str) -> str:
    """
    Format MCP search results for display in Telegram.
    
    Args:
        results: List of MCPSearchResult objects
        query: Original search query
        
    Returns:
        Formatted string for display
    """
    if not results:
        return f"🔍 No results found for: {query}"
    
    lines = [
        f"🔍 Web Search Results for: {query}",
        f"Found {len(results)} results:\n"
    ]
    lines.append("─" * 40)
    
    for i, result in enumerate(results, 1):
        lines.append(f"\n{i}. {result.title}")
        lines.append(f"🔗 {result.url}")
        if result.description:
            # Limit description to 150 characters
            desc = result.description[:150] + "..." if len(result.description) > 150 else result.description
            lines.append(f"📝 {desc}")
        if result.source:
            lines.append(f"📍 {result.source}")
        if result.engine:
            lines.append(f"🔍 Engine: {result.engine}")
        lines.append("")
    
    return "\n".join(lines)
