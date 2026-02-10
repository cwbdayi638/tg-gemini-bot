import os
from io import BytesIO
from typing import Optional
from .config import new_chat_info, prompt_new_info, gemini_err_info, generation_config, safety_settings

# Fallback messages
AI_NOT_AVAILABLE_MESSAGE = (
    "我是 Telegram 機器人助手。請使用以下方式使用我：\n\n"
    "• 直接對我說話，我會用 AI 回答您的問題\n"
    "• 使用 /help 查看可用指令\n"
    "• 嘗試地震指令，如 /eq_latest 或 /eq_global\n"
    "• 使用 /search <關鍵字> 進行網頁搜尋\n"
    "• 使用 /ai <問題> 或直接發送訊息進行 AI 問答\n"
    "• 使用 /get_my_info 取得您的資訊"
)

IMAGE_NO_API_KEY_MESSAGE = "圖片分析功能目前無法使用。"

# --- Compatibility Layer ---

class MockResponse:
    def __init__(self, text: str):
        self.text = text

class ChatConversation:
    def __init__(self):
        """Initialize chat conversation with Ollama AI support."""
        self.history = []
        print("已使用 Ollama AI 初始化聊天。")

    def send_message(self, text: str) -> MockResponse:
        """Send a message and get an AI response from Ollama"""
        # Track history for consistency
        self.history.append({"role": "user", "parts": [{"text": text}]})
        
        # Try to use Ollama AI service for generating response
        try:
            from .ai_service import generate_ai_text
            response_text = generate_ai_text(text)
        except Exception as e:
            print(f"Error calling Ollama AI: {e}")
            response_text = AI_NOT_AVAILABLE_MESSAGE
        
        self.history.append({"role": "model", "parts": [{"text": response_text}]})
        
        return MockResponse(response_text)

    @property
    def history_length(self):
        return len(self.history)

def generate_text_with_image(prompt: str, image_bytes: BytesIO) -> str:
    """Generate text with image - not currently supported"""
    return IMAGE_NO_API_KEY_MESSAGE

def list_models():
    """List available models"""
    print("目前未設定 AI 模型。")

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
