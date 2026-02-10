# MCP Server 使用範例

本文件提供 MCP (Model Context Protocol) 伺服器的實際使用範例。

## 📋 目錄

- [透過 Telegram Bot 使用](#透過-telegram-bot-使用)
- [透過 GitHub Copilot 使用](#透過-github-copilot-使用)
- [透過 Python 程式使用](#透過-python-程式使用)
- [進階應用範例](#進階應用範例)

---

## 透過 Telegram Bot 使用

MCP 工具已整合至 Telegram Bot，可以直接透過指令使用。

### 1. 取得 Bot 資訊

查詢 Bot 的功能和可用服務：

```
/mcp_info
```

**回應範例：**
```
Bot 資訊:
{
  "name": "tg-gemini-bot",
  "version": "1.0.0",
  "description": "功能強大的 Telegram 機器人，整合 Gemini AI 與即時地震監測",
  "status": "活躍開發中",
  "features": [
    "Google Gemini AI 智慧對話",
    "即時地震資訊（CWA 與 USGS）",
    "網頁搜尋整合",
    "圖片分析",
    "互動式地震地圖"
  ],
  "services": {
    "earthquake": "台灣中央氣象署（CWA）+ 美國地質調查局（USGS）",
    "ai": "Google Gemini",
    "search": "多引擎網頁搜尋"
  },
  "commands": [
    "/eq_latest - 最新顯著地震",
    "/eq_global - 全球地震（24小時）",
    "/eq_taiwan - 台灣地震（今年）",
    "/search - 網頁搜尋",
    "/help - 顯示所有指令"
  ]
}
```

### 2. 數學計算

執行基本數學運算：

**加法：**
```
/mcp_calc add 25 17
```
回應：`🔢 Calculation result: 25 add 17 = 42`

**減法：**
```
/mcp_calc subtract 100 42
```
回應：`🔢 Calculation result: 100 subtract 42 = 58`

**乘法：**
```
/mcp_calc multiply 7 8
```
回應：`🔢 Calculation result: 7 multiply 8 = 56`

**除法：**
```
/mcp_calc divide 100 4
```
回應：`🔢 Calculation result: 100 divide 4 = 25`

**錯誤處理：**
```
/mcp_calc divide 10 0
```
回應：`❌ 計算失敗: Cannot divide by zero`

### 3. 天氣查詢（模擬）

查詢任何地點的模擬天氣資訊：

```
/mcp_weather 台北
```

**回應範例：**
```
🌤️ Weather in 台北:
Temperature: 24°C
Condition: Sunny
Humidity: 65%
Updated: 2026-02-10T01:45:00.000Z
```

```
/mcp_weather Tokyo
```

```
/mcp_weather New York
```

### 4. HTTP 資料獲取

從外部 API 獲取數據：

**範例 1：獲取 JSON 數據**
```
/mcp_fetch https://api.github.com/repos/cwbdayi638/tg-gemini-bot
```

**範例 2：獲取地震數據**
```
/mcp_fetch https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson
```

**範例 3：獲取天氣數據**
```
/mcp_fetch https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization=YOUR_API_KEY
```

---

## 透過 GitHub Copilot 使用

在 VS Code 中配置 MCP 伺服器後，可以在 GitHub Copilot Chat 中使用 MCP 工具。

### 設定

1. 開啟 VS Code 設定 (`settings.json`):
   - Windows: `%APPDATA%\Code\User\settings.json`
   - macOS: `~/Library/Application Support/Code/User/settings.json`
   - Linux: `~/.config/Code/User/settings.json`

2. 添加 MCP 伺服器配置：

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

### 使用範例

在 GitHub Copilot Chat 中輸入：

**範例 1：獲取 Bot 資訊**
```
使用 MCP 工具獲取 tg-gemini-bot 的詳細資訊
```

**範例 2：執行計算**
```
使用 MCP 工具計算 123 加 456
```

**範例 3：查詢天氣**
```
使用 MCP 工具查詢倫敦的天氣
```

**範例 4：獲取外部數據**
```
使用 MCP 工具從 https://api.example.com/data 獲取數據
```

Copilot 會自動：
1. 識別需要使用哪個 MCP 工具
2. 準備正確的參數
3. 調用工具並獲取結果
4. 將結果整合到回應中

---

## 透過 Python 程式使用

在 Python 程式中直接使用 MCP 客戶端。

### 基本使用

```python
from api.mcp_client_service import get_bot_info, calculate, get_weather, fetch_url

# 1. 獲取 Bot 資訊
info = get_bot_info(detailed=True)
print(info)

# 2. 執行計算
result = calculate("add", 25, 17)
print(result)  # Calculation result: 25 add 17 = 42

# 3. 查詢天氣
weather = get_weather("Taipei")
print(weather)

# 4. 獲取外部數據
data = fetch_url("https://api.github.com/repos/cwbdayi638/tg-gemini-bot")
print(data)
```

### 進階使用

```python
from api.mcp_client_service import call_mcp_tool

# 使用自定義參數調用工具
result = call_mcp_tool("fetch_url", {
    "url": "https://api.example.com/data",
    "method": "POST",
    "headers": {
        "Authorization": "Bearer YOUR_TOKEN",
        "Content-Type": "application/json"
    },
    "body": '{"query": "test"}'
})

print(result)
```

### 錯誤處理

```python
from api.mcp_client_service import calculate

try:
    result = calculate("divide", 10, 0)
    print(result)
except Exception as e:
    print(f"Error: {e}")
```

---

## 進階應用範例

### 範例 1：批次計算

```python
from api.mcp_client_service import calculate

operations = [
    ("add", 10, 5),
    ("subtract", 20, 8),
    ("multiply", 6, 7),
    ("divide", 100, 4),
]

results = []
for op, a, b in operations:
    result = calculate(op, a, b)
    results.append(result)
    print(f"{op}: {result}")
```

### 範例 2：多地點天氣查詢

```python
from api.mcp_client_service import get_weather

cities = ["台北", "Tokyo", "New York", "London", "Paris"]

for city in cities:
    weather = get_weather(city)
    print(f"\n{city}:")
    print(weather)
```

### 範例 3：API 數據聚合

```python
from api.mcp_client_service import fetch_url
import json

# 獲取多個 API 的數據
urls = [
    "https://api.github.com/repos/cwbdayi638/tg-gemini-bot",
    "https://api.github.com/users/cwbdayi638",
]

data = []
for url in urls:
    result = fetch_url(url)
    # 處理結果...
    data.append(result)

# 整合數據...
```

### 範例 4：在 Telegram 指令處理器中使用

```python
from api.mcp_client_service import calculate

def handle_custom_command(command: str) -> str:
    """處理自定義計算指令"""
    # 範例：/calc 25 + 17
    if command.startswith("/calc"):
        parts = command.split()
        if len(parts) >= 4:
            num1 = float(parts[1])
            operator = parts[2]
            num2 = float(parts[3])
            
            op_map = {"+": "add", "-": "subtract", "*": "multiply", "/": "divide"}
            operation = op_map.get(operator)
            
            if operation:
                return calculate(operation, num1, num2)
    
    return "Invalid command"
```

---

## 🔧 疑難排解

### 問題 1：MCP 工具無法使用

**症狀：** 執行 MCP 指令時顯示「MCP 客戶端服務無法使用」

**解決方法：**
1. 確認 Node.js 已安裝（`node --version`）
2. 確認 MCP 伺服器檔案存在於 `mcp-server/server.js`
3. 檢查 Python 錯誤日誌

### 問題 2：計算結果錯誤

**症狀：** 計算結果不正確或出現錯誤

**解決方法：**
1. 確認輸入的數字格式正確
2. 檢查運算符是否正確（add, subtract, multiply, divide）
3. 除法時確保除數不為零

### 問題 3：HTTP 獲取超時

**症狀：** 使用 `/mcp_fetch` 時超時

**解決方法：**
1. 確認 URL 正確且可訪問
2. 檢查網路連線
3. 使用較快的 API 端點
4. MCP 伺服器的超時設定為 10 秒

---

## 📚 相關文件

- [MCP Server README](mcp-server/README.md) - MCP 伺服器詳細說明
- [主要 README](README.md) - Bot 整體功能說明
- [MCP 官方文檔](https://modelcontextprotocol.io/) - MCP 協議說明

---

*最後更新：2026-02-10*
