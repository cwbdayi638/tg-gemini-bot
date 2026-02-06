# tg-gemini-bot

[EN](README.md) | [简中](README_zh-CN.md) 

The **tg-gemini-bot** is a lightning-fast, rule-based Telegram assistant. Originally designed for Google Gemini, it has been refactored into a high-performance rule engine that provides instant responses for common tasks without the latency or cost of a Large Language Model (LLM).

![screen](./screenshots/screen.png)

## Walkthrough: Rule-Based Bot Enhancements
I've upgraded the rule-based logic in your TG bot to make it more powerful and interactive.

### Core Enhancements

#### 🧮 Advanced Math Support
The bot now handles complex mathematical expressions:
- **Parentheses**: `(12 + 8) * 5`
- **Exponents**: `2^10` or `2**10`
- **Decimals**: `10.5 / 2.1`
- **Safety**: Uses a sandboxed `eval` with no access to built-ins.

#### 🌤️ Detailed Weather Information
Improved variety in responses:
- Forecasts for "tomorrow" or "this week".
- Temperature-specific information (Celsius and Fahrenheit).
- Location-agnostic but descriptive results.

#### 📅 Enhanced Time and Date
- **Specific Queries**: Can respond specifically to requests for just the time, date, day of the week, or month.
- **Detailed Output**: Includes week number and day of the year.

#### 👋 Context-Aware Greetings
- **Time of Day**: Greets with "Good morning", "Good afternoon", etc., based on the current hour.
- **Intent Detection**: Recognizes farewells ("bye") and thanks ("thank you").

#### 🤖 Dedicated Help Menu
A new high-priority rule (`function0_help`) provides a clear overview of all capabilities.
- **Trigger**: "help", "guide", "menu", "capabilities", "what can you do".
- **Content**: Explains Math, Weather, Time, and Greeting features with examples.

## Features

- **Blazing Fast**: Responses are generated instantly using local rule-based logic.
- **Flask-Based**: Lightweight and easy to extend.
- **Vercel Ready**: Deploy to Vercel with a single click.
- **Docker Support**: Containerized for easy deployment anywhere.
- **Privacy Focused**: No data is sent to external AI providers.

## Preparation

Get these things ready, and then fill them in as environment variables in Vercel or your Docker environment.

- **BOT_TOKEN**

  Create your own telegram bot via [@BotFather](https://t.me/BotFather) and obtain the token.

- **ALLOWED_USERS / ALLOWED_GROUPS** (Optional)

  Restrict access to specific users or groups.

## Get Started

1. **Deploy to Vercel**: Click the button to clone and deploy.
2. **Set Environment Variables**: Configure your `BOT_TOKEN`.
3. **Connect Webhook**: Visit `https://api.telegram.org/bot<bot-token>/setWebhook?url=<vercel-domain>` to connect your bot.

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| BOT_TOKEN | YES | Your Telegram bot token. |
| ALLOWED_USERS | No | Allowed usernames or IDs (regex supported). |
| ALLOWED_GROUPS | No | Allowed group IDs or usernames. |
| ADMIN_ID | No | Your Telegram ID for admin commands. |
| IS_DEBUG_MODE | No | Set to `1` to enable debug commands. |
| AUCH_ENABLE | No | Set to `0` to disable authentication. |

## Command List

- `/help` - Show all capabilities and usage guide.
- `/new` - Start a fresh interaction.
- `/get_my_info` - Get your Telegram ID.
- `/get_group_info` - Get Group ID (in groups).
- `/5g_test` - Run a speed test simulation.

## Technical Changes
`gemini.py`: Refactored `function1_math` through `function5_fallback`.
