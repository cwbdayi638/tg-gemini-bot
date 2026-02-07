# tg-gemini-bot

[English](README_EN.md) | [繁體中文](README.md) | [简体中文](README_zh-CN.md)

**tg-gemini-bot** 是一个功能强大的 Telegram 机器人助手，整合了实时地震信息、新闻服务和 AI 对话能力。

## 🎯 主要功能

- **🌍 地震信息服务**：整合台湾中央气象署 (CWA) 和美国地质调查局 (USGS) 的实时地震数据
- **📰 新闻服务**：通过 RSS 订阅源获取科技、台湾和全球新闻
- **🤖 AI 对话**：使用 Hugging Face Transformers 进行本地 AI 对话（无需 API 密钥）
- **💬 GitHub Copilot AI**：整合 GitHub Copilot SDK，提供高级 AI 编程协助和对话功能
- **📸 图片分析**：使用 AI 分析和描述图片内容（需要 API 密钥）

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
- `/eq_ai <问题>` - 使用 AI 查询地震数据
  - 范例：`/eq_ai 昨天花莲有地震吗？`
  - 范例：`/eq_ai 2024年4月规模6以上的地震有哪些？`

**数据来源：**
- 台湾中央气象署开放数据平台
- 美国地质调查局 (USGS) 地震 API
- Hugging Face Transformers (本地 AI 模型，无需 API 密钥)

### 📰 新闻服务

通过 RSS 订阅源获取实时新闻信息：

**新闻指令：**
- `/news` - 从多个来源获取一般新闻
- `/news_tech` - 科技新闻（Hacker News）
- `/news_taiwan` - 台湾新闻（中央社）
- `/news_global` - 全球新闻（BBC）
- `/news_finance` - 财经新闻（从多个来源）
- `/news_cw` - 天下杂志
- `/news_gvm` - 远见杂志
- `/news_udn` - 经济日报
- `/news_bbc_chinese` - BBC中文网

**数据来源：**
- Hacker News - 科技新闻
- 中央社 (CNA) - 台湾新闻
- BBC News - 全球新闻
- 天下杂志 (CommonWealth Magazine) - 财经与深度
- 远见杂志 (Global Views Monthly) - 财经与深度
- 经济日报 (Economic Daily News) - 财经新闻
- BBC中文网 (BBC Chinese) - 国际新闻

### 🤖 AI 对话功能

机器人现在使用 Hugging Face Transformers 本地模型，**无需 API 密钥**即可运行：
- 进行自然语言对话（使用 DialoGPT 模型）
- 智能地震查询（自动理解日期、规模等条件）
- 回答各种问题
- 提供信息和建议

**注意：** 首次使用时，模型会自动下载，可能需要一些时间和网络流量。模型大小约为数百 MB。

### 💬 GitHub Copilot AI

机器人现在整合了 GitHub Copilot SDK，提供高级 AI 协助功能：

**功能特点：**
- 编程问题解答和代码示例
- 调试协助和错误说明
- 算法和最佳实践建议
- 技术概念解释
- 多种编程语言支持

**Copilot 指令：**
- `/copilot <消息>` - 与 GitHub Copilot AI 对话
- `/copilot_new` - 开始新对话（清除历史记录）
- `/copilot_help` - 获取 Copilot 功能说明

**使用示例：**
- `/copilot 如何在 Python 中反转字符串？`
- `/copilot 解释什么是 REST API`
- `/copilot 写一个找质数的函数`

**注意：** 使用 GitHub Copilot SDK 需要有效的 GitHub Copilot 订阅或 BYOK（自带密钥）设置。每个聊天室的对话记录会分别保存。

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

### 可选设置

| 变量 | 必填 | 描述 |
| --- | --- | --- |
| CWA_API_KEY | ❌ 否 | 台湾中央气象署 API 密钥，用于访问显著地震数据。从 [CWA 开放数据平台](https://opendata.cwa.gov.tw/) 获取 |
| MCP_SERVER_URL | ❌ 否 | MCP 服务器 URL，用于高级地震数据库搜索（默认：`https://cwadayi-mcp-2.hf.space`） |
| MCP_WEB_SEARCH_URL | ❌ 否 | MCP 网页搜索服务器 URL，用于增强新闻和网页搜索功能（使用 [open-webSearch](https://github.com/Aas-ee/open-webSearch)，例如：`http://localhost:3000`） |
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
   ```
   https://api.telegram.org/bot<您的BOT_TOKEN>/setWebhook?url=<您的Vercel网址>
   ```

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

### MCP 网页搜索服务器设置（可选）

若要启用增强的新闻和网页搜索功能，可以设置 [open-webSearch](https://github.com/Aas-ee/open-webSearch) MCP 服务器：

1. **使用 NPX 快速启动**（最简单）：
   ```bash
   # 基本使用
   npx open-websearch@latest
   
   # 或使用环境变量配置
   DEFAULT_SEARCH_ENGINE=duckduckgo ENABLE_CORS=true npx open-websearch@latest
   ```

2. **使用 Docker 部署**：
   ```bash
   docker run -d --name web-search \
     -p 3000:3000 \
     -e ENABLE_CORS=true \
     -e CORS_ORIGIN=* \
     ghcr.io/aas-ee/open-web-search:latest
   ```

3. **配置机器人**：
   在机器人的环境变量中设置：
   ```
   MCP_WEB_SEARCH_URL=http://localhost:3000
   ```

**注意**：如果不设置 `MCP_WEB_SEARCH_URL`，新闻功能仍会使用传统的 RSS 订阅方式。

## 💡 使用范例

### 查询地震信息
```
用户：/eq_latest
机器人：🚨 CWA Latest Significant Earthquake
----------------------------------
Time: 2024-02-06 15:30:00
Location: 花莲县近海
Magnitude: M5.8 | Depth: 15 km
Report: [链接]
```

### 查询新闻
```
用户：/news_tech
机器人：📰 Technology News (Hacker News)
----------------------------------
1. New AI Model Released...
2. Tech Company Announces...
...
```

### AI 对话（需要 API 密钥）
```
用户：你好，请介绍一下台湾的地震情况
机器人：台湾位于环太平洋地震带上，是地震活动频繁的地区...
```

### 图片分析（需要 API 密钥）
```
用户：[发送图片并附上文字「描述这张图片」]
机器人：这张图片显示了...
```

## 🔐 安全功能

- **身份验证支持**：可选的用户/群组限制
- **管理员指令**：特定指令仅限管理员使用
- **调试模式**：可选的日志记录功能

## 📝 注意事项

1. **AI 功能**：
   - 机器人使用 Hugging Face Transformers 本地模型，**不需要 Google API 密钥**
   - 首次启动时会自动下载模型（约数百 MB），请确保有足够的磁盘空间和网络流量
   - AI 对话功能会在本地运行，速度取决于服务器硬件配置

2. **API 密钥**：
   - 没有 `CWA_API_KEY`：部分地震信息功能可能受限

3. **群组使用**：
   - 在群组中使用时，请 @机器人 或回复机器人的消息

4. **对话历史**：
   - 使用 `/new` 指令可以清除对话历史，开始新的对话

## 📄 授权

详见 [LICENSE.txt](LICENSE.txt)

---

**用 ❤️ 制作，为快速、高效且实用的机器人交互**
