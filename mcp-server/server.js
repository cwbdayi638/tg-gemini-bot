#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// 常量定義
const MAX_RESPONSE_SIZE = 10000; // 最大響應大小（10KB）

// 創建 MCP 服務器實例
const server = new Server(
  {
    name: "tg-gemini-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 定義可用的工具
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_bot_info",
        description: "獲取 Telegram Bot 的基本信息和功能",
        inputSchema: {
          type: "object",
          properties: {
            detail_level: {
              type: "string",
              enum: ["basic", "detailed"],
              description: "返回的詳細程度（基本或詳細）",
              default: "basic",
            },
          },
        },
      },
      {
        name: "calculate",
        description: "執行簡單的數學計算",
        inputSchema: {
          type: "object",
          properties: {
            operation: {
              type: "string",
              enum: ["add", "subtract", "multiply", "divide"],
              description: "要執行的操作",
            },
            a: {
              type: "number",
              description: "第一個數字",
            },
            b: {
              type: "number",
              description: "第二個數字",
            },
          },
          required: ["operation", "a", "b"],
        },
      },
      {
        name: "get_weather",
        description: "獲取天氣信息（演示用）",
        inputSchema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "位置名稱",
            },
          },
          required: ["location"],
        },
      },
      {
        name: "fetch_url",
        description: "從外部服務器獲取數據，支援 HTTP GET 和 POST 請求",
        inputSchema: {
          type: "object",
          properties: {
            url: {
              type: "string",
              description: "要訪問的完整 URL（必須是 http:// 或 https://）",
            },
            method: {
              type: "string",
              enum: ["GET", "POST"],
              description: "HTTP 方法",
              default: "GET",
            },
            headers: {
              type: "object",
              description: "自定義 HTTP 標頭（可選）",
              additionalProperties: {
                type: "string",
              },
            },
            body: {
              type: "string",
              description: "POST 請求的內容（可選，僅用於 POST 方法）",
            },
          },
          required: ["url"],
        },
      },
    ],
  };
});

// 處理工具調用
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === "get_bot_info") {
      const detail_level = args.detail_level || "basic";
      
      const basicInfo = {
        name: "tg-gemini-bot",
        version: "1.0.0",
        description: "功能強大的 Telegram 機器人，整合 Gemini AI 與即時地震監測",
        status: "活躍開發中",
      };
      
      const detailedInfo = {
        ...basicInfo,
        features: [
          "Google Gemini AI 智慧對話",
          "即時地震資訊（CWA 與 USGS）",
          "網頁搜尋整合",
          "圖片分析",
          "互動式地震地圖",
        ],
        services: {
          earthquake: "台灣中央氣象署（CWA）+ 美國地質調查局（USGS）",
          ai: "Google Gemini",
          search: "多引擎網頁搜尋",
        },
        commands: [
          "/eq_latest - 最新顯著地震",
          "/eq_global - 全球地震（24小時）",
          "/eq_taiwan - 台灣地震（今年）",
          "/search - 網頁搜尋",
          "/help - 顯示所有指令",
        ],
      };
      
      const info = detail_level === "detailed" ? detailedInfo : basicInfo;
      
      return {
        content: [
          {
            type: "text",
            text: `Bot 資訊:\n${JSON.stringify(info, null, 2)}`,
          },
        ],
      };
    } else if (name === "calculate") {
      let result;
      const { operation, a, b } = args;
      
      switch (operation) {
        case "add":
          result = a + b;
          break;
        case "subtract":
          result = a - b;
          break;
        case "multiply":
          result = a * b;
          break;
        case "divide":
          if (b === 0) {
            throw new Error("除數不能為零");
          }
          result = a / b;
          break;
        default:
          throw new Error(`不支持的操作: ${operation}`);
      }
      
      return {
        content: [
          {
            type: "text",
            text: `計算結果: ${a} ${operation} ${b} = ${result}`,
          },
        ],
      };
    } else if (name === "get_weather") {
      // 演示用的模擬天氣數據
      const weatherData = {
        location: args.location,
        temperature: Math.floor(Math.random() * 30) + 10,
        condition: ["晴朗", "多雲", "小雨", "陰天"][Math.floor(Math.random() * 4)],
        humidity: Math.floor(Math.random() * 50) + 40,
        timestamp: new Date().toISOString(),
      };
      
      return {
        content: [
          {
            type: "text",
            text: `${args.location} 的天氣:\n溫度: ${weatherData.temperature}°C\n狀況: ${weatherData.condition}\n濕度: ${weatherData.humidity}%\n更新時間: ${weatherData.timestamp}`,
          },
        ],
      };
    } else if (name === "fetch_url") {
      // HTTP 客戶端工具 - 從外部服務器獲取數據
      const { url, method = "GET", headers = {}, body } = args;
      
      // 驗證 URL
      let urlObj;
      try {
        urlObj = new URL(url);
        if (!["http:", "https:"].includes(urlObj.protocol)) {
          throw new Error("只支援 HTTP 和 HTTPS 協議");
        }
      } catch (error) {
        throw new Error(`無效的 URL: ${error.message}`);
      }
      
      // 設置請求選項
      const fetchOptions = {
        method: method,
        headers: {
          "User-Agent": "MCP-Server/1.0",
          ...headers,
        },
        // 設置超時（10秒）
        signal: AbortSignal.timeout(10000),
      };
      
      // 添加請求體（僅用於 POST）
      if (method === "POST" && body) {
        fetchOptions.body = body;
        if (!headers["Content-Type"]) {
          fetchOptions.headers["Content-Type"] = "application/json";
        }
      }
      
      // 執行請求
      const response = await fetch(url, fetchOptions);
      
      // 獲取響應內容
      const contentType = response.headers.get("content-type") || "";
      let responseData;
      
      if (contentType.includes("application/json")) {
        responseData = await response.json();
        responseData = JSON.stringify(responseData, null, 2);
      } else {
        responseData = await response.text();
      }
      
      // 限制響應大小（最多 10KB）
      if (responseData.length > MAX_RESPONSE_SIZE) {
        responseData = responseData.substring(0, MAX_RESPONSE_SIZE) + "\n\n... (內容已截斷，僅顯示前 10000 字符)";
      }
      
      return {
        content: [
          {
            type: "text",
            text: `HTTP ${method} 請求到 ${url}\n狀態碼: ${response.status} ${response.statusText}\nContent-Type: ${contentType}\n\n響應內容:\n${responseData}`,
          },
        ],
      };
    }

    throw new Error(`未知工具: ${name}`);
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `錯誤: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// 啟動服務器
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("TG-Gemini MCP Server 已啟動 - 提供以下工具:");
  console.error("  1. get_bot_info - 獲取 Bot 資訊");
  console.error("  2. calculate - 執行數學計算");
  console.error("  3. get_weather - 獲取天氣信息");
  console.error("  4. fetch_url - 從外部服務器獲取數據 (HTTP客戶端)");
}

main().catch((error) => {
  console.error("服務器錯誤:", error);
  process.exit(1);
});
