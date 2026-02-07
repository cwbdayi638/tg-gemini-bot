import os
from io import BytesIO
from typing import Optional
from .config import new_chat_info, prompt_new_info, gemini_err_info, generation_config, safety_settings

# Fallback messages
AI_NOT_AVAILABLE_MESSAGE = (
    "I'm a Telegram bot assistant. To use me effectively, please:\n\n"
    "• Use /help to see available commands\n"
    "• Try earthquake commands like /eq_latest or /eq_global\n"
    "• Use web search with /search <query>\n"
    "• Get your info with /get_my_info\n\n"
    "Note: AI conversational features are not available."
)

IMAGE_NO_API_KEY_MESSAGE = "Image analysis feature is not currently available."

# --- Compatibility Layer ---

class MockResponse:
    def __init__(self, text: str):
        self.text = text

class ChatConversation:
    def __init__(self):
        """Initialize chat conversation with a basic response system."""
        self.history = []
        print("Chat initialized with a basic response system.")

    def send_message(self, text: str) -> MockResponse:
        """Send a message and get a fallback response"""
        # Track history for consistency
        self.history.append({"role": "user", "parts": [{"text": text}]})
        self.history.append({"role": "model", "parts": [{"text": AI_NOT_AVAILABLE_MESSAGE}]})
        
        return MockResponse(AI_NOT_AVAILABLE_MESSAGE)

    @property
    def history_length(self):
        return len(self.history)

def generate_text_with_image(prompt: str, image_bytes: BytesIO) -> str:
    """Generate text with image - not currently supported"""
    return IMAGE_NO_API_KEY_MESSAGE

def list_models():
    """List available models"""
    print("No AI models currently configured.")

# Provider class for handle.py compatibility
class HybridProvider:
    """Simple provider for basic bot functionality"""
    
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
PROVIDER = HybridProvider()

def get_provider():
    return PROVIDER
