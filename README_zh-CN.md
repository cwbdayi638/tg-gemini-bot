# tg-gemini-bot

[繁體中文](README.md) | [简体中文](README_zh-CN.md) | [English](README_EN.md)

**tg-gemini-bot** 是一个功能强大的 Telegram 机器人助手，整合了实时地震信息和 AI 对话能力。

## 🎯 主要功能

- **🌍 地震信息服务**：整合台湾中央气象署 (CWA) 和美国地质调查局 (USGS) 的实时地震数据
- **💬 AI 对话**：整合 Google Gemini AI，提供智能对话和图片分析功能
- **🔍 智能地震查询**：使用自然语言查询地震数据
- **🌐 网页搜索**：整合网页搜索功能
- **📰 AI 新闻聚合器**：从 150+ 来源获取最新 AI/ML/数据科学新闻
- **🔧 MCP 工具**：提供 Model Context Protocol 工具，可用于计算、数据获取等功能

## 🚀 功能详情

### 🌍 地震信息服务

整合台湾中央气象署 (CWA) 和美国地质调查局 (USGS) 的实时地震信息：

**实时地震信息：**
- `/eq_latest` - 最新显著地震报告（含地震报告图片）
- `/eq_alert` - CWA 地震速报与预警
- `/eq_significant` - CWA 过去 7 天显著有感地震列表

**全球地震监控：**
- `/eq_global` - 全球近 24 小时显著地震（规模 5.0 以上）
- `/eq_taiwan` - 台湾区域今年显著地震列表
- `/eq_map` - 外部地震查询服务链接

**AI 智能助理：**
- `/ai <问题>` - 使用 Ollama 回答一般问题
  - 范例：`/ai 台湾最高的山是什么？`
  - 范例：`/ai 帮我写一段旅游建议`

**数据来源：**
- 台湾中央气象署开放数据平台
- 美国地质调查局 (USGS) 地震 API

### 🔍 网页搜索

- `/search <关键字>` - 搜索网页
- `/websearch <关键字>` - 搜索网页（别名）

### 📰 AI 新闻聚合器

整合 Hugging Face AI 新闻聚合器，从 150+ 精选来源获取最新的 AI、机器学习和数据科学新闻：

**获取新闻：**
- `/ai_news_latest [数量]` - 获取最新 AI 新闻（默认 15 篇）
  - 范例：`/ai_news_latest 10`
- `/ai_news_search <关键字> [数量]` - 搜索特定主题的 AI 新闻
  - 范例：`/ai_news_search GPT-4 15`
  - 范例：`/ai_news_search machine learning`
- `/ai_news_source <来源名称> [数量]` - 从特定来源获取新闻
  - 范例：`/ai_news_source OpenAI Blog 5`
  - 范例：`/ai_news_source DeepMind Blog`

**管理来源：**
- `/ai_news_sources [类别]` - 列出可用的新闻来源
  - 范例：`/ai_news_sources top` - 显示热门来源
  - 范例：`/ai_news_sources all` - 显示全部来源

**新闻来源包括：**
- 研究实验室：OpenAI、DeepMind、Google AI、NVIDIA、Microsoft Research
- 科技新闻：TechCrunch、The Verge、MIT Technology Review、Ars Technica
- 学术资源：arXiv (cs.LG, cs.CV, cs.CL)
- 产业博客：Hugging Face、TensorFlow、LangChain、PyTorch
- 社群：Reddit (r/MachineLearning, r/artificial)、Medium、Substack

**数据来源：**
- [AI News Aggregator](https://huggingface.co/spaces/cwbdayi/ai-news-aggregator) (Hugging Face Space)

### 🔧 MCP 工具

基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 的扩展功能：

- `/mcp_info` - 获取 Bot 详细信息
- `/mcp_calc <运算> <数字1> <数字2>` - 数学计算（支持 add, subtract, multiply, divide）
  - 范例：`/mcp_calc add 25 17`
- `/mcp_weather <地点>` - 查询天气信息（模拟）
- `/mcp_fetch <URL>` - 从外部 API 获取数据

💡 **MCP 功能说明**：本 Bot 整合了 MCP 服务器，可通过标准化协议提供额外工具。这些工具也可以在 GitHub Copilot 等 MCP 兼容客户端中使用。详见 [MCP_USAGE_EXAMPLES.md](MCP_USAGE_EXAMPLES.md)。

## 📋 基本指令

- `/help` 或 `/start` - 显示帮助信息和可用指令
- `/new` - 开始新的对话（清除对话历史）
- `/get_my_info` - 获取您的 Telegram ID
- `/get_group_info` - 获取群组 ID（仅限群组）
- `/5g_test` - 运行模拟速度测试

## 🔧 环境变量设置

### 必要设置

| 变量 | 必填 | 描述 |
| --- | --- | --- |
| BOT_TOKEN | ✅ 是 | 您的 Telegram 机器人 Token（从 [@BotFather](https://t.me/BotFather) 获取） |
| API_ACCESS_TOKEN | ❌ 否 | API 访问令牌，用于保护 Webhook 端点。设置后需要在 Telegram setWebhook 时使用 `secret_token` 参数，Telegram 会自动在请求头加入验证 |

### 可选设置

| 变量 | 必填 | 描述 |
| --- | --- | --- |
| GOOGLE_API_KEY | ❌ 否 | Google Gemini API 密钥，启用 AI 对话功能 |
| OLLAMA_BASE_URL | ❌ 否 | Ollama 服务器 URL（默认：`http://ollama.zeabur.internal:11434`），用于 AI 对话功能 |
| OLLAMA_MODEL | ❌ 否 | Ollama 模型名称（默认：`gemma3:270m`），用于 AI 对话功能 |
| CWA_API_KEY | ❌ 否 | 台湾中央气象署 API 密钥，用于访问显著地震数据。从 [CWA 开放数据平台](https://opendata.cwa.gov.tw/) 获取 |
| MCP_SERVER_URL | ❌ 否 | MCP 服务器 URL，用于高级地震数据库搜索（默认：`https://cwadayi-mcp-2.hf.space`） |
| MCP_WEB_SEARCH_URL | ❌ 否 | MCP 网页搜索服务器 URL，用于增强网页搜索功能 |
| AI_NEWS_AGGREGATOR_URL | ❌ 否 | AI 新闻聚合器 Hugging Face Space 名称（默认：`cwbdayi/ai-news-aggregator`） |
| ALLOWED_USERS | ❌ 否 | 允许使用的用户名或 ID（支持正则表达式，多个值用空格或逗号分隔） |
| ALLOWED_GROUPS | ❌ 否 | 允许使用的群组 ID 或用户名（多个值用空格或逗号分隔） |
| ADMIN_ID | ❌ 否 | 管理员的 Telegram ID，用于执行管理员指令 |
| IS_DEBUG_MODE | ❌ 否 | 设置为 `1` 以启用调试模式 |
| AUCH_ENABLE | ❌ 否 | 设置为 `0` 以禁用身份验证（默认启用） |

## 🚀 部署指南

### Vercel 部署

1. **Fork 此项目**到您的 GitHub 账号

2. **部署到 Vercel**：
   - 前往 [Vercel](https://vercel.com) 并登录
   - 点击「New Project」
   - 选择您 fork 的项目
   - 配置环境变量（至少需要 `BOT_TOKEN`）
   - 点击「Deploy」

3. **设置 Webhook**：
   部署完成后，访问以下网址设置 Telegram Webhook：
   
   **基本设置（无验证）**：
   ```
   https://api.telegram.org/bot<您的BOT_TOKEN>/setWebhook?url=<您的Vercel网址>
   ```
   
   **启用 Token 验证（推荐）**：
   若您设置了 `API_ACCESS_TOKEN` 环境变量，需要在设置 webhook 时加入 `secret_token` 参数：
   ```
   https://api.telegram.org/bot<您的BOT_TOKEN>/setWebhook?url=<您的Vercel网址>&secret_token=<您的API_ACCESS_TOKEN>
   ```
   Telegram 会在每次请求时自动加入 `X-Telegram-Bot-Api-Secret-Token` 头进行验证，提高安全性。

### Docker 部署

1. **构建 Docker 镜像**：
   ```bash
   docker build -t tg-gemini-bot .
   ```

2. **运行容器**：
   ```bash
   docker run -d \
     -e BOT_TOKEN="您的机器人Token" \
     -e CWA_API_KEY="您的CWA API密钥" \
     -p 8080:8080 \
     tg-gemini-bot
   ```

3. **设置 Webhook**：
   将 Webhook 指向您的 Docker 服务网址。

## 💡 使用范例

### 查询地震信息
```
用户：/eq_latest
机器人：🚨 中央气象署最新显著地震
----------------------------------
时间：2024-02-06 15:30:00
位置：花莲县近海
规模：M5.8 | 深度：15 公里
报告：[链接]
```

### AI 对话
```
用户：你好，请介绍一下台湾的地震情况
机器人：台湾位于环太平洋地震带上，是地震活动频繁的地区...
```

### AI 问答
```
用户：/ai 台湾最高的山是什么？
机器人：玉山，海拔 3952 米，是台湾的最高峰。
```

## 🔐 安全功能

- **身份验证支持**：可选的用户/群组限制
- **管理员指令**：特定指令仅限管理员使用
- **调试模式**：可选的日志记录功能

## 📝 注意事项

1. **API 密钥**：
   - 没有 `CWA_API_KEY`：部分地震信息功能可能受限
   - 没有 `GOOGLE_API_KEY`：AI 对话功能将无法使用

2. **群组使用**：
   - 在群组中使用时，请 @机器人 或回复机器人的消息

3. **对话历史**：
   - 使用 `/new` 指令可以清除对话历史，开始新的对话

## 📄 授权

详见 [LICENSE.txt](LICENSE.txt)

---

**用 ❤️ 制作，为快速、高效且实用的机器人交互**
