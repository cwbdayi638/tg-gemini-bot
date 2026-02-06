import re
from datetime import datetime
from io import BytesIO
from .config import new_chat_info, prompt_new_info, gemini_err_info

# --- Rule Functions ---

def function1_math(text: str) -> str:
    """Function 1: Simple math calculations"""
    # Look for expressions like 123 + 456
    pattern = r"(\d+\s*[\+\-\*\/\%]\s*\d+)"
    match = re.search(pattern, text)
    if match:
        try:
            expression = match.group(1)
            # Safe evaluation for basic math
            # We strictly limit characters to digits and basic operators
            if all(c in "0123456789+-*/% " for c in expression):
                # Using a simple eval for 2-operand math
                result = eval(expression)
                return f"The result of {expression} is {result}."
        except Exception:
            pass
    return None

def function2_weather(text: str) -> str:
    """Function 2: The weather condition"""
    keywords = ["weather", "temperature", "forecast", "rain", "sunny", "cloudy"]
    if any(k in text.lower() for k in keywords):
        return "The weather condition is currently pleasant with a moderate temperature. It's a great day for outdoor activities!"
    return None

def function3_time(text: str) -> str:
    """Function 3: Current time and date"""
    keywords = ["time", "date", "today", "now", "calendar"]
    if any(k in text.lower() for k in keywords):
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%I:%M %p")
        return f"Current date is {date_str} and the time is {time_str}."
    return None

def function4_greeting(text: str) -> str:
    """Function 4: Greeting with manner"""
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "how are you"]
    if any(text.lower().startswith(g) for g in greetings) or text.lower().strip() in greetings:
        return "Greetings! I hope you are having a wonderful day. How can I assist you with your inquiries?"
    return None

def function5_fallback(text: str) -> str:
    """Function 5: Anything else"""
    return "Thank you for your question. I will search the answer ....."

# --- Compatibility Layer ---

class MockResponse:
    def __init__(self, text: str):
        self.text = text

class ChatConversation:
    def __init__(self):
        self.history = []

    def send_message(self, text: str) -> MockResponse:
        # Prioritized rule checking
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
    response = function1_math(prompt) or function2_weather(prompt) or \
               function3_time(prompt) or function4_greeting(prompt) or \
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
