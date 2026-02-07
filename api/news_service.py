# news_service.py - News fetching and display service
import re
import requests
import feedparser
from datetime import datetime, timezone
from typing import List, Dict, Optional

# Import MCP web search service
try:
    from .mcp_web_search_service import mcp_news_search, mcp_web_search, format_mcp_search_results
    from .config import MCP_WEB_SEARCH_URL
    MCP_SEARCH_AVAILABLE = bool(MCP_WEB_SEARCH_URL)
except ImportError:
    MCP_SEARCH_AVAILABLE = False

def _format_time(time_str: str) -> str:
    """Format time string for display."""
    try:
        dt = datetime.strptime(time_str, "%a, %d %b %Y %H:%M:%S %z")
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return time_str

def fetch_rss_news(url: str, limit: int = 5, source_name: str = "News") -> str:
    """Fetch news from an RSS feed."""
    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            return f"✅ No {source_name} articles available at this time. The news service may be temporarily unavailable or network access is restricted."
        
        lines = []
        for i, entry in enumerate(feed.entries[:limit], 1):
            title = entry.get('title', 'No title')
            link = entry.get('link', '')
            pub_date = entry.get('published', '')
            
            # Format the time if available
            if pub_date:
                try:
                    time_formatted = _format_time(pub_date)
                except Exception:
                    time_formatted = pub_date
            else:
                time_formatted = "Unknown time"
            
            summary = entry.get('summary', '')
            # Clean HTML tags from summary if present
            if summary:
                summary = re.sub('<[^<]+?>', '', summary)
                # Truncate summary
                if len(summary) > 150:
                    summary = summary[:150] + "..."
            
            article_text = f"{i}. {title}\n"
            article_text += f"   Time: {time_formatted}\n"
            if summary:
                article_text += f"   {summary}\n"
            article_text += f"   Link: {link}"
            lines.append(article_text)
        
        return "\n\n".join(lines)
    except Exception as e:
        return f"❌ Failed to fetch {source_name}: {e}\n\nNote: News feeds may be blocked in restricted network environments."

def fetch_tech_news(limit: int = 5) -> str:
    """Fetch technology news."""
    url = "https://news.ycombinator.com/rss"
    result = fetch_rss_news(url, limit, "Technology News")
    return f"🔬 Technology News (Hacker News)\n{'=' * 40}\n\n{result}"

def fetch_taiwan_news(limit: int = 5) -> str:
    """Fetch Taiwan news."""
    # Using a public Taiwan news RSS feed
    url = "https://www.cna.com.tw/rss/news.xml"
    result = fetch_rss_news(url, limit, "Taiwan News")
    return f"🇹🇼 Taiwan News (CNA)\n{'=' * 40}\n\n{result}"

def fetch_global_news(limit: int = 5) -> str:
    """Fetch global news."""
    # Using BBC News RSS feed as an example
    url = "http://feeds.bbci.co.uk/news/rss.xml"
    result = fetch_rss_news(url, limit, "Global News")
    return f"🌍 Global News (BBC)\n{'=' * 40}\n\n{result}"

def fetch_general_news(limit: int = 5) -> str:
    """Fetch general news from multiple sources."""
    # Try MCP web search first if available
    if MCP_SEARCH_AVAILABLE:
        try:
            result = mcp_news_search("latest news", limit=limit, engines=["bing", "duckduckgo"])
            if result and not result.startswith("❌"):
                return result
        except Exception as e:
            print(f"MCP news search failed, falling back to RSS: {e}")
    
    # Fallback to RSS feeds
    sources = [
        ("Tech", fetch_tech_news),
        ("Global", fetch_global_news),
        ("Taiwan", fetch_taiwan_news)
    ]
    
    for source_name, fetch_func in sources:
        try:
            result = fetch_func(limit)
            if not result.startswith("❌"):
                return result
        except Exception:
            continue
    
    return "❌ Unable to fetch news from any source at this time.\n\nNote: News feeds may require network access that is not available in this environment."


def fetch_tech_news_mcp(limit: int = 5) -> str:
    """Fetch technology news using MCP web search."""
    if not MCP_SEARCH_AVAILABLE:
        return fetch_tech_news(limit)
    
    try:
        result = mcp_news_search("technology tech", limit=limit, engines=["bing", "duckduckgo"])
        if result and not result.startswith("❌"):
            return result
    except Exception as e:
        print(f"MCP tech news search failed: {e}")
    
    # Fallback to RSS
    return fetch_tech_news(limit)


def fetch_taiwan_news_mcp(limit: int = 5) -> str:
    """Fetch Taiwan news using MCP web search."""
    if not MCP_SEARCH_AVAILABLE:
        return fetch_taiwan_news(limit)
    
    try:
        result = mcp_news_search("Taiwan 台灣", limit=limit, engines=["bing", "duckduckgo"])
        if result and not result.startswith("❌"):
            return result
    except Exception as e:
        print(f"MCP Taiwan news search failed: {e}")
    
    # Fallback to RSS
    return fetch_taiwan_news(limit)


def fetch_global_news_mcp(limit: int = 5) -> str:
    """Fetch global news using MCP web search."""
    if not MCP_SEARCH_AVAILABLE:
        return fetch_global_news(limit)
    
    try:
        result = mcp_news_search("world international", limit=limit, engines=["bing", "duckduckgo"])
        if result and not result.startswith("❌"):
            return result
    except Exception as e:
        print(f"MCP global news search failed: {e}")
    
    # Fallback to RSS
    return fetch_global_news(limit)
