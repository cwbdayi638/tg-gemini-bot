# tg-gemini-bot

[繁體中文](README.md) | [简体中文](README_zh-CN.md) | [English](README_EN.md)

**tg-gemini-bot** 是一個功能強大的 Telegram 機器人助手，整合了即時地震資訊和 AI 對話能力。

## 🎯 主要功能

- **🌍 地震資訊服務**：整合台灣中央氣象署 (CWA) 和美國地質調查局 (USGS) 的即時地震資料
- **💬 AI 對話**：整合 Google Gemini AI，提供智慧對話和圖片分析功能
- **🔍 智慧地震查詢**：使用自然語言查詢地震資料
- **🌐 網頁搜尋**：整合網頁搜尋功能

## 🚀 功能詳情

### 🌍 地震資訊服務

整合台灣中央氣象署 (CWA) 和美國地質調查局 (USGS) 的即時地震資訊：

**即時地震資訊：**
- `/eq_latest` - 最新顯著地震報告（含地震報告圖片）
- `/eq_alert` - CWA 地震速報與預警
- `/eq_significant` - CWA 過去 7 天顯著有感地震列表

**全球地震監控：**
- `/eq_global` - 全球近 24 小時顯著地震（規模 5.0 以上）
- `/eq_taiwan` - 台灣區域今年顯著地震列表
- `/eq_map` - 外部地震查詢服務連結

**自訂查詢全球地震：**
- `/eq_query <起始日期> <結束日期> <最小規模>` - 查詢全球地震資料
  - 範例：`/eq_query 2024-07-01 2024-07-07 5.0`
  - 日期格式：YYYY-MM-DD
  - 規模範圍：0-10

**AI 智慧助理：**
- `/ai <問題>` - 使用 Ollama 回答一般問題
  - 範例：`/ai 台灣最高的山是什麼？`
  - 範例：`/ai 幫我寫一段旅遊建議`

**資料來源：**
- 台灣中央氣象署開放資料平台
- 美國地質調查局 (USGS) 地震 API

### 🔍 網頁搜尋

- `/search <關鍵字>` - 搜尋網頁
- `/websearch <關鍵字>` - 搜尋網頁（別名）

## 📋 基本指令

- `/help` 或 `/start` - 顯示幫助資訊和可用指令
- `/new` - 開始新的對話（清除對話歷史）
- `/get_my_info` - 獲取您的 Telegram ID
- `/get_group_info` - 獲取群組 ID（僅限群組）
- `/5g_test` - 運行模擬速度測試

## 🔧 環境變數設定

### 必要設定

| 變數 | 必填 | 描述 |
| --- | --- | --- |
| BOT_TOKEN | ✅ 是 | 您的 Telegram 機器人 Token（從 [@BotFather](https://t.me/BotFather) 獲取） |
| API_ACCESS_TOKEN | ❌ 否 | API 存取令牌，用於保護 Webhook 端點。設定後需要在 Telegram setWebhook 時使用 `secret_token` 參數，Telegram 會自動在請求標頭加入驗證 |

### 可選設定

| 變數 | 必填 | 描述 |
| --- | --- | --- |
| GOOGLE_API_KEY | ❌ 否 | Google Gemini API 金鑰，啟用 AI 對話功能 |
| OLLAMA_BASE_URL | ❌ 否 | Ollama 服務器 URL（預設：`http://ollama.zeabur.internal:11434`），用於 AI 對話功能 |
| OLLAMA_MODEL | ❌ 否 | Ollama 模型名稱（預設：`gemma3:270m`），用於 AI 對話功能 |
| CWA_API_KEY | ❌ 否 | 台灣中央氣象署 API 金鑰，用於存取顯著地震資料。從 [CWA 開放資料平台](https://opendata.cwa.gov.tw/) 取得 |
| MCP_SERVER_URL | ❌ 否 | MCP 伺服器 URL，用於進階地震資料庫搜尋（預設：`https://cwadayi-mcp-2.hf.space`） |
| HF_SPACE_URL | ❌ 否 | Hugging Face Space URL，機器人啟動時會發送 ping 請求以防止免費 Space 進入睡眠狀態 |
| ALLOWED_USERS | ❌ 否 | 允許使用的用戶名或 ID（支援正則表達式，多個值用空格或逗號分隔） |
| ALLOWED_GROUPS | ❌ 否 | 允許使用的群組 ID 或用戶名（多個值用空格或逗號分隔） |
| ADMIN_ID | ❌ 否 | 管理員的 Telegram ID，用於執行管理員指令 |
| IS_DEBUG_MODE | ❌ 否 | 設置為 `1` 以啟用調試模式 |
| AUCH_ENABLE | ❌ 否 | 設置為 `0` 以禁用身份驗證（預設啟用） |

## 🚀 部署指南

### Vercel 部署

1. **Fork 此專案**到您的 GitHub 帳號

2. **部署到 Vercel**：
   - 前往 [Vercel](https://vercel.com) 並登入
   - 點擊「New Project」
   - 選擇您 fork 的專案
   - 配置環境變數（至少需要 `BOT_TOKEN`）
   - 點擊「Deploy」

3. **設置 Webhook**：
   部署完成後，訪問以下網址設置 Telegram Webhook：
   
   **基本設定（無驗證）**：
   ```
   https://api.telegram.org/bot<您的BOT_TOKEN>/setWebhook?url=<您的Vercel網址>
   ```
   
   **啟用 Token 驗證（推薦）**：
   若您設定了 `API_ACCESS_TOKEN` 環境變數，需要在設置 webhook 時加入 `secret_token` 參數：
   ```
   https://api.telegram.org/bot<您的BOT_TOKEN>/setWebhook?url=<您的Vercel網址>&secret_token=<您的API_ACCESS_TOKEN>
   ```
   Telegram 會在每次請求時自動加入 `X-Telegram-Bot-Api-Secret-Token` 標頭進行驗證，提高安全性。

### Docker 部署

1. **構建 Docker 映像**：
   ```bash
   docker build -t tg-gemini-bot .
   ```

2. **運行容器**：
   ```bash
   docker run -d \
     -e BOT_TOKEN="您的機器人Token" \
     -e CWA_API_KEY="您的CWA API金鑰" \
     -p 8080:8080 \
     tg-gemini-bot
   ```

3. **設置 Webhook**：
   將 Webhook 指向您的 Docker 服務網址。

## 💡 使用範例

### 查詢地震資訊
```
用戶：/eq_latest
機器人：🚨 中央氣象署最新顯著地震
----------------------------------
時間：2024-02-06 15:30:00
位置：花蓮縣近海
規模：M5.8 | 深度：15 公里
報告：[連結]
```

### AI 對話
```
用戶：你好，請介紹一下台灣的地震情況
機器人：台灣位於環太平洋地震帶上，是地震活動頻繁的地區...
```

### AI 問答
```
用戶：/ai 台灣最高的山是什麼？
機器人：玉山，海拔 3952 公尺，是台灣的最高峰。
```

### AI 新聞查詢
```
用戶：/ai_news_latest 5
機器人：🤖 AI 最新新聞 (最多 5 篇)
========================================

📰 OpenAI 發布新版 GPT-4 Turbo
來源：OpenAI Blog
摘要：OpenAI 今天宣布推出 GPT-4 Turbo...
連結：https://...

📰 Google DeepMind 的最新研究突破
來源：DeepMind Blog
摘要：DeepMind 研究團隊在蛋白質摺疊方面取得重大突破...
...

用戶：/ai_news_search transformer 10
機器人：🔍 搜尋結果：「transformer」
========================================

找到 10 篇相關新聞...

用戶：/ai_news_source OpenAI Blog 3
機器人：📡 新聞來源：OpenAI Blog
========================================

最新 3 篇來自 OpenAI Blog 的文章...
```

## 🔐 安全功能

- **身份驗證支援**：可選的用戶/群組限制
- **管理員指令**：特定指令僅限管理員使用
- **調試模式**：可選的日誌記錄功能

## 📝 注意事項

1. **API 金鑰**：
   - 沒有 `CWA_API_KEY`：部分地震資訊功能可能受限
   - 沒有 `GOOGLE_API_KEY`：AI 對話功能將無法使用

2. **群組使用**：
   - 在群組中使用時，請 @機器人 或回覆機器人的訊息

3. **對話歷史**：
   - 使用 `/new` 指令可以清除對話歷史，開始新的對話

## 📄 授權

詳見 [LICENSE.txt](LICENSE.txt)

---

**用 ❤️ 製作，為快速、高效且實用的機器人互動**
