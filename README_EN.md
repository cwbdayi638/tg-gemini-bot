# tg-gemini-bot

[English](README_EN.md) | [繁體中文](README.md) | [简体中文](README_zh-CN.md)

**tg-gemini-bot** is a powerful Telegram bot assistant that integrates real-time earthquake information, news services, and AI conversation capabilities.

## 🎯 Main Features

- **🌍 Earthquake Information Services**: Integrated real-time earthquake data from Taiwan Central Weather Administration (CWA) and USGS
- **📰 News Services**: Get technology, Taiwan, and global news through RSS feeds
- **🤖 AI Conversations**: Intelligent conversations powered by Google Gemini 1.5 (Optional)
- **📸 Image Analysis**: AI-powered image analysis and description (requires API key)

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
- Google Gemini 1.5 Flash (AI features)

### 📰 News Services

Get real-time news from multiple sources via RSS feeds:

**News Commands:**
- `/news` - General news from multiple sources
- `/news_tech` - Technology news (Hacker News)
- `/news_taiwan` - Taiwan news (CNA)
- `/news_global` - Global news (BBC)

**Data Sources:**
- Hacker News - Technology news
- Central News Agency (CNA) - Taiwan news
- BBC News - Global news

### 🤖 AI Conversation Features

When `GOOGLE_API_KEY` environment variable is configured, the bot can:
- Engage in natural language conversations
- Answer various questions
- Provide intelligent suggestions and analysis

### 📸 Image Analysis

Send images to the bot and it will analyze and describe the content using AI (requires API key configuration).

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
| GOOGLE_API_KEY | ❌ No | Google Gemini API key for AI conversations and image analysis. Get from [Google AI Studio](https://makersuite.google.com/app/apikey) |
| CWA_API_KEY | ❌ No | Taiwan Central Weather Administration API key for significant earthquake data. Get from [CWA Open Data Platform](https://opendata.cwa.gov.tw/) |
| MCP_SERVER_URL | ❌ No | MCP server URL for advanced earthquake database search (default: `https://cwadayi-mcp-2.hf.space`) |
| MCP_WEB_SEARCH_URL | ❌ No | MCP web search server URL for enhanced news and web search features (using [open-webSearch](https://github.com/Aas-ee/open-webSearch), e.g., `http://localhost:3000`) |
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
     -e GOOGLE_API_KEY="your-gemini-api-key" \
     -e CWA_API_KEY="your-cwa-api-key" \
     -p 8080:8080 \
     tg-gemini-bot
   ```

3. **Set up Webhook**:
   Point the webhook to your Docker service URL.

### MCP Web Search Server Setup (Optional)

To enable enhanced news and web search features, you can set up the [open-webSearch](https://github.com/Aas-ee/open-webSearch) MCP server:

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

**Note**: If `MCP_WEB_SEARCH_URL` is not set, news features will still work using traditional RSS feeds.

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

### Query News
```
User: /news_tech
Bot: 📰 Technology News (Hacker News)
----------------------------------
1. New AI Model Released...
2. Tech Company Announces...
...
```

### AI Conversation (requires API key)
```
User: Hello, tell me about earthquakes in Taiwan
Bot: Taiwan is located on the Pacific Ring of Fire, which makes it one of the most seismically active regions...
```

### Image Analysis (requires API key)
```
User: [Send an image with caption "Describe this image"]
Bot: This image shows...
```

## 🔐 Security Features

- **Authentication Support**: Optional user/group restrictions
- **Admin Commands**: Specific commands restricted to administrators
- **Debug Mode**: Optional logging functionality
- **Safety Settings**: Gemini API safety configurations

## 📝 Notes

1. **API Keys**:
   - Without `GOOGLE_API_KEY`: Bot still works but cannot perform AI conversations and image analysis
   - Without `CWA_API_KEY`: Some earthquake information features may be limited

2. **Group Usage**:
   - When using in groups, @mention the bot or reply to its messages

3. **Conversation History**:
   - Use `/new` command to clear conversation history and start fresh

## 📄 License

See [LICENSE.txt](LICENSE.txt)

---

**Made with ❤️ for fast, efficient, and practical bot interactions**
