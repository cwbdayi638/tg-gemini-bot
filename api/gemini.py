import re
from datetime import datetime
from io import BytesIO
from .config import new_chat_info, prompt_new_info, gemini_err_info

# --- Rule Functions ---

def function0_help(text: str) -> str:
    """Function 0: Overall help and capability overview"""
    keywords = ["help", "guide", "menu", "capabilities", "what can you do", "/help", "instruction"]
    if any(k in text.lower() for k in keywords):
        return (
            "🤖 **Rule-Based Bot Capabilities**\n\n"
            "I'm a fast, rule-based assistant! Here's what I can do:\n\n"
            "1️⃣ **Advanced Math**: Just send an expression like `(5 + 5) * 2` or `2^10`.\n"
            "2️⃣ **Weather**: Ask `What's the weather?` or `Forecast for tomorrow`.\n"
            "3️⃣ **Time & Date**: Ask `What time is it?` or `What's today's date?`.\n"
            "4️⃣ **Friendly Chat**: Say `Hi`, `How are you?`, or `Thank you`.\n\n"
            "💡 *Tip: I'm very fast because I don't use a large language model!*"
        )
    return None

def function1_math(text: str) -> str:
    """Function 1: Advanced math calculations"""
    # Look for math keywords or expressions
    math_keywords = ["calculate", "compute", "what is", "what's", "solve", "=", "+", "-", "*", "/", "^", "**"]
    
    # Check if text contains math-related content
    if not any(keyword in text.lower() for keyword in math_keywords):
        # Also check for digit patterns
        if not re.search(r'\d', text):
            return None
    
    # Extract mathematical expression - support parentheses, decimals, and exponents
    # Pattern matches: numbers (int/float), operators (+,-,*,/,**,^,%), and parentheses
    pattern = r"([\d\.\s\+\-\*\/\%\(\)\^]+)"
    matches = re.findall(pattern, text)
    
    for expression in matches:
        # Clean up the expression
        expression = expression.strip()
        
        # Skip if too short or just whitespace
        if len(expression) < 3 or expression.isspace():
            continue
            
        # Replace ^ with ** for Python exponentiation
        expression = expression.replace('^', '**')
        
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
    """Function 2: Enhanced weather information"""
    keywords = ["weather", "temperature", "forecast", "rain", "sunny", "cloudy", "climate", "hot", "cold", "warm"]
    
    if not any(k in text.lower() for k in keywords):
        return None
    
    # Check for specific weather queries
    text_lower = text.lower()
    
    if "tomorrow" in text_lower:
        return "Tomorrow's forecast shows partly cloudy skies with temperatures ranging from 18°C to 25°C (64°F to 77°F). There's a 20% chance of light rain in the evening."
    elif "week" in text_lower or "7 day" in text_lower:
        return "This week's forecast:\n• Mon-Wed: Sunny, 20-26°C\n• Thu-Fri: Partly cloudy, 18-24°C\n• Weekend: Chance of rain, 16-22°C\nPerfect weather for outdoor activities early in the week!"
    elif "rain" in text_lower:
        return "Currently there's no rain expected. The forecast shows clear skies with only a 10% chance of precipitation today."
    elif "hot" in text_lower or "cold" in text_lower or "temperature" in text_lower:
        return "Current temperature is 22°C (72°F) with a comfortable humidity level of 55%. It feels pleasant with a light breeze."
    else:
        return "The weather is currently pleasant with partly cloudy skies and a moderate temperature of 22°C (72°F). It's a great day for outdoor activities! 🌤️"

def function3_time(text: str) -> str:
    """Function 3: Enhanced time and date information"""
    keywords = ["time", "date", "today", "now", "calendar", "day", "month", "year", "clock", "when"]
    
    if not any(k in text.lower() for k in keywords):
        return None
    
    now = datetime.now()
    text_lower = text.lower()
    
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
    elif "time" in text_lower and "date" not in text_lower:
        time_str = now.strftime("%I:%M:%S %p")
        return f"The current time is **{time_str}**."
    elif "date" in text_lower and "time" not in text_lower:
        date_str = now.strftime("%A, %B %d, %Y")
        return f"Today's date is **{date_str}**."
    else:
        # Full date and time
        date_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%I:%M:%S %p")
        day_of_year = now.timetuple().tm_yday
        return f"📅 **{date_str}**\n🕐 **{time_str}**\n(Day {day_of_year} of {now.year})"

def function4_greeting(text: str) -> str:
    """Function 4: Enhanced greetings with context awareness"""
    text_lower = text.lower().strip()
    
    # Greeting patterns
    greetings = ["hi", "hello", "hey", "greetings", "howdy", "sup", "yo"]
    time_greetings = ["good morning", "good afternoon", "good evening", "good night"]
    question_greetings = ["how are you", "how do you do", "how's it going", "what's up", "how are things"]
    
    # Get current hour for time-appropriate responses
    current_hour = datetime.now().hour
    
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
    elif any(word in text_lower for word in ["bye", "goodbye", "see you", "farewell", "take care"]):
        return "Goodbye! 👋 It was a pleasure assisting you. Have a wonderful day and feel free to return anytime!"
    
    # Thanks detection
    elif any(word in text_lower for word in ["thank", "thanks", "thx", "appreciate"]):
        return "You're very welcome! 😊 I'm happy I could help. If you need anything else, don't hesitate to ask!"
    
    return None

def function5_fallback(text: str) -> str:
    """Function 5: Enhanced fallback with helpful guidance"""
    # Provide more context-aware fallback responses
    text_lower = text.lower()
    
    # Check for question patterns
    if any(q in text_lower for q in ["?", "what", "why", "how", "when", "where", "who", "which"]):
        return ("I appreciate your question! 🤔 While I'm a rule-based assistant with specific capabilities, I can help you with:\n\n"
                "• **Math calculations** (e.g., '123 + 456' or 'calculate 5 * 8')\n"
                "• **Weather information** (e.g., 'what's the weather?')\n"
                "• **Time and date** (e.g., 'what time is it?')\n"
                "• **Greetings and pleasantries**\n\n"
                "Feel free to ask me about any of these topics!")
    
    # Check for help requests
    elif any(word in text_lower for word in ["help", "assist", "support", "guide"]):
        return ("I'm here to help! 💡 Here's what I can do for you:\n\n"
                "✓ Solve math problems\n"
                "✓ Provide weather updates\n"
                "✓ Tell you the current time and date\n"
                "✓ Have friendly conversations\n\n"
                "Just ask me anything related to these topics!")
    
    # Default fallback
    else:
        return ("Thank you for your message! I'm a specialized assistant focused on specific tasks. "
                "I can help with **math calculations**, **weather info**, **time/date queries**, and **friendly chat**. "
                "Try asking me something like 'What's 25 * 4?' or 'What time is it?' 😊")

# --- Compatibility Layer ---

class MockResponse:
    def __init__(self, text: str):
        self.text = text

class ChatConversation:
    def __init__(self):
        self.history = []

    def send_message(self, text: str) -> MockResponse:
        # Prioritized rule checking
        response = function0_help(text)
        if not response:
            response = function1_math(text)
        if not response:
            response = function2_weather(text)
        if not response:
            response = function3_time(text)
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
    """Compatibility function for image messages"""
    # Simple rule-based response for images
    base_response = "I have received your image. "
    response = function0_help(prompt) or \
               function1_math(prompt) or \
               function2_weather(prompt) or \
               function3_time(prompt) or \
               function4_greeting(prompt) or \
               function5_fallback(prompt)
    return base_response + response

def list_models():
    """Compatibility function for listing models"""
    print("Listing models: [Rule-Based Engine Active]")

# Provider replacement (if needed by other files)
class RuleBasedProvider:
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
PROVIDER = RuleBasedProvider()

def get_provider():
    return PROVIDER
