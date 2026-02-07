# tg-gemini-bot

[English](README_EN.md) | [繁體中文](README.md) | [简体中文](README_zh-CN.md)

**tg-gemini-bot** 是一個功能強大的 Telegram 機器人助手，整合了即時地震資訊、新聞服務和 AI 對話能力。

## 🎯 主要功能

- **🌍 地震資訊服務**：整合台灣中央氣象署 (CWA) 和美國地質調查局 (USGS) 的即時地震資料
- **📰 新聞服務**：透過 RSS 訂閱源獲取科技、台灣和全球新聞
- **🤖 AI 對話**：使用 Google Gemini 1.5 進行智慧對話（可選）
- **📸 圖片分析**：使用 AI 分析和描述圖片內容（需要 API 金鑰）

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

**AI 智慧助理：**
- `/eq_ai <問題>` - 使用 AI 查詢地震資料
  - 範例：`/eq_ai 昨天花蓮有地震嗎？`
  - 範例：`/eq_ai 2024年4月規模6以上的地震有哪些？`

**資料來源：**
- 台灣中央氣象署開放資料平台
- 美國地質調查局 (USGS) 地震 API
- Google Gemini 1.5 Flash (AI 功能)

### 📰 新聞服務

透過 RSS 訂閱源獲取即時新聞資訊：

**新聞指令：**
- `/news` - 從多個來源獲取一般新聞
- `/news_tech` - 科技新聞（Hacker News）
- `/news_taiwan` - 台灣新聞（中央社）
- `/news_global` - 全球新聞（BBC）

**資料來源：**
- Hacker News - 科技新聞
- 中央社 (CNA) - 台灣新聞
- BBC News - 全球新聞

### 🤖 AI 對話功能

當設定 `GOOGLE_API_KEY` 環境變數後，機器人可以：
- 進行自然語言對話
- 回答各種問題
- 提供智慧建議和分析

### 📸 圖片分析

發送圖片給機器人，它會使用 AI 分析圖片內容並提供描述（需要設定 API 金鑰）。

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

### 可選設定

| 變數 | 必填 | 描述 |
| --- | --- | --- |
| GOOGLE_API_KEY | ❌ 否 | Google Gemini API 金鑰，用於 AI 對話和圖片分析功能。從 [Google AI Studio](https://makersuite.google.com/app/apikey) 取得 |
| CWA_API_KEY | ❌ 否 | 台灣中央氣象署 API 金鑰，用於存取顯著地震資料。從 [CWA 開放資料平台](https://opendata.cwa.gov.tw/) 取得 |
| MCP_SERVER_URL | ❌ 否 | MCP 伺服器 URL，用於進階地震資料庫搜尋（預設：`https://cwadayi-mcp-2.hf.space`） |
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
   ```
   https://api.telegram.org/bot<您的BOT_TOKEN>/setWebhook?url=<您的Vercel網址>
   ```

### Docker 部署

1. **構建 Docker 映像**：
   ```bash
   docker build -t tg-gemini-bot .
   ```

2. **運行容器**：
   ```bash
   docker run -d \
     -e BOT_TOKEN="您的機器人Token" \
     -e GOOGLE_API_KEY="您的Gemini API金鑰" \
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
機器人：🚨 CWA Latest Significant Earthquake
----------------------------------
Time: 2024-02-06 15:30:00
Location: 花蓮縣近海
Magnitude: M5.8 | Depth: 15 km
Report: [連結]
```

### 查詢新聞
```
用戶：/news_tech
機器人：📰 Technology News (Hacker News)
----------------------------------
1. New AI Model Released...
2. Tech Company Announces...
...
```

### AI 對話（需要 API 金鑰）
```
用戶：你好，請介紹一下台灣的地震情況
機器人：台灣位於環太平洋地震帶上，是地震活動頻繁的地區...
```

### 圖片分析（需要 API 金鑰）
```
用戶：[發送圖片並附上文字「描述這張圖片」]
機器人：這張圖片顯示了...
```

## 🔐 安全功能

- **身份驗證支援**：可選的用戶/群組限制
- **管理員指令**：特定指令僅限管理員使用
- **調試模式**：可選的日誌記錄功能
- **安全設置**：Gemini API 安全設定

## 📝 注意事項

1. **API 金鑰**：
   - 沒有 `GOOGLE_API_KEY`：機器人仍可運行，但無法進行 AI 對話和圖片分析
   - 沒有 `CWA_API_KEY`：部分地震資訊功能可能受限

2. **群組使用**：
   - 在群組中使用時，請 @機器人 或回覆機器人的訊息

3. **對話歷史**：
   - 使用 `/new` 指令可以清除對話歷史，開始新的對話

## 📄 授權

詳見 [LICENSE.txt](LICENSE.txt)

---

**用 ❤️ 製作，為快速、高效且實用的機器人互動**
