"""
MCP Client Service for Telegram Bot

This module provides a Python client to interact with MCP tools.
When Node.js is not available, it falls back to simple Python implementations.
"""

import json
import os
import subprocess
import requests
from typing import Dict, Any, Optional
from datetime import datetime

# Configuration constants
MCP_CALL_TIMEOUT = 30  # Timeout for MCP tool calls in seconds


class MCPClient:
    """Client for interacting with MCP tools (Node.js or Python fallback)."""
    
    def __init__(self, server_path: Optional[str] = None):
        """
        Initialize MCP client.
        
        Args:
            server_path: Path to the MCP server.js file. 
                        If None, uses default path relative to this file.
        """
        if server_path is None:
            # Default to mcp-server/server.js in the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            server_path = os.path.join(project_root, "mcp-server", "server.js")
        
        self.server_path = server_path
        self.nodejs_available = self._check_nodejs()
    
    def _check_nodejs(self) -> bool:
        """Check if Node.js is available without raising errors."""
        try:
            # Check if server file exists
            if not os.path.exists(self.server_path):
                return False
            
            # Check if Node.js is available
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _call_nodejs_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call tool via Node.js MCP server."""
        # Prepare the MCP request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Convert to JSON
        request_json = json.dumps(request)
        
        try:
            # Call the MCP server via stdio
            result = subprocess.run(
                ["node", self.server_path],
                input=request_json,
                capture_output=True,
                text=True,
                timeout=MCP_CALL_TIMEOUT
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error"
                raise RuntimeError(f"MCP server error: {error_msg}")
            
            # Parse the response
            response = json.loads(result.stdout)
            
            # Extract content from MCP response
            if "content" in response and isinstance(response["content"], list):
                texts = []
                for item in response["content"]:
                    if isinstance(item, dict) and "text" in item:
                        texts.append(item["text"])
                return "\n".join(texts)
            elif "error" in response:
                raise RuntimeError(f"Tool error: {response['error']}")
            else:
                return str(response)
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("MCP tool call timed out")
        except Exception as e:
            raise RuntimeError(f"Failed to call MCP tool: {e}")
    
    def _call_python_fallback(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Fallback Python implementation when Node.js is unavailable."""
        if tool_name == "calculate":
            return self._calculate(arguments)
        elif tool_name == "get_bot_info":
            return self._get_bot_info(arguments)
        elif tool_name == "get_weather":
            return self._get_weather(arguments)
        elif tool_name == "fetch_url":
            return self._fetch_url(arguments)
        else:
            raise RuntimeError(f"Unknown tool: {tool_name}")
    
    def _calculate(self, args: Dict[str, Any]) -> str:
        """Simple calculator implementation."""
        operation = args.get("operation")
        a = float(args.get("a", 0))
        b = float(args.get("b", 0))
        
        if operation == "add":
            result = a + b
            return f"🔢 計算結果：{a} + {b} = {result}"
        elif operation == "subtract":
            result = a - b
            return f"🔢 計算結果：{a} - {b} = {result}"
        elif operation == "multiply":
            result = a * b
            return f"🔢 計算結果：{a} × {b} = {result}"
        elif operation == "divide":
            if b == 0:
                return "❌ 錯誤：除數不能為零"
            result = a / b
            return f"🔢 計算結果：{a} ÷ {b} = {result}"
        else:
            return f"❌ 不支援的運算：{operation}"
    
    def _get_bot_info(self, args: Dict[str, Any]) -> str:
        """Return bot information."""
        detail_level = args.get("detail_level", "basic")
        
        info = """🤖 Telegram Bot 資訊

📋 **基本功能**：
• AI 對話 - 使用 Google Gemini API
• 地震查詢 - 台灣地震資料
• MCP 工具 - 計算機、天氣等

⚙️ **MCP 狀態**：
• 運行模式：Python 簡化版（Node.js 不可用）
• 可用工具：計算機、Bot 資訊、天氣查詢、URL 獲取

💡 **提示**：安裝 Node.js 以解鎖完整 MCP 功能"""
        
        if detail_level == "detailed":
            info += """

📦 **完整功能列表**：
/help - 顯示幫助
/new - 開始新對話
/eq_latest - 最新地震資訊
/mcp_calc - 數學計算
/mcp_weather - 天氣查詢
/mcp_info - Bot 資訊"""
        
        return info
    
    def _get_weather(self, args: Dict[str, Any]) -> str:
        """Simulated weather information."""
        location = args.get("location", "未知地點")
        return f"""🌤️ {location} 天氣資訊（模擬）

📅 日期：{datetime.now().strftime("%Y-%m-%d")}
🌡️ 溫度：22°C
💧 濕度：65%
🌥️ 天氣：多雲

⚠️ 注意：這是模擬數據，請使用專業天氣服務獲取實際天氣資訊"""
    
    def _fetch_url(self, args: Dict[str, Any]) -> str:
        """Fetch data from a URL."""
        url = args.get("url")
        method = args.get("method", "GET").upper()
        
        if not url:
            return "❌ 錯誤：未提供 URL"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                body = args.get("body", "")
                headers = args.get("headers", {})
                response = requests.post(url, data=body, headers=headers, timeout=10)
            else:
                return f"❌ 不支援的 HTTP 方法：{method}"
            
            response.raise_for_status()
            
            # Try to format JSON response
            try:
                data = response.json()
                return f"✅ 請求成功\n\n```json\n{json.dumps(data, indent=2, ensure_ascii=False)}\n```"
            except:
                # Return raw text (truncate if too long)
                text = response.text[:1000]
                if len(response.text) > 1000:
                    text += "\n...(已截斷)"
                return f"✅ 請求成功\n\n{text}"
                
        except requests.exceptions.RequestException as e:
            return f"❌ 請求失敗：{e}"
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Call an MCP tool (Node.js preferred, Python fallback).
        
        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments for the tool
            
        Returns:
            str: The tool's response text
            
        Raises:
            RuntimeError: If the tool call fails
        """
        if self.nodejs_available:
            try:
                return self._call_nodejs_tool(tool_name, arguments)
            except Exception:
                # If Node.js call fails, silently fall back to Python
                return self._call_python_fallback(tool_name, arguments)
        else:
            # Use Python fallback directly
            return self._call_python_fallback(tool_name, arguments)


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client


def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Convenience function to call an MCP tool.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Dictionary of arguments for the tool
        
    Returns:
        str: The tool's response text
        
    Example:
        >>> result = call_mcp_tool("calculate", {"operation": "add", "a": 5, "b": 3})
        >>> print(result)
        Calculation result: 5 add 3 = 8
    """
    try:
        client = get_mcp_client()
        return client.call_tool(tool_name, arguments)
    except Exception as e:
        return f"❌ MCP Error: {e}"


# Specific helper functions for common tools

def get_bot_info(detailed: bool = False) -> str:
    """
    Get information about the bot.
    
    Args:
        detailed: If True, returns detailed information
        
    Returns:
        str: Bot information
    """
    detail_level = "detailed" if detailed else "basic"
    return call_mcp_tool("get_bot_info", {"detail_level": detail_level})


def calculate(operation: str, a: float, b: float) -> str:
    """
    Perform a mathematical calculation.
    
    Args:
        operation: One of "add", "subtract", "multiply", "divide"
        a: First number
        b: Second number
        
    Returns:
        str: Calculation result
    """
    return call_mcp_tool("calculate", {
        "operation": operation,
        "a": a,
        "b": b
    })


def get_weather(location: str) -> str:
    """
    Get weather information for a location.
    
    Args:
        location: Location name
        
    Returns:
        str: Weather information
    """
    return call_mcp_tool("get_weather", {"location": location})


def fetch_url(url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, 
              body: Optional[str] = None) -> str:
    """
    Fetch data from a URL.
    
    Args:
        url: URL to fetch
        method: HTTP method (GET or POST)
        headers: Optional HTTP headers
        body: Optional request body (for POST)
        
    Returns:
        str: Response from the URL
    """
    args = {
        "url": url,
        "method": method
    }
    if headers:
        args["headers"] = headers
    if body:
        args["body"] = body
    
    return call_mcp_tool("fetch_url", args)


if __name__ == "__main__":
    # Test the MCP client
    print("Testing MCP Client...")
    print("\n1. Get bot info:")
    print(get_bot_info())
    
    print("\n2. Calculate 25 + 17:")
    print(calculate("add", 25, 17))
    
    print("\n3. Get weather for Taipei:")
    print(get_weather("Taipei"))
    
    print("\nMCP Client test complete!")
