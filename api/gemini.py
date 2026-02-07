import os
from io import BytesIO
from typing import Optional
from .config import new_chat_info, prompt_new_info, gemini_err_info, generation_config, safety_settings

# Try to import Hugging Face Transformers
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Configuration
HF_MODEL_NAME = "microsoft/DialoGPT-medium"  # Default conversational model
# Alternative models:
# - "facebook/blenderbot-400M-distill" (good for conversations)
# - "microsoft/DialoGPT-large" (larger, better quality)
# - "google/flan-t5-base" (instruction-following)

# Global model and tokenizer cache
_model_cache = {}
_tokenizer_cache = {}

# Fallback messages
AI_LOADING_MESSAGE = "🤖 AI model is loading for the first time, please wait..."
AI_NOT_AVAILABLE_MESSAGE = (
    "I'm a Telegram bot assistant. To use me effectively, please:\n\n"
    "• Use /help to see available commands\n"
    "• Try earthquake commands like /eq_latest or /eq_global\n"
    "• Check news with /news, /news_tech, or /news_taiwan\n"
    "• Get your info with /get_my_info\n\n"
    "Note: AI conversational features require transformers library to be installed."
)

IMAGE_NO_API_KEY_MESSAGE = "Image analysis requires specialized vision models. This feature is not available with the current Hugging Face setup."

# --- Compatibility Layer ---

class MockResponse:
    def __init__(self, text: str):
        self.text = text

def _get_or_load_model(model_name: str = HF_MODEL_NAME):
    """Load and cache Hugging Face model and tokenizer."""
    if model_name in _model_cache:
        return _model_cache[model_name], _tokenizer_cache[model_name]
    
    if not TRANSFORMERS_AVAILABLE:
        return None, None
    
    try:
        print(f"Loading Hugging Face model: {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
        
        # Set pad token if not exists
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load model with appropriate device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            low_cpu_mem_usage=True
        )
        model.to(device)
        model.eval()
        
        _model_cache[model_name] = model
        _tokenizer_cache[model_name] = tokenizer
        
        print(f"✓ Model loaded successfully on {device}")
        return model, tokenizer
    except Exception as e:
        print(f"Error loading model {model_name}: {e}")
        return None, None

class ChatConversation:
    def __init__(self):
        """Initialize chat conversation with Hugging Face Transformers.
        
        Uses local transformer models for conversational AI without requiring API keys.
        """
        self.history = []
        self.model, self.tokenizer = _get_or_load_model()
        self.use_transformers = self.model is not None and self.tokenizer is not None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_length = 1024  # Maximum response length
        
        if self.use_transformers:
            print("✓ Chat initialized with Hugging Face Transformers")
        else:
            print("Warning: Transformers not available. Bot will have limited conversational capabilities.")

    def send_message(self, text: str) -> MockResponse:
        """Send a message and get response using Hugging Face Transformers"""
        if self.use_transformers:
            return self._send_with_transformers(text)
        else:
            return self._send_fallback(text)
    
    def _send_with_transformers(self, text: str) -> MockResponse:
        """Send message using Hugging Face Transformers"""
        try:
            # Build conversation context from history
            conversation_context = ""
            for msg in self.history[-6:]:  # Keep last 3 exchanges (6 messages)
                role = msg.get("role", "user")
                content = msg.get("parts", [{}])[0].get("text", "")
                if role == "user":
                    conversation_context += f"User: {content}\n"
                else:
                    conversation_context += f"Bot: {content}\n"
            
            # Add current message
            conversation_context += f"User: {text}\nBot:"
            
            # Generate response
            inputs = self.tokenizer.encode(
                conversation_context,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Generate with sampling for more natural responses
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 150,  # Add tokens for response
                    num_return_sequences=1,
                    do_sample=True,
                    top_k=50,
                    top_p=0.95,
                    temperature=0.8,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the new response (after "Bot:")
            if "Bot:" in response_text:
                parts = response_text.split("Bot:")
                response_text = parts[-1].strip()
            
            # Clean up response
            response_text = response_text.split("User:")[0].strip()
            
            # If response is empty or too short, provide a default response
            if not response_text or len(response_text) < 3:
                response_text = "I understand. Could you please tell me more?"
            
            # Track history
            self.history.append({"role": "user", "parts": [{"text": text}]})
            self.history.append({"role": "model", "parts": [{"text": response_text}]})
            
            return MockResponse(response_text)
            
        except Exception as e:
            print(f"Error in Transformers generation: {e}")
            return self._send_fallback(text)
    
    def _send_fallback(self, text: str) -> MockResponse:
        """Fallback response when Transformers is not available"""
        # Track history for consistency
        self.history.append({"role": "user", "parts": [{"text": text}]})
        self.history.append({"role": "model", "parts": [{"text": AI_NOT_AVAILABLE_MESSAGE}]})
        
        return MockResponse(AI_NOT_AVAILABLE_MESSAGE)

    @property
    def history_length(self):
        return len(self.history)

def generate_text_with_image(prompt: str, image_bytes: BytesIO) -> str:
    """Generate text with image - not supported with basic Transformers setup"""
    # Image analysis with transformers requires specialized vision-language models
    # like BLIP, CLIP, or LLaVA which are much larger and more resource-intensive
    return IMAGE_NO_API_KEY_MESSAGE

def list_models():
    """List available models"""
    if TRANSFORMERS_AVAILABLE:
        print("Using Hugging Face Transformers with local models:")
        print(f"  - Default model: {HF_MODEL_NAME}")
        print("  - Alternative models you can configure:")
        print("    • microsoft/DialoGPT-large (better quality, larger)")
        print("    • facebook/blenderbot-400M-distill (conversation optimized)")
        print("    • google/flan-t5-base (instruction following)")
    else:
        print("Transformers library not available. Please install with: pip install transformers torch")

# Provider class for handle.py compatibility
class HybridProvider:
    """Provider supporting Hugging Face Transformers"""
    
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
