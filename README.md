# tg-gemini-bot

[English](README.md) | [繁體中文](README.md)

**tg-gemini-bot** 是一個極速、基於規則的 Telegram 助手。最初是為 Google Gemini 設計的，現在已重構為高效能的規則引擎，能夠立即回應常見任務，無需大型語言模型 (LLM) 的延遲或成本。

![screen](./screenshots/screen.png)

## 逐步導覽：基於規則的機器人增強功能
我已經升級了您的 TG 機器人中的基於規則的邏輯，使其功能更強大、互動性更高。

### 核心增強功能

#### 🧮 進階數學支援
機器人現在可以處理複雜的數學表達式：
- **括號**：`(12 + 8) * 5`
- **指數**：`2^10` 或 `2**10`
- **小數**：`10.5 / 2.1`
- **安全性**：使用沙盒化的 `eval`，無法存取內建函數。

#### 🌤️ 詳細的天氣資訊
改進了回應的多樣性：
- 「明天」或「本週」的預報。
- 特定溫度的資訊（攝氏度和華氏度）。
- 與位置無關但具描述性的結果。

#### 📅 增強的時間和日期
- **特定查詢**：可以專門回應僅關於時間、日期、星期幾或月份的請求。
- **詳細輸出**：包括週數和一年中的第幾天。

#### 👋 語境感知的問候語
- **時段感應**：根據目前的小時數，以「早安」、「午安」等方式打招呼。
- **意圖檢測**：識別告別（"bye"）和感謝（"thank you"）。

#### 🤖 專屬說明選單
一個新的高優先級規則 (`function0_help`) 提供所有功能的清晰概覽。
- **觸發字**："help"、"guide"、"menu"、"capabilities"、"what can you do"。
- **內容**：透過範例解釋數學、天氣、時間和問候功能。

## 功能特點

- **閃電般的速度**：使用本地規則邏輯立即生成回應。
- **基於 Flask**：輕量級且易於擴展。
- **支援 Vercel**：只需點擊一下即可部署到 Vercel。
- **支援 Docker**：容器化設計，便於在任何地方部署。
- **隱私優先**：不向外部 AI 供應商發送數據。

## 準備工作

準備好這些內容，然後將其作為環境變量填寫在 Vercel 或您的 Docker 環境中。

- **BOT_TOKEN**

  透過 [@BotFather](https://t.me/BotFather) 建立您自己的 Telegram 機器人並獲取 Token。

- **ALLOWED_USERS / ALLOWED_GROUPS** (可選)

  限制特定用戶或群組的存取。

## 開始使用

1. **部署到 Vercel**：點擊按鈕進行克隆和部署。
2. **設置環境變量**：配置您的 `BOT_TOKEN`。
3. **連接 Webhook**：訪問 `https://api.telegram.org/bot<bot-token>/setWebhook?url=<vercel-domain>` 以連接您的機器人。

## 環境變量

| 變量 | 必填 | 描述 |
| --- | --- | --- |
| BOT_TOKEN | 是 | 您的 Telegram 機器人 Token。 |
| ALLOWED_USERS | 否 | 允許的用戶名或 ID（支援正則表達式）。 |
| ALLOWED_GROUPS | 否 | 允許的群組 ID 或用戶名。 |
| ADMIN_ID | 否 | 用於管理員指令的 Telegram ID。 |
| IS_DEBUG_MODE | 否 | 設置為 `1` 以啟用調試指令。 |
| AUCH_ENABLE | 否 | 設置為 `0` 以禁用身份驗證。 |

## 指令列表

- `/help` - 顯示所有功能和使用指南。
- `/new` - 開始新的互動。
- `/get_my_info` - 獲取您的 Telegram ID。
- `/get_group_info` - 獲取群組 ID（在群組中）。
- `/5g_test` - 運行模擬速度測試。

## 技術變更
`gemini.py`：重構了從 `function1_math` 到 `function5_fallback` 的功能。
