import os
import re
import math
from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional, Dict, Any
from .config import new_chat_info, prompt_new_info, gemini_err_info, generation_config, safety_settings

# Try to import the Google Generative AI SDK for function calling support
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Get API key from environment
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# --- Rule Functions ---

def function0_help(text: str) -> str:
    """Function 0: Overall help and capability overview"""
    keywords = ["help", "guide", "menu", "capabilities", "what can you do", "/help", "instruction"]
    if any(k in text.lower() for k in keywords):
        return (
            "🤖 **Advanced Rule-Based Bot Capabilities**\n\n"
            "I'm a powerful, fast, rule-based assistant! Here's what I can do:\n\n"
            "1️⃣ **Advanced Math**: Send expressions like `sqrt(16)`, `sin(45)`, `log(100)`, `2^10`, or `(5 + 5) * 2`\n"
            "2️⃣ **Unit Conversion**: Convert units like `10 km to miles`, `32 F to C`, `5 kg to lbs`\n"
            "3️⃣ **Weather**: Ask `What's the weather?`, `Forecast for tomorrow`, or `Weather in Paris`\n"
            "4️⃣ **Time & Date**: Ask `What time is it?`, `Date in 7 days`, `Timezone UTC+8`\n"
            "5️⃣ **Language Detection**: I can detect languages in your text\n"
            "6️⃣ **Friendly Chat**: Say `Hi`, `How are you?`, or `Thank you`\n\n"
            "💡 *Tip: I'm very fast because I use advanced rule-based logic!*"
        )
    return None

def function1_math(text: str) -> str:
    """Function 1: Advanced math calculations with scientific functions"""
    # Look for math keywords or expressions
    math_keywords = ["calculate", "compute", "what is", "what's", "solve", "=", "+", "-", "*", "/", "^", "**", "x",
                     "sqrt", "sin", "cos", "tan", "log", "ln", "exp", "abs", "factorial"]
    
    # Check if text contains math-related content
    has_math_keyword = any(keyword in text.lower() for keyword in math_keywords)
    has_digit = re.search(r'\d', text)
    
    if not has_math_keyword and not has_digit:
        return None
    
    text_lower = text.lower()
    
    # Handle scientific functions
    scientific_patterns = {
        r'sqrt\s*\(?\s*(\d+\.?\d*)\s*\)?': lambda x: math.sqrt(float(x)),
        r'sin\s*\(?\s*(-?\d+\.?\d*)\s*\)?': lambda x: math.sin(math.radians(float(x))),
        r'cos\s*\(?\s*(-?\d+\.?\d*)\s*\)?': lambda x: math.cos(math.radians(float(x))),
        r'tan\s*\(?\s*(-?\d+\.?\d*)\s*\)?': lambda x: math.tan(math.radians(float(x))),
        r'log\s*\(?\s*(\d+\.?\d*)\s*\)?': lambda x: math.log10(float(x)),
        r'ln\s*\(?\s*(\d+\.?\d*)\s*\)?': lambda x: math.log(float(x)),
        r'exp\s*\(?\s*(-?\d+\.?\d*)\s*\)?': lambda x: math.exp(float(x)),
        r'abs\s*\(?\s*(-?\d+\.?\d*)\s*\)?': lambda x: abs(float(x)),
        r'factorial\s*\(?\s*(\d+)\s*\)?': lambda x: math.factorial(int(x)),
    }
    
    # Try scientific functions first
    for pattern, func in scientific_patterns.items():
        match = re.search(pattern, text_lower)
        if match:
            try:
                value = match.group(1)
                result = func(value)
                
                # Format result nicely
                if isinstance(result, float):
                    if result.is_integer():
                        result = int(result)
                    else:
                        result = round(result, 6)
                
                # Extract function name properly
                func_name = pattern.split(r'\s')[0]
                return f"The result of `{func_name}({value})` is **{result}**."
            except (ValueError, ZeroDivisionError, OverflowError):
                # Skip invalid operations (e.g., sqrt of negative, log of non-positive)
                continue
            except Exception:
                continue
    
    # Extract mathematical expression - support parentheses, decimals, and exponents
    # Pattern matches: numbers (int/float), operators (+,-,*,/,**,^,x,%), and parentheses
    pattern = r"([\d\.\s\+\-\*\/\%\(\)\^x]+)"
    matches = re.findall(pattern, text)
    
    for expression in matches:
        # Clean up the expression
        expression = expression.strip()
        
        # Skip if too short or just whitespace
        if len(expression) < 3 or expression.isspace():
            continue
            
        # Replace x with * for multiplication and ^ with ** for Python exponentiation
        expression = expression.replace('x', '*').replace('^', '**')
        
        # Validate: only allow safe characters
        if not all(c in "0123456789+-*/.% ()" for c in expression):
            continue
        
        # Must contain at least one operator
        if not any(op in expression for op in ['+', '-', '*', '/', '%', '**']):
            continue
            
        try:
            # Safe evaluation for math expressions
            result = eval(expression, {"__builtins__": {}}, {})
            
            # Format result nicely
            if isinstance(result, float):
                # Round to 6 decimal places if needed
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 6)
            
            return f"The result of `{expression}` is **{result}**."
        except Exception:
            continue
    
    return None

def function2_weather(text: str) -> str:
    """Function 2: Enhanced weather information with location detection"""
    keywords = ["weather", "temperature", "forecast", "rain", "sunny", "cloudy", "climate", "hot", "cold", "warm"]
    
    if not any(k in text.lower() for k in keywords):
        return None
    
    # Check for specific weather queries
    text_lower = text.lower()
    
    # Location detection (basic pattern matching)
    location_match = re.search(r'(?:in|at|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', text)
    location = location_match.group(1) if location_match else "your area"
    
    if "tomorrow" in text_lower:
        return f"Tomorrow's forecast for {location} shows partly cloudy skies with temperatures ranging from 18°C to 25°C (64°F to 77°F). There's a 20% chance of light rain in the evening. Wind speed: 10-15 km/h."
    elif "week" in text_lower or "7 day" in text_lower or "next few days" in text_lower:
        return (f"This week's forecast for {location}:\n"
                "• Mon-Wed: Sunny, 20-26°C, Clear skies ☀️\n"
                "• Thu-Fri: Partly cloudy, 18-24°C, Light breeze 🌤️\n"
                "• Weekend: Chance of rain, 16-22°C, Bring an umbrella! 🌧️\n"
                "Perfect weather for outdoor activities early in the week!")
    elif "rain" in text_lower or "precipitation" in text_lower:
        return f"Currently there's no rain expected in {location}. The forecast shows clear skies with only a 10% chance of precipitation today. UV index: Moderate (5/10)."
    elif "hot" in text_lower or "cold" in text_lower or "temperature" in text_lower:
        return f"Current temperature in {location} is 22°C (72°F) with a comfortable humidity level of 55%. Feels like: 23°C (73°F). It feels pleasant with a light breeze from the northwest."
    elif "humidity" in text_lower:
        return f"Current humidity in {location} is 55% with a dew point of 13°C (55°F). Air quality: Good. Visibility: 10 km."
    elif "wind" in text_lower:
        return f"Current wind conditions in {location}: Wind speed 12 km/h (7 mph) from the northwest. Gusts up to 18 km/h. Ideal conditions for outdoor activities."
    else:
        return f"The weather in {location} is currently pleasant with partly cloudy skies and a moderate temperature of 22°C (72°F). Humidity: 55%, Wind: 12 km/h NW. It's a great day for outdoor activities! 🌤️"

def function3_time(text: str) -> str:
    """Function 3: Enhanced time and date information with calculations"""
    keywords = ["time", "date", "today", "now", "calendar", "day", "month", "year", "clock", "when", "timezone", "days from"]
    
    if not any(k in text.lower() for k in keywords):
        return None
    
    now = datetime.now()
    text_lower = text.lower()
    
    # Date calculations
    days_match = re.search(r'(\d+)\s+days?\s+(?:from|after)', text_lower)
    if days_match:
        days = int(days_match.group(1))
        future_date = now + timedelta(days=days)
        date_str = future_date.strftime("%A, %B %d, %Y")
        return f"**{days} days from now** will be: **{date_str}**"
    
    days_ago_match = re.search(r'(\d+)\s+days?\s+ago', text_lower)
    if days_ago_match:
        days = int(days_ago_match.group(1))
        past_date = now - timedelta(days=days)
        date_str = past_date.strftime("%A, %B %d, %Y")
        return f"**{days} days ago** was: **{date_str}**"
    
    # Timezone queries (basic simulation)
    timezone_match = re.search(r'(?:timezone|time\s+in|utc)\s*([+-]?\d+)', text_lower)
    if timezone_match:
        offset = int(timezone_match.group(1))
        tz_time = now + timedelta(hours=offset)
        time_str = tz_time.strftime("%I:%M:%S %p")
        return f"Time in UTC{offset:+d} is: **{time_str}**"
    
    # Specific queries
    if "day of week" in text_lower or "what day" in text_lower:
        return f"Today is **{now.strftime('%A')}**."
    elif "month" in text_lower and "day" not in text_lower:
        return f"The current month is **{now.strftime('%B %Y')}**."
    elif "year" in text_lower:
        return f"The current year is **{now.year}**."
    elif "week" in text_lower and "number" in text_lower:
        week_num = now.isocalendar()[1]
        return f"This is week **{week_num}** of {now.year}."
    elif "tomorrow" in text_lower:
        tomorrow = now + timedelta(days=1)
        date_str = tomorrow.strftime("%A, %B %d, %Y")
        return f"Tomorrow's date will be: **{date_str}**"
    elif "yesterday" in text_lower:
        yesterday = now - timedelta(days=1)
        date_str = yesterday.strftime("%A, %B %d, %Y")
        return f"Yesterday's date was: **{date_str}**"
    elif "time" in text_lower and "date" not in text_lower:
        time_str = now.strftime("%I:%M:%S %p")
        timezone_info = now.strftime("%Z") if now.strftime("%Z") else "Local Time"
        return f"The current time is **{time_str}** ({timezone_info})."
    elif "date" in text_lower and "time" not in text_lower:
        date_str = now.strftime("%A, %B %d, %Y")
        return f"Today's date is **{date_str}**."
    else:
        # Full date and time
        date_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%I:%M:%S %p")
        day_of_year = now.timetuple().tm_yday
        week_num = now.isocalendar()[1]
        return f"📅 **{date_str}**\n🕐 **{time_str}**\n📊 Day {day_of_year} of {now.year} | Week {week_num}"

def function4_greeting(text: str) -> str:
    """Function 4: Enhanced greetings with multilingual support"""
    text_lower = text.lower().strip()
    
    # Greeting patterns - English
    greetings = ["hi", "hello", "hey", "greetings", "howdy", "sup", "yo"]
    # Multilingual greetings
    multilingual_greetings = ["hola", "bonjour", "ciao", "hallo", "olá", "привет", "你好", "こんにちは", "안녕하세요"]
    time_greetings = ["good morning", "good afternoon", "good evening", "good night"]
    question_greetings = ["how are you", "how do you do", "how's it going", "what's up", "how are things"]
    
    # Get current hour for time-appropriate responses
    current_hour = datetime.now().hour
    
    # Check for multilingual greetings
    for greeting in multilingual_greetings:
        if greeting in text_lower:
            responses = {
                "hola": "¡Hola! 👋 Español detected! How can I assist you?",
                "bonjour": "Bonjour! 👋 Français detected! Comment puis-je vous aider?",
                "ciao": "Ciao! 👋 Italiano detected! Come posso aiutarti?",
                "hallo": "Hallo! 👋 Deutsch detected! Wie kann ich Ihnen helfen?",
                "olá": "Olá! 👋 Português detected! Como posso ajudá-lo?",
                "привет": "Привет! 👋 Русский detected! Как я могу помочь?",
                "你好": "你好！👋 中文 detected! How can I help you?",
                "こんにちは": "こんにちは！👋 日本語 detected! How can I help you?",
                "안녕하세요": "안녕하세요! 👋 한국어 detected! How can I help you?"
            }
            return responses.get(greeting, "Hello! 👋 How can I assist you today?")
    
    # Check for greetings
    if any(text_lower.startswith(g) for g in greetings) or text_lower in greetings:
        if current_hour < 12:
            return "Good morning! ☀️ I hope you're having a wonderful start to your day. How can I assist you?"
        elif current_hour < 17:
            return "Good afternoon! 🌤️ I hope your day is going well. How can I help you today?"
        elif current_hour < 21:
            return "Good evening! 🌆 I hope you've had a great day. What can I do for you?"
        else:
            return "Hello! 🌙 I hope you're having a pleasant evening. How may I assist you?"
    
    # Time-specific greetings
    elif any(g in text_lower for g in time_greetings):
        return "Thank you for the kind greeting! I hope you're having an excellent day. How can I help you with your inquiries?"
    
    # Question greetings
    elif any(q in text_lower for q in question_greetings):
        return "I'm functioning perfectly, thank you for asking! 😊 I'm here and ready to help you. What can I assist you with today?"
    
    # Farewell detection
    elif any(word in text_lower for word in ["bye", "goodbye", "see you", "farewell", "take care", "cya", "later"]):
        return "Goodbye! 👋 It was a pleasure assisting you. Have a wonderful day and feel free to return anytime!"
    
    # Thanks detection
    elif any(word in text_lower for word in ["thank", "thanks", "thx", "appreciate", "gracias", "merci", "danke"]):
        return "You're very welcome! 😊 I'm happy I could help. If you need anything else, don't hesitate to ask!"
    
    return None

def function6_unit_conversion(text: str) -> str:
    """Function 6: Advanced unit conversion"""
    keywords = ["convert", "to", "in", "km", "miles", "kg", "lbs", "celsius", "fahrenheit", "meters", "feet"]
    
    if not any(k in text.lower() for k in keywords):
        return None
    
    text_lower = text.lower()
    
    # Conversion patterns
    conversion_patterns = [
        # Distance conversions
        (r'(\d+\.?\d*)\s*(?:km|kilometers?)\s+(?:to|in)\s+(?:miles?|mi)', 
         lambda x: (float(x) * 0.621371, "km", "miles")),
        (r'(\d+\.?\d*)\s*(?:miles?|mi)\s+(?:to|in)\s+(?:km|kilometers?)', 
         lambda x: (float(x) * 1.60934, "miles", "km")),
        (r'(\d+\.?\d*)\s*(?:meters?|m)\s+(?:to|in)\s+(?:feet|ft)', 
         lambda x: (float(x) * 3.28084, "meters", "feet")),
        (r'(\d+\.?\d*)\s*(?:feet|ft)\s+(?:to|in)\s+(?:meters?|m)', 
         lambda x: (float(x) * 0.3048, "feet", "meters")),
        
        # Weight conversions
        (r'(\d+\.?\d*)\s*(?:kg|kilograms?)\s+(?:to|in)\s+(?:lbs?|pounds?)', 
         lambda x: (float(x) * 2.20462, "kg", "lbs")),
        (r'(\d+\.?\d*)\s*(?:lbs?|pounds?)\s+(?:to|in)\s+(?:kg|kilograms?)', 
         lambda x: (float(x) * 0.453592, "lbs", "kg")),
        
        # Temperature conversions
        (r'(\d+\.?\d*)\s*(?:c|celsius)\s+(?:to|in)\s+(?:f|fahrenheit)', 
         lambda x: (float(x) * 9/5 + 32, "°C", "°F")),
        (r'(\d+\.?\d*)\s*(?:f|fahrenheit)\s+(?:to|in)\s+(?:c|celsius)', 
         lambda x: ((float(x) - 32) * 5/9, "°F", "°C")),
    ]
    
    for pattern, converter in conversion_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                value = match.group(1)
                result, from_unit, to_unit = converter(value)
                
                # Format result
                if isinstance(result, float):
                    result = round(result, 2)
                
                return f"**{value} {from_unit}** is equal to **{result} {to_unit}**."
            except Exception:
                continue
    
    return None

def function7_language_detection(text: str) -> str:
    """Function 7: Simple language detection and information"""
    keywords = ["language", "detect", "what language", "translate"]
    
    if not any(k in text.lower() for k in keywords):
        return None
    
    # Simple pattern-based language detection
    language_patterns = {
        r'[\u4e00-\u9fff]+': 'Chinese (中文)',
        r'[\u0400-\u04ff]+': 'Russian (Русский)',
        r'[\u3040-\u309f\u30a0-\u30ff]+': 'Japanese (日本語)',
        r'[\uac00-\ud7af]+': 'Korean (한국어)',
        r'[\u0600-\u06ff]+': 'Arabic (العربية)',
        r'[\u0e00-\u0e7f]+': 'Thai (ไทย)',
    }
    
    detected_languages = []
    for pattern, language in language_patterns.items():
        if re.search(pattern, text):
            detected_languages.append(language)
    
    if detected_languages:
        langs = ", ".join(detected_languages)
        return f"I detected the following language(s) in your message: **{langs}**. 🌍\n\nNote: I'm a rule-based bot and can detect language patterns but cannot translate content."
    
    # If asking about language detection capability
    if "detect" in text.lower() or "what language" in text.lower():
        return ("I can detect various languages including:\n"
                "• Chinese (中文)\n"
                "• Russian (Русский)\n"
                "• Japanese (日本語)\n"
                "• Korean (한국어)\n"
                "• Arabic (العربية)\n"
                "• Thai (ไทย)\n"
                "• And more!\n\n"
                "Just send me text in any language and I'll try to identify it! 🌐")
    
    return None

def function5_fallback(text: str) -> str:
    """Function 5: Enhanced fallback with helpful guidance"""
    # Provide more context-aware fallback responses
    text_lower = text.lower()
    
    # Check for question patterns
    if any(q in text_lower for q in ["?", "what", "why", "how", "when", "where", "who", "which"]):
        return ("I appreciate your question! 🤔 While I'm a rule-based assistant with specific capabilities, I can help you with:\n\n"
                "• **Advanced Math** (e.g., 'sqrt(16)', 'sin(45)', 'log(100)')\n"
                "• **Unit Conversions** (e.g., '10 km to miles', '32 F to C')\n"
                "• **Weather information** (e.g., 'what's the weather?')\n"
                "• **Time and date** (e.g., 'what time is it?', '7 days from now')\n"
                "• **Language detection** (send text in any language)\n"
                "• **Greetings and pleasantries**\n\n"
                "Feel free to ask me about any of these topics!")
    
    # Check for help requests
    elif any(word in text_lower for word in ["help", "assist", "support", "guide"]):
        return ("I'm here to help! 💡 Here's what I can do for you:\n\n"
                "✓ Solve advanced math problems (including trig, logs, roots)\n"
                "✓ Convert units (distance, weight, temperature)\n"
                "✓ Provide weather updates with location detection\n"
                "✓ Tell you the current time and date (with timezone support)\n"
                "✓ Detect languages in your text\n"
                "✓ Have friendly multilingual conversations\n\n"
                "Just ask me anything related to these topics!")
    
    # Default fallback
    else:
        return ("Thank you for your message! I'm a specialized assistant focused on specific tasks. "
                "I can help with **advanced math**, **unit conversions**, **weather info**, **time/date queries**, **language detection**, and **friendly chat**. "
                "Try asking me something like 'sqrt(144)', '10 km to miles', or 'What time is it?' 😊")

# --- Gemini Function Calling Declarations ---

# Define function declarations for Gemini API function calling
function_declarations = [
    {
        "name": "calculate_math",
        "description": "Perform advanced mathematical calculations including basic operations, scientific functions like sqrt, sin, cos, tan, log, ln, exp, abs, and factorial. Supports expressions with parentheses and decimals.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate, e.g., 'sqrt(144)', 'sin(45)', '(5 + 5) * 2', 'log(100)'"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "convert_units",
        "description": "Convert between different units including distance (km/miles/meters/feet), weight (kg/lbs), and temperature (Celsius/Fahrenheit).",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "number",
                    "description": "The numeric value to convert"
                },
                "from_unit": {
                    "type": "string",
                    "description": "The unit to convert from, e.g., 'km', 'miles', 'kg', 'lbs', 'celsius', 'fahrenheit', 'meters', 'feet'"
                },
                "to_unit": {
                    "type": "string",
                    "description": "The unit to convert to"
                }
            },
            "required": ["value", "from_unit", "to_unit"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get weather information for a location. Can provide current weather, forecasts, temperature, humidity, wind conditions.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location to get weather for, defaults to 'your area' if not specified"
                },
                "query_type": {
                    "type": "string",
                    "enum": ["current", "tomorrow", "week", "rain", "temperature", "humidity", "wind"],
                    "description": "Type of weather information to retrieve"
                }
            },
            "required": ["query_type"]
        }
    },
    {
        "name": "get_time_date",
        "description": "Get current time, date, or perform date calculations. Can show current time/date, calculate future/past dates, convert timezones.",
        "parameters": {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "enum": ["current_time", "current_date", "full_datetime", "future_date", "past_date", "timezone", "day_of_week", "tomorrow", "yesterday"],
                    "description": "Type of time/date query"
                },
                "days_offset": {
                    "type": "integer",
                    "description": "Number of days to add or subtract (for future_date/past_date)"
                },
                "timezone_offset": {
                    "type": "integer",
                    "description": "Timezone offset in hours from UTC (for timezone queries)"
                }
            },
            "required": ["query_type"]
        }
    },
    {
        "name": "detect_language",
        "description": "Detect the language(s) present in text. Supports Chinese, Russian, Japanese, Korean, Arabic, Thai, and more.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to analyze for language detection"
                }
            },
            "required": ["text"]
        }
    }
]

# Function execution helpers
def execute_function_call(function_name: str, function_args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute function calls from Gemini and return structured results"""
    try:
        if function_name == "calculate_math":
            expression = function_args.get("expression", "")
            # Use existing function1_math logic
            result = function1_math(f"calculate {expression}")
            if result:
                return {"success": True, "result": result}
            return {"success": False, "error": "Could not evaluate expression"}
        
        elif function_name == "convert_units":
            value = function_args.get("value", 0)
            from_unit = function_args.get("from_unit", "")
            to_unit = function_args.get("to_unit", "")
            # Use existing function6_unit_conversion logic
            result = function6_unit_conversion(f"{value} {from_unit} to {to_unit}")
            if result:
                return {"success": True, "result": result}
            return {"success": False, "error": "Could not convert units"}
        
        elif function_name == "get_weather":
            location = function_args.get("location", "your area")
            query_type = function_args.get("query_type", "current")
            # Use existing function2_weather logic
            if query_type == "tomorrow":
                query = f"weather tomorrow in {location}"
            elif query_type == "week":
                query = f"weather this week in {location}"
            elif query_type == "rain":
                query = f"will it rain in {location}"
            elif query_type == "temperature":
                query = f"temperature in {location}"
            elif query_type == "humidity":
                query = f"humidity in {location}"
            elif query_type == "wind":
                query = f"wind in {location}"
            else:
                query = f"weather in {location}"
            
            result = function2_weather(query)
            if result:
                return {"success": True, "result": result}
            return {"success": False, "error": "Could not get weather info"}
        
        elif function_name == "get_time_date":
            query_type = function_args.get("query_type", "full_datetime")
            days_offset = function_args.get("days_offset")
            timezone_offset = function_args.get("timezone_offset")
            
            # Use existing function3_time logic
            if query_type == "current_time":
                query = "what time is it"
            elif query_type == "current_date":
                query = "what is the date"
            elif query_type == "tomorrow":
                query = "what is tomorrow's date"
            elif query_type == "yesterday":
                query = "what was yesterday's date"
            elif query_type == "day_of_week":
                query = "what day is it"
            elif query_type == "future_date" and days_offset:
                query = f"{days_offset} days from now"
            elif query_type == "past_date" and days_offset:
                query = f"{days_offset} days ago"
            elif query_type == "timezone" and timezone_offset is not None:
                query = f"time in UTC{timezone_offset:+d}"
            else:
                query = "what time and date is it"
            
            result = function3_time(query)
            if result:
                return {"success": True, "result": result}
            return {"success": False, "error": "Could not get time/date info"}
        
        elif function_name == "detect_language":
            text = function_args.get("text", "")
            # Use existing function7_language_detection logic
            result = function7_language_detection(f"detect language: {text}")
            if result:
                return {"success": True, "result": result}
            return {"success": False, "error": "Could not detect language"}
        
        else:
            return {"success": False, "error": f"Unknown function: {function_name}"}
    
    except Exception as e:
        return {"success": False, "error": f"Error executing {function_name}: {str(e)}"}

# --- Compatibility Layer ---

class MockResponse:
    def __init__(self, text: str):
        self.text = text

class ChatConversation:
    def __init__(self, use_function_calling: bool = None):
        """Initialize chat conversation with optional Gemini API function calling support
        
        Args:
            use_function_calling: If True, use Gemini API. If False, use rule-based.
                                If None (default), auto-detect based on API key availability.
        """
        self.history = []
        
        # Auto-detect if not specified
        if use_function_calling is None:
            use_function_calling = GEMINI_AVAILABLE and bool(GOOGLE_API_KEY)
        
        self.use_function_calling = use_function_calling
        self.gemini_chat = None
        self.model = None
        
        if self.use_function_calling:
            try:
                genai.configure(api_key=GOOGLE_API_KEY)
                
                # Initialize model with function declarations
                self.model = genai.GenerativeModel(
                    model_name='gemini-1.5-flash',
                    generation_config=generation_config,
                    safety_settings=safety_settings,
                    tools=[{"function_declarations": function_declarations}]
                )
                
                self.gemini_chat = self.model.start_chat(history=[])
                print("✓ Gemini API with function calling initialized")
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini API: {e}. Falling back to rule-based mode.")
                self.use_function_calling = False

    def send_message(self, text: str) -> MockResponse:
        """Send a message and get response, with optional Gemini function calling"""
        if self.use_function_calling and self.gemini_chat:
            return self._send_with_gemini(text)
        else:
            return self._send_with_rules(text)
    
    def _send_with_gemini(self, text: str) -> MockResponse:
        """Send message using Gemini API with function calling"""
        try:
            response = self.gemini_chat.send_message(text)
            
            # Check if Gemini wants to call functions
            function_calls = []
            for part in response.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_calls.append(part.function_call)
            
            # If function calls are present, execute them
            if function_calls:
                function_responses = []
                
                for function_call in function_calls:
                    function_name = function_call.name
                    function_args = dict(function_call.args)
                    
                    # Execute the function
                    result = execute_function_call(function_name, function_args)
                    
                    # Create function response for Gemini
                    function_responses.append(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response={"result": result}
                            )
                        )
                    )
                
                # Send function results back to Gemini to generate final response
                response = self.gemini_chat.send_message(function_responses)
            
            # Extract text from response
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Track history
            self.history.append({"role": "user", "parts": [{"text": text}]})
            self.history.append({"role": "model", "parts": [{"text": response_text}]})
            
            return MockResponse(response_text)
            
        except Exception as e:
            print(f"Error in Gemini API call: {e}. Falling back to rule-based mode.")
            # Fallback to rule-based on error
            return self._send_with_rules(text)
    
    def _send_with_rules(self, text: str) -> MockResponse:
        """Send message using rule-based functions (fallback)"""
        # Prioritized rule checking
        response = function0_help(text)
        if not response:
            response = function1_math(text)
        if not response:
            response = function6_unit_conversion(text)
        if not response:
            response = function2_weather(text)
        if not response:
            response = function3_time(text)
        if not response:
            response = function7_language_detection(text)
        if not response:
            response = function4_greeting(text)
        if not response:
            response = function5_fallback(text)
        
        # Track history for consistency with bot expectations (though no context is used)
        self.history.append({"role": "user", "parts": [{"text": text}]})
        self.history.append({"role": "model", "parts": [{"text": response}]})
        
        return MockResponse(response)

    @property
    def history_length(self):
        return len(self.history)

def generate_text_with_image(prompt: str, image_bytes: BytesIO) -> str:
    """Generate text with image using Gemini or fallback to rule-based"""
    if GEMINI_AVAILABLE and GOOGLE_API_KEY:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Open image from bytes
            from PIL import Image
            image = Image.open(image_bytes)
            
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            print(f"Error in Gemini image generation: {e}. Using fallback.")
    
    # Fallback: Simple rule-based response for images
    base_response = "I have received your image. "
    response = function0_help(prompt) or \
               function1_math(prompt) or \
               function6_unit_conversion(prompt) or \
               function2_weather(prompt) or \
               function3_time(prompt) or \
               function7_language_detection(prompt) or \
               function4_greeting(prompt) or \
               function5_fallback(prompt)
    return base_response + response

def list_models():
    """List available models"""
    if GEMINI_AVAILABLE and GOOGLE_API_KEY:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            models = genai.list_models()
            print("Available Gemini models:")
            for model in models:
                print(f"  - {model.name}")
                if hasattr(model, 'supported_generation_methods'):
                    print(f"    Methods: {', '.join(model.supported_generation_methods)}")
        except Exception as e:
            print(f"Error listing models: {e}")
    else:
        print("Gemini API not available. Using rule-based engine.")

# Provider replacement (if needed by other files)
class GeminiProvider:
    def start_chat(self, history=None):
        return ChatConversation()
    
    def generate_content(self, prompt: str) -> str:
        chat = ChatConversation()
        return chat.send_message(prompt).text
    
    def generate_content_with_image(self, prompt: str, image_bytes: BytesIO) -> str:
        return generate_text_with_image(prompt, image_bytes)
    
    def list_models(self):
        list_models()

# Global PROVIDER for handle.py compatibility
PROVIDER = GeminiProvider()

def get_provider():
    return PROVIDER
