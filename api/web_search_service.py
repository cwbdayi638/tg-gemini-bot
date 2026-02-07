"""
Web Search Service
Provides web search functionality using multiple search engines.
Based on open-webSearch (https://github.com/Aas-ee/open-webSearch.git)
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urlencode, quote_plus


class SearchResult:
    """Represents a single search result."""
    
    def __init__(self, title: str, url: str, description: str = "", source: str = "", engine: str = ""):
        self.title = title
        self.url = url
        self.description = description
        self.source = source
        self.engine = engine
    
    def __str__(self):
        return f"{self.title}\n{self.url}\n{self.description}"
    
    def to_dict(self):
        return {
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "source": self.source,
            "engine": self.engine
        }


def search_bing(query: str, limit: int = 10) -> List[SearchResult]:
    """
    Search using Bing search engine.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List of SearchResult objects
    """
    results = []
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }
        
        params = {
            "q": query,
            "first": 1
        }
        
        response = requests.get("https://www.bing.com/search", params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find search results
        search_results = soup.select('#b_results li.b_algo')
        
        for item in search_results:
            if len(results) >= limit:
                break
                
            # Extract title and URL
            title_elem = item.select_one('h2 a')
            if not title_elem:
                continue
                
            url = title_elem.get('href', '')
            if not url or not url.startswith('http'):
                continue
                
            title = title_elem.get_text(strip=True)
            
            # Extract description
            desc_elem = item.select_one('p, .b_caption p')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract source
            source_elem = item.select_one('.b_attribution cite')
            source = source_elem.get_text(strip=True) if source_elem else ""
            
            results.append(SearchResult(
                title=title,
                url=url,
                description=description,
                source=source,
                engine="bing"
            ))
    
    except Exception as e:
        print(f"Bing search error: {e}")
        
    return results


def search_duckduckgo(query: str, limit: int = 10) -> List[SearchResult]:
    """
    Search using DuckDuckGo search engine.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List of SearchResult objects
    """
    results = []
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        
        # DuckDuckGo HTML search
        params = {
            "q": query,
            "t": "h_",
            "ia": "web"
        }
        
        response = requests.get("https://html.duckduckgo.com/html/", params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find search results
        search_results = soup.select('.result')
        
        for item in search_results:
            if len(results) >= limit:
                break
                
            # Extract title and URL
            title_elem = item.select_one('.result__title a')
            if not title_elem:
                continue
                
            # DuckDuckGo uses redirect URLs, extract actual URL
            url = title_elem.get('href', '')
            if url.startswith('//duckduckgo.com/l/?'):
                # Extract uddg parameter which contains the actual URL
                try:
                    from urllib.parse import parse_qs, urlparse
                    parsed = urlparse(url)
                    url_params = parse_qs(parsed.query)
                    if 'uddg' in url_params:
                        url = url_params['uddg'][0]
                except Exception:
                    pass
            
            if not url or not url.startswith('http'):
                continue
                
            title = title_elem.get_text(strip=True)
            
            # Extract description
            desc_elem = item.select_one('.result__snippet')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            results.append(SearchResult(
                title=title,
                url=url,
                description=description,
                source="",
                engine="duckduckgo"
            ))
    
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
        
    return results


def web_search(query: str, limit: int = 10, engines: Optional[List[str]] = None) -> List[SearchResult]:
    """
    Perform web search using specified search engines.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        engines: List of search engines to use (default: ["bing", "duckduckgo"])
        
    Returns:
        List of SearchResult objects
    """
    if not query or not query.strip():
        return []
    
    if engines is None:
        engines = ["bing"]  # Default to Bing as it's most reliable
    
    all_results = []
    
    # Map engine names to functions
    engine_map = {
        "bing": search_bing,
        "duckduckgo": search_duckduckgo
    }
    
    # Calculate results per engine
    results_per_engine = max(1, limit // len(engines))
    
    for engine in engines:
        if engine not in engine_map:
            print(f"Unsupported search engine: {engine}")
            continue
            
        try:
            engine_results = engine_map[engine](query, results_per_engine)
            all_results.extend(engine_results)
        except Exception as e:
            print(f"Error searching with {engine}: {e}")
    
    # Return up to limit results
    return all_results[:limit]


def format_search_results(results: List[SearchResult], query: str) -> str:
    """
    Format search results for display in Telegram.
    
    Args:
        results: List of SearchResult objects
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
        lines.append("")
    
    return "\n".join(lines)
