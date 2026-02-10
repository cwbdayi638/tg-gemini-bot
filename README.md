# tg-gemini-bot

[繁體中文](README.md) | [简体中文](README_zh-CN.md) | [English](README_EN.md)

**tg-gemini-bot** 是一個功能強大的 Telegram 機器人助手，整合了即時地震資訊和 AI 對話能力。

## 🎯 主要功能

- **🌍 地震資訊服務**：整合台灣中央氣象署 (CWA) 和美國地質調查局 (USGS) 的即時地震資料
- **💬 AI 對話**：整合 Google Gemini AI，提供智慧對話和圖片分析功能
- **🔍 智慧地震查詢**：使用自然語言查詢地震資料
- **🌐 網頁搜尋**：整合網頁搜尋功能
- **🔧 MCP 工具**：提供 Model Context Protocol 工具，可用於計算、資料獲取等功能

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
- `/eq_ai <問題>` - 使用 AI 查詢地震資料
  - 範例：`/eq_ai 昨天花蓮有地震嗎？`
  - 範例：`/eq_ai 2024年4月規模6以上的地震有哪些？`

**資料來源：**
- 台灣中央氣象署開放資料平台
- 美國地質調查局 (USGS) 地震 API

### 🔍 網頁搜尋

- `/search <關鍵字>` - 搜尋網頁
- `/websearch <關鍵字>` - 搜尋網頁（別名）

### 🔧 MCP 工具

基於 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 的擴展功能：

- `/mcp_info` - 取得 Bot 詳細資訊
- `/mcp_calc <運算> <數字1> <數字2>` - 數學計算（支援 add, subtract, multiply, divide）
  - 範例：`/mcp_calc add 25 17`
- `/mcp_weather <地點>` - 查詢天氣資訊（模擬）
- `/mcp_fetch <URL>` - 從外部 API 獲取數據

💡 **MCP 功能說明**：本 Bot 整合了 MCP 伺服器，可透過標準化協議提供額外工具。這些工具也可以在 GitHub Copilot 等 MCP 相容客戶端中使用。詳見 [MCP_USAGE_EXAMPLES.md](MCP_USAGE_EXAMPLES.md)。

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
| GOOGLE_API_KEY | ❌ 否 | Google Gemini API 金鑰，啟用 AI 對話功能 |
| CWA_API_KEY | ❌ 否 | 台灣中央氣象署 API 金鑰，用於存取顯著地震資料。從 [CWA 開放資料平台](https://opendata.cwa.gov.tw/) 取得 |
| MCP_SERVER_URL | ❌ 否 | MCP 伺服器 URL，用於進階地震資料庫搜尋（預設：`https://cwadayi-mcp-2.hf.space`） |
| MCP_WEB_SEARCH_URL | ❌ 否 | MCP 網頁搜尋伺服器 URL，用於增強網頁搜尋功能 |
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

### 智慧地震查詢
```
用戶：/eq_ai 昨天花蓮有地震嗎？
機器人：🌍 地震搜尋結果 (2024-02-05 至 2024-02-05, M≥4.5):
找到 1 筆地震記錄：
1. 時間：2024-02-05 15:30:00
   位置：花蓮縣近海
   規模：M5.2 | 深度：12 公里
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

## 🔧 MCP (Model Context Protocol) 整合

本專案整合了 **Model Context Protocol (MCP)** 伺服器，提供標準化的工具接口。MCP 是一個開放協議，讓 AI 應用程式能夠安全地連接到外部資源和工具。

### MCP 功能

- 🧮 **計算工具** - 執行數學運算
- 📊 **Bot 資訊** - 取得 Bot 功能和服務資訊
- 🌤️ **天氣查詢** - 模擬天氣數據
- 🌐 **HTTP 客戶端** - 從外部 API 獲取數據

### 使用 MCP 工具

#### 在 Telegram Bot 中：
```
/mcp_info                    # 取得 Bot 資訊
/mcp_calc add 25 17          # 計算 25 + 17
/mcp_weather 台北            # 查詢天氣
/mcp_fetch https://api.example.com/data  # 獲取外部數據
```

#### 在 GitHub Copilot 中：

1. 配置 VS Code `settings.json`：
```json
{
  "github.copilot.advanced": {
    "mcpServers": {
      "tg-gemini": {
        "command": "node",
        "args": ["/path/to/tg-gemini-bot/mcp-server/server.js"]
      }
    }
  }
}
```

2. 在 Copilot Chat 中使用：
```
使用 MCP 工具計算 123 + 456
使用 MCP 工具獲取 Bot 的詳細資訊
使用 MCP 工具從 API 獲取數據
```

### MCP 相關文件

- 📖 [MCP Server README](mcp-server/README.md) - MCP 伺服器完整說明
- 📚 [MCP 使用範例](MCP_USAGE_EXAMPLES.md) - 詳細使用指南和範例
- 🌐 [MCP 官方文檔](https://modelcontextprotocol.io/) - 協議規範

### MCP 部署模式

#### 模式 1：使用外部 MCP 伺服器（預設，推薦）

Bot 預設使用 HTTP 連接到外部 MCP 伺服器，無需安裝 Node.js：

- **預設伺服器**：`https://cwadayi-mcp-2.hf.space`
- **自訂伺服器**：設置環境變數 `MCP_SERVER_URL`
- **優點**：部署簡單，適合 Vercel 等 Serverless 平台
- **適用於**：生產環境、Vercel 部署

#### 模式 2：本地 MCP 伺服器（選用）

僅在以下情況需要本地 Node.js 伺服器：
- GitHub Copilot 整合（VS Code 擴展）
- 本地開發和測試
- 自定義 MCP 工具開發

#### 方法 1：自動設定（推薦）

```bash
cd mcp-server
./setup.sh
```

設定腳本會：
- 檢查是否安裝 Node.js >= 18.0.0
- 檢查是否有 npm
- 自動安裝所有依賴套件

#### 方法 2：手動設定

```bash
cd mcp-server
npm install
npm start  # 測試伺服器
```

### 配置環境變數

**重要說明**：`MCP_SERVER_URL` 用於**地震資料庫搜尋**（Gradio API），不用於基本 MCP 工具（計算機等）。

```bash
# 地震資料庫 MCP 伺服器（選用，預設已設定）
MCP_SERVER_URL=https://cwadayi-mcp-2.hf.space

# 網頁搜尋 MCP 伺服器（選用）
MCP_WEB_SEARCH_URL=https://your-search-server.com
```

### MCP 工具運行模式

本 Bot 的 MCP 工具有三種運行模式：

1. **Python 簡化版**（預設，無需 Node.js）
   - ✅ 適用於 Vercel、Heroku 等 Serverless 平台
   - ✅ 自動啟用，無需配置
   - 📦 包含：計算機、Bot 資訊、天氣查詢、HTTP 請求

2. **Node.js 完整版**（本地開發/自定義）
   - 🔧 需要安裝 Node.js >= 18.0.0
   - 🎯 提供完整 MCP 協議支援
   - 🔄 自動檢測並啟用（如果可用）

3. **外部 API 整合**
   - 🌍 地震資料庫：`MCP_SERVER_URL` (Gradio API)
   - 🔍 網頁搜尋：`MCP_WEB_SEARCH_URL` (MCP 協議)

### 疑難排解

#### MCP 工具無回應

基本 MCP 工具（計算機、天氣等）：
- ✅ **無需配置**，使用內建 Python 實現
- 如看到錯誤，請檢查指令格式是否正確

地震資料查詢無結果：
1. 確認 `MCP_SERVER_URL` 設置正確（預設：`https://cwadayi-mcp-2.hf.space`）
2. 檢查網路連線狀態
3. 啟用 `IS_DEBUG_MODE=1` 查看詳細日誌

#### Node.js 相關（選用功能）

- ⚠️ 看到 "Node.js not found"？**可以忽略**，Bot 會自動使用 Python 版本
- 🔧 如需 Node.js 完整功能，參考上方"模式 2：本地 MCP 伺服器"安裝步驟
- ✅ Vercel 部署：無需 Node.js，Python 版本即可完整運行

---

**用 ❤️ 製作，為快速、高效且實用的機器人互動**
