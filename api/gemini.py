import os
from io import BytesIO
from typing import Optional
from .config import new_chat_info, prompt_new_info, gemini_err_info, generation_config, safety_settings

# Try to import the Google Generative AI SDK
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Get API key from environment
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Configuration
GEMINI_MODEL_NAME = "gemini-1.5-flash"  # Default model

# --- Compatibility Layer ---

class MockResponse:
    def __init__(self, text: str):
        self.text = text

class ChatConversation:
    def __init__(self):
        """Initialize chat conversation with optional Gemini API support"""
        self.history = []
        self.use_gemini = GEMINI_AVAILABLE and bool(GOOGLE_API_KEY)
        self.gemini_chat = None
        self.model = None
        
        if self.use_gemini:
            try:
                genai.configure(api_key=GOOGLE_API_KEY)
                
                # Initialize model
                self.model = genai.GenerativeModel(
                    model_name=GEMINI_MODEL_NAME,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                
                self.gemini_chat = self.model.start_chat(history=[])
                print("✓ Gemini API initialized")
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini API: {e}. Bot will not have conversational capabilities.")
                self.use_gemini = False

    def send_message(self, text: str) -> MockResponse:
        """Send a message and get response using Gemini API"""
        if self.use_gemini and self.gemini_chat:
            return self._send_with_gemini(text)
        else:
            return self._send_fallback(text)
    
    def _send_with_gemini(self, text: str) -> MockResponse:
        """Send message using Gemini API"""
        try:
            response = self.gemini_chat.send_message(text)
            
            # Extract text from response
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Track history
            self.history.append({"role": "user", "parts": [{"text": text}]})
            self.history.append({"role": "model", "parts": [{"text": response_text}]})
            
            return MockResponse(response_text)
            
        except Exception as e:
            print(f"Error in Gemini API call: {e}")
            return self._send_fallback(text)
    
    def _send_fallback(self, text: str) -> MockResponse:
        """Fallback response when Gemini API is not available"""
        response = (
            "I'm a Telegram bot assistant. To use me effectively, please:\n\n"
            "• Use /help to see available commands\n"
            "• Try earthquake commands like /eq_latest or /eq_global\n"
            "• Check news with /news, /news_tech, or /news_taiwan\n"
            "• Get your info with /get_my_info\n\n"
            "Note: Conversational AI features require GOOGLE_API_KEY to be configured."
        )
        
        # Track history for consistency
        self.history.append({"role": "user", "parts": [{"text": text}]})
        self.history.append({"role": "model", "parts": [{"text": response}]})
        
        return MockResponse(response)

    @property
    def history_length(self):
        return len(self.history)

def generate_text_with_image(prompt: str, image_bytes: BytesIO) -> str:
    """Generate text with image using Gemini"""
    if GEMINI_AVAILABLE and GOOGLE_API_KEY:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            
            # Open image from bytes
            from PIL import Image
            image = Image.open(image_bytes)
            
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            print(f"Error in Gemini image generation: {e}.")
            return f"Sorry, I couldn't process this image. Error: {str(e)}"
    
    # Fallback when Gemini is not available
    return "Image analysis is not available. Please configure GOOGLE_API_KEY to enable this feature."

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
        print("Gemini API not available. Please configure GOOGLE_API_KEY.")

# Provider class for handle.py compatibility
class HybridProvider:
    """Provider supporting Gemini AI"""
    
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
