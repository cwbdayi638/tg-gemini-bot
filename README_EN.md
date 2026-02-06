# tg-gemini-bot

[English](README_EN.md) | [繁體中文](README.md) | [简体中文](README_zh-CN.md)

**tg-gemini-bot** is a lightning-fast, rule-based Telegram assistant. Originally designed for Google Gemini, it has been refactored into a high-performance rule engine that responds instantly to common tasks without the latency or cost of large language models (LLMs).

## 🚀 Advanced Features Overview

This bot has been significantly upgraded with powerful rule-based functions that provide instant responses to a wide variety of tasks.

### 🧮 Advanced Mathematical Capabilities

The bot now handles complex mathematical expressions with scientific functions:

- **Basic Operations**: `(12 + 8) * 5`, `100 / 4`, `2^10`
- **Scientific Functions**: 
  - `sqrt(144)` - Square root
  - `sin(45)` - Sine (in degrees)
  - `cos(60)` - Cosine (in degrees)
  - `tan(30)` - Tangent (in degrees)
  - `log(100)` - Logarithm base 10
  - `ln(2.718)` - Natural logarithm
  - `exp(2)` - Exponential function
  - `abs(-15)` - Absolute value
  - `factorial(5)` - Factorial
- **Decimal Support**: `10.5 / 2.1`
- **Security**: Uses sandboxed `eval` with no access to built-in functions

**Examples:**
- "What is sqrt(256)?" → Returns 16
- "Calculate sin(90)" → Returns 1
- "log(1000)" → Returns 3

### 🔄 Unit Conversion System

Convert between various units instantly:

**Distance Conversions:**
- `10 km to miles` → 6.21 miles
- `5 miles to km` → 8.05 km
- `100 meters to feet` → 328.08 feet
- `50 feet to meters` → 15.24 meters

**Weight Conversions:**
- `5 kg to lbs` → 11.02 lbs
- `150 lbs to kg` → 68.04 kg

**Temperature Conversions:**
- `32 F to C` → 0°C
- `100 C to F` → 212°F
- `0 celsius to fahrenheit` → 32°F

### 🌤️ Enhanced Weather Information

Get detailed weather information with location awareness:

- **Current Weather**: "What's the weather?" or "Weather in Paris"
- **Tomorrow's Forecast**: "Weather tomorrow"
- **Weekly Forecast**: "Weather for this week" or "7 day forecast"
- **Specific Conditions**: "Is it going to rain?", "What's the temperature?", "Humidity today"
- **Wind Information**: "What's the wind speed?"

**Features:**
- Temperature in both Celsius and Fahrenheit
- Humidity and feels-like temperature
- Wind speed and direction
- UV index and visibility
- Location detection from your query

### 📅 Advanced Time & Date Functions

Comprehensive time and date capabilities with calculations:

**Current Information:**
- `What time is it?` - Current time with timezone
- `What's today's date?` - Full date information
- `What day is it?` - Day of the week

**Date Calculations:**
- `7 days from now` → Shows date 7 days in the future
- `30 days ago` → Shows date 30 days in the past
- `What's tomorrow's date?`
- `What was yesterday's date?`

**Timezone Support:**
- `Time in UTC+8` - Shows time in specified timezone
- `Timezone UTC-5` - Eastern time zone

**Detailed Information:**
- Week number of the year
- Day number of the year
- Month and year information

### 🌍 Language Detection

Simple language pattern detection for various scripts:

**Supported Languages:**
- Chinese (中文)
- Russian (Русский)
- Japanese (日本語)
- Korean (한국어)
- Arabic (العربية)
- Thai (ไทย)
- And more!

**Examples:**
- Send text with "你好" → Detects Chinese
- Ask "What language is this?" → Shows capabilities
- Mix languages → Detects all present languages

### 👋 Multilingual Greetings

Context-aware greetings with time-of-day intelligence:

**Supported Greeting Languages:**
- English: Hi, Hello, Hey
- Spanish: Hola
- French: Bonjour
- Italian: Ciao
- German: Hallo
- Portuguese: Olá
- Russian: Привет
- Chinese: 你好
- Japanese: こんにちは
- Korean: 안녕하세요

**Smart Responses:**
- Time-based greetings (morning, afternoon, evening)
- Farewell detection (bye, goodbye, see you)
- Thank you recognition (in multiple languages)

## 🎯 Key Features

- **⚡ Lightning Speed**: Instant responses using local rule logic
- **🔒 Privacy First**: No data sent to external AI providers
- **🎨 Rich Functionality**: 7+ advanced rule functions
- **🌐 Multilingual**: Support for multiple languages
- **📊 Smart Detection**: Pattern matching for intelligent responses
- **🛠️ Flask-Based**: Lightweight and easy to extend
- **☁️ Vercel Ready**: Deploy to Vercel with one click
- **🐳 Docker Support**: Containerized for easy deployment anywhere

## 📋 Prerequisites

Prepare the following and configure them as environment variables in Vercel or your Docker environment:

- **BOT_TOKEN** (Required)
  
  Create your own Telegram bot via [@BotFather](https://t.me/BotFather) and obtain the token.

- **ALLOWED_USERS** (Optional)
  
  Restrict access to specific users by username or ID.

- **ALLOWED_GROUPS** (Optional)
  
  Restrict access to specific groups.

## 🚀 Getting Started

### Deploy to Vercel

1. Click the deploy button to clone and deploy
2. Configure your `BOT_TOKEN` environment variable
3. Visit `https://api.telegram.org/bot<bot-token>/setWebhook?url=<vercel-domain>` to connect your bot

### Deploy with Docker

```bash
docker build -t tg-gemini-bot .
docker run -d -p 5000:5000 \
  -e BOT_TOKEN="your_bot_token" \
  tg-gemini-bot
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export BOT_TOKEN="your_bot_token"

# Run the application
python -m flask run
```

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| BOT_TOKEN | Yes | Your Telegram bot token from BotFather |
| ALLOWED_USERS | No | Allowed usernames or IDs (supports regex) |
| ALLOWED_GROUPS | No | Allowed group IDs or usernames |
| ADMIN_ID | No | Telegram ID for admin commands |
| IS_DEBUG_MODE | No | Set to `1` to enable debug commands |
| AUTH_ENABLE | No | Set to `0` to disable authentication |

## 🤖 Bot Commands

- `/help` - Display all capabilities and usage guide
- `/new` - Start a new interaction session
- `/get_my_info` - Get your Telegram ID
- `/get_group_info` - Get group ID (in group chats)
- `/5g_test` - Run a simulated speed test

## 💡 Usage Examples

### Mathematics
```
User: "What is sqrt(144)?"
Bot: "The result of sqrt(144) is 12."

User: "Calculate sin(45)"
Bot: "The result of sin(45) is 0.707107."

User: "log(1000)"
Bot: "The result of log(1000) is 3."
```

### Unit Conversion
```
User: "Convert 10 km to miles"
Bot: "10 km is equal to 6.21 miles."

User: "32 F to C"
Bot: "32 °F is equal to 0 °C."
```

### Date Calculations
```
User: "What date is 7 days from now?"
Bot: "7 days from now will be: Thursday, February 13, 2026"

User: "What time is it in UTC+8?"
Bot: "Time in UTC+8 is: 04:15:30 PM"
```

### Weather
```
User: "What's the weather in London?"
Bot: "The weather in London is currently pleasant with partly cloudy skies..."
```

## 🔧 Technical Architecture

### Rule Function Priority

The bot processes messages through a prioritized chain of rule functions:

1. **function0_help** - Help and capability overview
2. **function1_math** - Advanced mathematical calculations
3. **function6_unit_conversion** - Unit conversions
4. **function2_weather** - Weather information
5. **function3_time** - Time and date queries
6. **function7_language_detection** - Language detection
7. **function4_greeting** - Greetings and pleasantries
8. **function5_fallback** - Helpful fallback with suggestions

### File Structure

```
tg-gemini-bot/
├── api/
│   ├── gemini.py          # Core rule functions (upgraded)
│   ├── handle.py          # Message handling
│   ├── telegram.py        # Telegram API integration
│   ├── command.py         # Bot commands
│   ├── config.py          # Configuration
│   └── ...
├── screenshots/           # Documentation images
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── vercel.json           # Vercel deployment config
└── README.md             # This file
```

## 🔐 Security Features

- **Sandboxed Evaluation**: Math expressions are evaluated in a restricted environment
- **No External API Calls**: All processing done locally
- **Authentication Support**: Optional user/group restrictions
- **Privacy Focused**: No data logging or external transmission

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new rule functions
- Submit pull requests
- Improve documentation

## 📄 License

See [LICENSE.txt](LICENSE.txt) for details.

## 🌟 Acknowledgments

This bot demonstrates the power of rule-based systems for specific tasks, providing instant responses without the complexity and cost of large language models.

---

**Made with ❤️ for fast, efficient, and privacy-focused bot interactions**
