# tg-gemini-bot

[English](README_EN.md) | [繁體中文](README.md) | [简体中文](README_zh-CN.md)

**tg-gemini-bot** is a powerful Telegram bot assistant that integrates real-time earthquake information and AI conversation capabilities.

## 🎯 Main Features

- **🌍 Earthquake Information Services**: Integrated real-time earthquake data from Taiwan Central Weather Administration (CWA) and USGS
- **💬 GitHub Copilot AI**: Integrated GitHub Copilot SDK for advanced AI programming assistance and conversations
- **🔍 Smart Earthquake Query**: Use natural language to query earthquake data

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
- `/eq_ai <question>` - Query earthquake data using AI
  - Example: `/eq_ai Were there any earthquakes in Hualien yesterday?`
  - Example: `/eq_ai What earthquakes above magnitude 6 occurred in April 2024?`

**Data Sources:**
- Taiwan Central Weather Administration Open Data Platform
- United States Geological Survey (USGS) Earthquake API

### 💬 GitHub Copilot AI

The bot now integrates GitHub Copilot SDK, providing advanced AI assistance features:

**Key Features:**
- Programming questions and code examples
- Debugging help and error explanations
- Algorithm and best practice recommendations
- Technical concept explanations
- Multiple programming language support

**Copilot Commands:**
- `/copilot <message>` - Chat with GitHub Copilot AI
- `/copilot_new` - Start a new conversation (clear history)
- `/copilot_help` - Get help about Copilot features

**Usage Examples:**
- `/copilot How do I reverse a string in Python?`
- `/copilot Explain what is a REST API`
- `/copilot Write a function to find prime numbers`

**Note:** Using GitHub Copilot SDK requires a valid GitHub Copilot subscription or BYOK (Bring Your Own Key) setup. Conversation history is maintained separately for each chat.

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

### Optional Configuration

| Variable | Required | Description |
| --- | --- | --- |
| CWA_API_KEY | ❌ No | Taiwan Central Weather Administration API key for significant earthquake data. Get from [CWA Open Data Platform](https://opendata.cwa.gov.tw/) |
| MCP_SERVER_URL | ❌ No | MCP server URL for advanced earthquake database search (default: `https://cwadayi-mcp-2.hf.space`) |
| MCP_WEB_SEARCH_URL | ❌ No | MCP web search server URL for enhanced web search features (using [open-webSearch](https://github.com/Aas-ee/open-webSearch), e.g., `http://localhost:3000`) |
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

### MCP Web Search Server Setup (Optional)

To enable enhanced web search features, you can set up the [open-webSearch](https://github.com/Aas-ee/open-webSearch) MCP server:

1. **Quick start with NPX** (easiest):
   ```bash
   # Basic usage
   npx open-websearch@latest
   
   # Or with environment variables
   DEFAULT_SEARCH_ENGINE=duckduckgo ENABLE_CORS=true npx open-websearch@latest
   ```

2. **Deploy with Docker**:
   ```bash
   docker run -d --name web-search \
     -p 3000:3000 \
     -e ENABLE_CORS=true \
     -e CORS_ORIGIN=* \
     ghcr.io/aas-ee/open-web-search:latest
   ```

3. **Configure the bot**:
   Set the environment variable for the bot:
   ```
   MCP_WEB_SEARCH_URL=http://localhost:3000
   ```

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

### Smart Earthquake Query
```
User: /eq_ai Were there any earthquakes in Hualien yesterday?
Bot: 🌍 Earthquake Search Results (2024-02-05 to 2024-02-05, M≥4.5):
Found 1 earthquake(s):
1. Time: 2024-02-05 15:30:00
   Location: Hualien County Offshore
   Magnitude: M5.2 | Depth: 12 km
```

## 🔐 Security Features

- **Authentication Support**: Optional user/group restrictions
- **Admin Commands**: Specific commands restricted to administrators
- **Debug Mode**: Optional logging functionality

## 📝 Notes

1. **GitHub Copilot AI Features**:
   - Bot can integrate GitHub Copilot SDK for advanced AI conversations
   - Requires GitHub account and authorization to use Copilot features

2. **API Keys**:
   - Without `CWA_API_KEY`: Some earthquake information features may be limited

3. **Group Usage**:
   - When using in groups, @mention the bot or reply to its messages

4. **Conversation History**:
   - Use `/new` command to clear conversation history and start fresh

## 📄 License

See [LICENSE.txt](LICENSE.txt)

---

**Made with ❤️ for fast, efficient, and practical bot interactions**
