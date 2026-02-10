"""
MCP Client Service for Telegram Bot

This module provides a Python client to interact with the MCP server.
It allows the Telegram bot to call MCP tools programmatically.
"""

import subprocess
import json
import os
from typing import Dict, Any, Optional

# Configuration constants
MCP_CALL_TIMEOUT = 30  # Timeout for MCP tool calls in seconds
MCP_SERVER_HTTP_TIMEOUT = 10  # Should match server.js timeout setting


class MCPClient:
    """Client for interacting with the MCP server."""
    
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
        self._validate_server()
    
    def _validate_server(self):
        """Validate that the MCP server exists and Node.js is available."""
        if not os.path.exists(self.server_path):
            raise FileNotFoundError(f"MCP server not found at: {self.server_path}")
        
        # Check if Node.js is available
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("Node.js not available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raise RuntimeError("Node.js not found. Please install Node.js >= 18.0.0")
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments for the tool
            
        Returns:
            str: The tool's response text
            
        Raises:
            RuntimeError: If the tool call fails
        """
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
            try:
                # MCP server might output debug info to stderr, actual response is in stdout
                response = json.loads(result.stdout)
                
                # Extract content from MCP response
                if "content" in response and isinstance(response["content"], list):
                    # Combine all text content
                    texts = []
                    for item in response["content"]:
                        if isinstance(item, dict) and "text" in item:
                            texts.append(item["text"])
                    return "\n".join(texts)
                elif "error" in response:
                    raise RuntimeError(f"Tool error: {response['error']}")
                else:
                    return str(response)
            except json.JSONDecodeError as e:
                # If not JSON, return raw output
                return result.stdout if result.stdout else result.stderr
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("MCP tool call timed out")
        except Exception as e:
            raise RuntimeError(f"Failed to call MCP tool: {e}")


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
