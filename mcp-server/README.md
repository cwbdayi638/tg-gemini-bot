# TG-Gemini MCP Server

This is a Model Context Protocol (MCP) server that provides additional tools and capabilities for the Telegram Gemini Bot.

## 📋 Overview

The MCP server extends the bot's functionality by providing standardized tools that can be accessed via the MCP protocol. This allows for modular, reusable functionality that can be integrated with AI assistants like GitHub Copilot or other MCP-compatible clients.

## 🚀 Features

### Available Tools

1. **get_bot_info** - Get information about the Telegram bot
   - Basic info: name, version, status
   - Detailed info: features, services, available commands

2. **calculate** - Perform mathematical calculations
   - Supports: add, subtract, multiply, divide
   - Error handling for division by zero

3. **get_weather** - Get weather information (demo)
   - Simulated weather data for any location
   - Returns temperature, conditions, humidity

4. **fetch_url** - HTTP client for external APIs
   - Supports GET and POST requests
   - Custom headers support
   - 10-second timeout
   - Response size limiting (10KB max)

## 📦 Installation

### Prerequisites

- Node.js >= 18.0.0
- npm >= 8.0.0

### Setup

```bash
cd mcp-server
npm install
```

## 🔧 Usage

### Standalone Testing

```bash
npm start
```

You should see:
```
TG-Gemini MCP Server 已啟動 - 提供以下工具:
  1. get_bot_info - 獲取 Bot 資訊
  2. calculate - 執行數學計算
  3. get_weather - 獲取天氣信息
  4. fetch_url - 從外部服務器獲取數據
```

### Integration with GitHub Copilot

Add this to your VS Code `settings.json`:

```json
{
  "github.copilot.advanced": {
    "mcpServers": {
      "tg-gemini": {
        "command": "node",
        "args": ["/absolute/path/to/tg-gemini-bot/mcp-server/server.js"]
      }
    }
  }
}
```

Replace `/absolute/path/to/` with the actual path to your project.

### Using in GitHub Copilot Chat

Once configured, you can ask Copilot to use the MCP tools:

```
使用 MCP 工具獲取 bot 的詳細資訊
使用 MCP 工具計算 25 + 17
使用 MCP 工具查詢台北的天氣
使用 MCP 工具從 https://api.example.com/data 獲取數據
```

## 🔌 Integration with Telegram Bot

The MCP server can also be accessed programmatically from the Python Telegram bot through the `mcp_client_service.py` module.

Example usage in Python:
```python
from api.mcp_client_service import call_mcp_tool

# Get bot info
result = call_mcp_tool("get_bot_info", {"detail_level": "detailed"})

# Perform calculation
result = call_mcp_tool("calculate", {
    "operation": "add",
    "a": 25,
    "b": 17
})

# Fetch external data
result = call_mcp_tool("fetch_url", {
    "url": "https://api.example.com/data",
    "method": "GET"
})
```

## 🛠️ Development

### Adding New Tools

To add a new tool to the MCP server:

1. Add the tool definition in `ListToolsRequestSchema` handler
2. Add the tool implementation in `CallToolRequestSchema` handler
3. Update the startup message to list the new tool
4. Test the tool with `npm start`

Example:
```javascript
// 1. Define the tool
{
  name: "my_new_tool",
  description: "Description of what the tool does",
  inputSchema: {
    type: "object",
    properties: {
      param1: {
        type: "string",
        description: "Parameter description",
      },
    },
    required: ["param1"],
  },
}

// 2. Implement the tool
if (name === "my_new_tool") {
  // Tool logic here
  return {
    content: [
      {
        type: "text",
        text: `Result: ${args.param1}`,
      },
    ],
  };
}
```

## 📚 MCP Protocol

The Model Context Protocol (MCP) is an open protocol that standardizes how AI applications connect to external data sources and tools. Learn more at [modelcontextprotocol.io](https://modelcontextprotocol.io/).

### Key Concepts

- **MCP Server**: Provides tools and resources (this server)
- **MCP Client**: Consumes tools from servers (GitHub Copilot, Python bot)
- **Transport**: Communication method (stdio, HTTP)
- **Tools**: Functions that can be called with parameters

## 🔒 Security

- All HTTP requests use a 10-second timeout
- Response sizes are limited to 10KB
- Only HTTP and HTTPS protocols are allowed for URL fetching
- Input validation for all tool parameters

## 📝 License

Same as parent project (see LICENSE.txt)

## 🤝 Contributing

To contribute:
1. Add your tools following the existing patterns
2. Ensure error handling is robust
3. Update this README with new tools
4. Test thoroughly before committing

---

*Built with ❤️ using the Model Context Protocol*
