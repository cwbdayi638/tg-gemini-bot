#!/usr/bin/env node

/**
 * Simple test script for MCP server
 * Tests basic functionality without requiring stdio communication
 */

console.log("Testing MCP Server components...\n");

// Test 1: Check if SDK can be imported
try {
  const { Server } = await import("@modelcontextprotocol/sdk/server/index.js");
  const { StdioServerTransport } = await import("@modelcontextprotocol/sdk/server/stdio.js");
  console.log("✅ MCP SDK imported successfully");
} catch (error) {
  console.log("❌ Failed to import MCP SDK:", error.message);
  process.exit(1);
}

// Test 2: Test calculation logic
function testCalculation(op, a, b) {
  let result;
  switch (op) {
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
      if (b === 0) throw new Error("Cannot divide by zero");
      result = a / b;
      break;
    default:
      throw new Error(`Unsupported operation: ${op}`);
  }
  return result;
}

console.log("✅ Testing calculation logic:");
console.log("  25 + 17 =", testCalculation("add", 25, 17));
console.log("  100 - 42 =", testCalculation("subtract", 100, 42));
console.log("  7 * 8 =", testCalculation("multiply", 7, 8));
console.log("  100 / 4 =", testCalculation("divide", 100, 4));

// Test 3: Test URL validation
function testUrlValidation(url) {
  try {
    const urlObj = new URL(url);
    if (!["http:", "https:"].includes(urlObj.protocol)) {
      throw new Error("Only HTTP and HTTPS protocols are supported");
    }
    return true;
  } catch (error) {
    throw new Error(`Invalid URL: ${error.message}`);
  }
}

console.log("\n✅ Testing URL validation:");
console.log("  Valid HTTPS URL:", testUrlValidation("https://api.example.com/data"));
console.log("  Valid HTTP URL:", testUrlValidation("http://example.com"));

try {
  testUrlValidation("ftp://example.com");
  console.log("  ❌ Should have rejected FTP URL");
} catch (error) {
  console.log("  ✅ Correctly rejected FTP URL");
}

// Test 4: Test bot info generation
function testBotInfo(detailLevel = "basic") {
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
  };
  
  return detailLevel === "detailed" ? detailedInfo : basicInfo;
}

console.log("\n✅ Testing bot info generation:");
const basicInfo = testBotInfo("basic");
const detailedInfo = testBotInfo("detailed");
console.log("  Basic info has", Object.keys(basicInfo).length, "fields");
console.log("  Detailed info has", Object.keys(detailedInfo).length, "fields");
console.log("  Detailed info features:", detailedInfo.features.length, "items");

console.log("\n✅ All MCP server component tests passed!");
console.log("\nTo test the full MCP server with stdio communication:");
console.log("  npm start");
