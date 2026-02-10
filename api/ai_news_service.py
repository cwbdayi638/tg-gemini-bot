"""
AI News Service for Telegram Bot

This module provides integration with the Hugging Face AI News Aggregator
to fetch latest AI/ML/Data Science news from 150+ sources.

API Documentation: https://huggingface.co/spaces/cwbdayi/ai-news-aggregator
"""

from gradio_client import Client
from typing import Dict, Any, Optional, List, Tuple
import os


# Configuration
AI_NEWS_AGGREGATOR_URL = "cwbdayi/ai-news-aggregator"


def _create_client() -> Client:
    """Create and return a Gradio client for the AI news aggregator."""
    try:
        return Client(AI_NEWS_AGGREGATOR_URL)
    except Exception as e:
        raise RuntimeError(f"Failed to connect to AI news aggregator: {e}")


def get_latest_news(max_articles: int = 15) -> Tuple[str, str]:
    """
    Get the latest AI news from multiple sources.
    
    Args:
        max_articles: Maximum number of articles to fetch (default: 15)
        
    Returns:
        Tuple of (formatted_articles_html, status_message)
        
    Raises:
        RuntimeError: If the API call fails
    """
    try:
        client = _create_client()
        result = client.predict(
            max_articles=max_articles,
            api_name="/get_latest_news"
        )
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to get latest news: {e}")


def search_news(query: str, max_results: int = 20) -> Tuple[str, str]:
    """
    Search for news articles by keyword.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 20)
        
    Returns:
        Tuple of (formatted_results_html, status_message)
        
    Raises:
        RuntimeError: If the API call fails
    """
    try:
        client = _create_client()
        result = client.predict(
            query=query,
            max_results=max_results,
            api_name="/search_news"
        )
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to search news: {e}")


def get_news_from_source(source_name: str, max_articles: int = 10) -> Tuple[str, str]:
    """
    Get news from a specific source.
    
    Args:
        source_name: Name of the news source (e.g., "OpenAI Blog")
        max_articles: Maximum number of articles to fetch (default: 10)
        
    Returns:
        Tuple of (formatted_articles_html, status_message)
        
    Raises:
        RuntimeError: If the API call fails
    """
    try:
        client = _create_client()
        result = client.predict(
            source_name=source_name,
            max_articles=max_articles,
            api_name="/get_news_from_source"
        )
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to get news from source: {e}")


def list_sources(category: str = "top") -> Tuple[str, str]:
    """
    List available news sources.
    
    Args:
        category: Category of sources to list ("top" or "all", default: "top")
        
    Returns:
        Tuple of (formatted_sources_html, status_message)
        
    Raises:
        RuntimeError: If the API call fails
    """
    try:
        client = _create_client()
        result = client.predict(
            category=category,
            api_name="/list_sources"
        )
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to list sources: {e}")


def format_html_to_telegram(html_content: str, max_length: int = 4000) -> str:
    """
    Convert HTML content from the API to Telegram-friendly markdown format.
    
    Args:
        html_content: HTML content from the API
        max_length: Maximum message length (default: 4000 to leave room for headers)
        
    Returns:
        Formatted text for Telegram
    """
    import re
    
    # Remove HTML tags and convert to plain text
    text = re.sub(r'<br\s*/?>', '\n', html_content)
    text = re.sub(r'<h[1-6]>(.*?)</h[1-6]>', r'\n📰 \1\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<b>(.*?)</b>', r'**\1**', text, flags=re.IGNORECASE)
    text = re.sub(r'<i>(.*?)</i>', r'_\1_', text, flags=re.IGNORECASE)
    text = re.sub(r'<a\s+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', r'\2: \1', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)  # Remove remaining HTML tags
    
    # Decode HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = text.strip()
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length-50] + "\n\n... (內容過長，已截斷)"
    
    return text


def get_latest_news_text(max_articles: int = 15) -> str:
    """
    Get latest AI news formatted for Telegram.
    
    Args:
        max_articles: Maximum number of articles (default: 15)
        
    Returns:
        Formatted text message for Telegram
    """
    try:
        articles_html, status = get_latest_news(max_articles)
        
        if not articles_html or "無" in status or "error" in status.lower():
            return f"❌ 無法獲取最新新聞\n狀態：{status}"
        
        # Format the output
        header = f"🤖 AI 最新新聞 (最多 {max_articles} 篇)\n"
        header += "=" * 40 + "\n\n"
        
        formatted_text = format_html_to_telegram(articles_html)
        
        footer = "\n\n" + "=" * 40
        footer += f"\n📊 狀態：{status}"
        footer += "\n🔗 來源：AI News Aggregator (HuggingFace)"
        
        return header + formatted_text + footer
        
    except Exception as e:
        return f"❌ 獲取最新新聞時發生錯誤：{e}"


def search_news_text(query: str, max_results: int = 20) -> str:
    """
    Search AI news and format for Telegram.
    
    Args:
        query: Search query
        max_results: Maximum number of results (default: 20)
        
    Returns:
        Formatted text message for Telegram
    """
    try:
        results_html, status = search_news(query, max_results)
        
        if not results_html or "無" in status or "error" in status.lower():
            return f"❌ 找不到相關新聞\n查詢：{query}\n狀態：{status}"
        
        # Format the output
        header = f"🔍 搜尋結果：「{query}」\n"
        header += "=" * 40 + "\n\n"
        
        formatted_text = format_html_to_telegram(results_html)
        
        footer = "\n\n" + "=" * 40
        footer += f"\n📊 狀態：{status}"
        
        return header + formatted_text + footer
        
    except Exception as e:
        return f"❌ 搜尋新聞時發生錯誤：{e}"


def get_news_from_source_text(source_name: str, max_articles: int = 10) -> str:
    """
    Get news from a specific source formatted for Telegram.
    
    Args:
        source_name: Name of the news source
        max_articles: Maximum number of articles (default: 10)
        
    Returns:
        Formatted text message for Telegram
    """
    try:
        articles_html, status = get_news_from_source(source_name, max_articles)
        
        if not articles_html or "無" in status or "error" in status.lower():
            return f"❌ 無法從來源獲取新聞\n來源：{source_name}\n狀態：{status}"
        
        # Format the output
        header = f"📡 新聞來源：{source_name}\n"
        header += "=" * 40 + "\n\n"
        
        formatted_text = format_html_to_telegram(articles_html)
        
        footer = "\n\n" + "=" * 40
        footer += f"\n📊 狀態：{status}"
        
        return header + formatted_text + footer
        
    except Exception as e:
        return f"❌ 從來源獲取新聞時發生錯誤：{e}"


def list_sources_text(category: str = "top") -> str:
    """
    List available news sources formatted for Telegram.
    
    Args:
        category: Category of sources ("top" or "all")
        
    Returns:
        Formatted text message for Telegram
    """
    try:
        sources_html, status = list_sources(category)
        
        if not sources_html or "無" in status or "error" in status.lower():
            return f"❌ 無法獲取來源列表\n狀態：{status}"
        
        # Format the output
        category_name = "熱門來源" if category == "top" else "全部來源"
        header = f"📋 {category_name}\n"
        header += "=" * 40 + "\n\n"
        
        formatted_text = format_html_to_telegram(sources_html, max_length=3500)
        
        footer = "\n\n" + "=" * 40
        footer += f"\n📊 狀態：{status}"
        footer += "\n\n💡 使用 /ai_news_source <來源名稱> 獲取特定來源的新聞"
        
        return header + formatted_text + footer
        
    except Exception as e:
        return f"❌ 獲取來源列表時發生錯誤：{e}"


# Popular source names for autocomplete/suggestions
POPULAR_SOURCES = [
    "OpenAI Blog",
    "DeepMind Blog",
    "Google AI Blog",
    "Hugging Face Blog",
    "TechCrunch",
    "MIT Technology Review",
    "The Verge",
    "arXiv cs.LG",
    "arXiv cs.CV",
    "arXiv cs.CL",
    "VentureBeat",
    "Ars Technica",
]


if __name__ == "__main__":
    # Test the service
    print("Testing AI News Service...")
    
    print("\n1. Get latest news:")
    print(get_latest_news_text(5))
    
    print("\n2. Search for 'GPT':")
    print(search_news_text("GPT", 5))
    
    print("\n3. List top sources:")
    print(list_sources_text("top"))
