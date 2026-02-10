# tg-gemini-bot

[繁體中文](README.md) | [简体中文](README_zh-CN.md) | [English](README_EN.md)

**tg-gemini-bot** is a powerful Telegram bot assistant that integrates real-time earthquake information and AI conversation capabilities.

## 🎯 Main Features

- **🌍 Earthquake Information Services**: Integrated real-time earthquake data from Taiwan Central Weather Administration (CWA) and USGS
- **💬 AI Conversation**: Integrated Google Gemini AI for intelligent conversation and image analysis
- **🔍 Smart Earthquake Query**: Use natural language to query earthquake data
- **🌐 Web Search**: Integrated web search functionality

## 🚀 Feature Details

### 🌍 Earthquake Information Services

Integrated real-time earthquake data from Taiwan Central Weather Administration (CWA) and USGS:

**Real-time Earthquake Information:**
- `/eq_latest` - Latest significant earthquake report (with image)
- `/eq_alert` - CWA earthquake early warnings
- `/eq_significant` - CWA significant earthquakes in past 7 days

**Global Earthquake Monitoring:**
- `/eq_global` - Global significant earthquakes in past 24 hours (M≥5.0)
- `/eq_taiwan` - Taiwan region significant earthquakes this year
- `/eq_map` - Link to external earthquake query service

**AI Smart Assistant:**
- `/ai <question>` - Ask general questions answered by Ollama
  - Example: `/ai What is the highest mountain in Taiwan?`
  - Example: `/ai Give me a short travel tip for Taipei`

**Data Sources:**
- Taiwan Central Weather Administration Open Data Platform
- United States Geological Survey (USGS) Earthquake API

### 🔍 Web Search

- `/search <query>` - Search the web
- `/websearch <query>` - Search the web (alias)

## 📋 Basic Commands

- `/help` or `/start` - Show help information and available commands
- `/new` - Start a new conversation (clear conversation history)
- `/get_my_info` - Get your Telegram ID
- `/get_group_info` - Get group ID (group only)
- `/5g_test` - Run simulated speed test

## 🔧 Environment Variables

### Required Configuration

| Variable | Required | Description |
| --- | --- | --- |
| BOT_TOKEN | ✅ Yes | Your Telegram bot token (get from [@BotFather](https://t.me/BotFather)) |
| API_ACCESS_TOKEN | ❌ No | API access token for webhook endpoint protection. If set, all POST requests to webhook must include `x-access-token` header |

### Optional Configuration

| Variable | Required | Description |
| --- | --- | --- |
| GOOGLE_API_KEY | ❌ No | Google Gemini API key, enables AI conversation features |
| OLLAMA_BASE_URL | ❌ No | Ollama server URL (default: `http://ollama.zeabur.internal:11434`), used for AI conversation |
| OLLAMA_MODEL | ❌ No | Ollama model name (default: `gemma3:270m`), used for AI conversation |
| CWA_API_KEY | ❌ No | Taiwan Central Weather Administration API key for significant earthquake data. Get from [CWA Open Data Platform](https://opendata.cwa.gov.tw/) |
| MCP_SERVER_URL | ❌ No | MCP server URL for advanced earthquake database search (default: `https://cwadayi-mcp-2.hf.space`) |
| MCP_WEB_SEARCH_URL | ❌ No | MCP web search server URL for enhanced web search features |
| ALLOWED_USERS | ❌ No | Allowed usernames or IDs (supports regex, separate multiple values with space or comma) |
| ALLOWED_GROUPS | ❌ No | Allowed group IDs or usernames (separate multiple values with space or comma) |
| ADMIN_ID | ❌ No | Telegram ID for admin commands |
| IS_DEBUG_MODE | ❌ No | Set to `1` to enable debug mode |
| AUCH_ENABLE | ❌ No | Set to `0` to disable authentication (enabled by default) |

## 🚀 Deployment Guide

### Deploy to Vercel

1. **Fork this project** to your GitHub account

2. **Deploy to Vercel**:
   - Go to [Vercel](https://vercel.com) and sign in
   - Click "New Project"
   - Select your forked repository
   - Configure environment variables (at least `BOT_TOKEN` is required)
   - Click "Deploy"

3. **Set up Webhook**:
   After deployment, visit the following URL to set up Telegram Webhook:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<YOUR_VERCEL_URL>
   ```

### Deploy with Docker

1. **Build Docker image**:
   ```bash
   docker build -t tg-gemini-bot .
   ```

2. **Run container**:
   ```bash
   docker run -d \
     -e BOT_TOKEN="your-bot-token" \
     -e CWA_API_KEY="your-cwa-api-key" \
     -p 8080:8080 \
     tg-gemini-bot
   ```

3. **Set up Webhook**:
   Point the webhook to your Docker service URL.

## 💡 Usage Examples

### Query Earthquake Information
```
User: /eq_latest
Bot: 🚨 CWA Latest Significant Earthquake
----------------------------------
Time: 2024-02-06 15:30:00
Location: Near Hualien Coast
Magnitude: M5.8 | Depth: 15 km
Report: [link]
```

### AI Conversation
```
User: Hello, please introduce Taiwan's earthquake situation
Bot: Taiwan is located on the Pacific Ring of Fire, an area with frequent seismic activity...
```

### AI Q&A
```
User: /ai What is the highest mountain in Taiwan?
Bot: Yushan (Jade Mountain) at 3,952 meters is the tallest peak in Taiwan.
```

## 🔐 Security Features

- **Authentication Support**: Optional user/group restrictions
- **Admin Commands**: Specific commands restricted to administrators
- **Debug Mode**: Optional logging functionality

## 📝 Notes

1. **API Keys**:
   - Without `CWA_API_KEY`: Some earthquake information features may be limited
   - Without `GOOGLE_API_KEY`: AI conversation features will not be available

2. **Group Usage**:
   - When using in groups, @mention the bot or reply to its messages

3. **Conversation History**:
   - Use `/new` command to clear conversation history and start fresh

## 📄 License

See [LICENSE.txt](LICENSE.txt)

---

**Made with ❤️ for fast, efficient, and practical bot interactions**
