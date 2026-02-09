"""
OpenAI service for Telegram bot.
Provides AI-powered conversation capabilities using OpenAI API.
"""
import os
from typing import Dict, List, Optional

from .config import OPENAI_KEY
from .printLog import send_log

# Try to import OpenAI and httpx
try:
    from openai import OpenAI
    import httpx
    OPENAI_AVAILABLE = bool(OPENAI_KEY)
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not available. Install with: pip install openai")


class OpenAIService:
    """Service for managing OpenAI API interactions."""
    
    def __init__(self):
        self.client: Optional[OpenAI] = None
        self.sessions: Dict[str, List[Dict]] = {}  # Store conversation history by chat_id
        self._initialized = False
    
    def initialize(self):
        """
        Initialize the OpenAI client.
        
        Proxy configuration:
        - Set HTTP_PROXY and/or HTTPS_PROXY environment variables
        - The httpx library (used by OpenAI SDK v1.0+) will automatically use them
        - Do NOT pass 'proxies' parameter directly to OpenAI() - it's not supported
        """
        if not OPENAI_KEY:
            raise RuntimeError("OPENAI_KEY environment variable is not set")
        
        if self._initialized:
            return
        
        try:
            # Initialize OpenAI client
            # Note: httpx (underlying HTTP client) automatically respects 
            # HTTP_PROXY and HTTPS_PROXY environment variables
            self.client = OpenAI(api_key=OPENAI_KEY)
            self._initialized = True
            
            # Log proxy configuration if present
            proxy_info = []
            if os.environ.get('HTTP_PROXY'):
                proxy_info.append(f"HTTP_PROXY={os.environ.get('HTTP_PROXY')}")
            if os.environ.get('HTTPS_PROXY'):
                proxy_info.append(f"HTTPS_PROXY={os.environ.get('HTTPS_PROXY')}")
            
            if proxy_info:
                send_log(f"✅ OpenAI client initialized with proxy: {', '.join(proxy_info)}")
            else:
                send_log("✅ OpenAI client initialized successfully")
        except Exception as e:
            send_log(f"❌ Failed to initialize OpenAI client: {e}")
            raise
    
    def get_or_create_session(self, chat_id: str) -> List[Dict]:
        """Get or create a conversation history for a chat."""
        if not self._initialized:
            self.initialize()
        
        if chat_id not in self.sessions:
            self.sessions[chat_id] = []
        
        return self.sessions[chat_id]
    
    def chat(self, chat_id: str, prompt: str, model: str = "gpt-4o") -> str:
        """
        Send a prompt to OpenAI and get the response.
        
        Args:
            chat_id: Unique identifier for the chat session
            prompt: User's message/question
            model: Model to use (default: gpt-4o)
        
        Returns:
            AI response text
        """
        try:
            if not self._initialized:
                self.initialize()
            
            # Get conversation history
            history = self.get_or_create_session(chat_id)
            
            # Add user message to history
            history.append({"role": "user", "content": prompt})
            
            # Prepare messages for API call (include system message)
            messages = [
                {"role": "system", "content": "You are a helpful assistant."}
            ] + history
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1024
            )
            
            # Extract response text
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to history
            history.append({"role": "assistant", "content": assistant_message})
            
            # Keep history manageable (last 20 messages)
            if len(history) > 20:
                self.sessions[chat_id] = history[-20:]
            
            return assistant_message
            
        except Exception as e:
            send_log(f"❌ OpenAI chat error: {e}")
            # Remove the failed user message from history (verify it's a user message)
            if chat_id in self.sessions and self.sessions[chat_id]:
                last_msg = self.sessions[chat_id][-1]
                if last_msg.get("role") == "user":
                    self.sessions[chat_id].pop()
            return f"❌ Error communicating with OpenAI: {str(e)}"
    
    def clear_session(self, chat_id: str) -> bool:
        """Clear/delete a session for a specific chat."""
        if chat_id in self.sessions:
            del self.sessions[chat_id]
            return True
        return False


# Global service instance
_openai_service = None


def get_openai_service() -> OpenAIService:
    """Get the global OpenAI service instance."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service


def openai_chat_sync(chat_id: str, prompt: str, model: str = "gpt-4o") -> str:
    """
    Synchronous wrapper for OpenAI chat.
    """
    if not OPENAI_AVAILABLE:
        return "❌ OpenAI is not available. Please ensure OPENAI_KEY is set and openai package is installed."
    
    try:
        service = get_openai_service()
        return service.chat(chat_id, prompt, model)
    except Exception as e:
        send_log(f"❌ OpenAI sync chat error: {e}")
        return f"❌ Error: {str(e)}"


def clear_openai_session_sync(chat_id: str) -> bool:
    """Synchronous wrapper for clearing an OpenAI session."""
    if not OPENAI_AVAILABLE:
        return False
    
    try:
        service = get_openai_service()
        return service.clear_session(chat_id)
    except Exception as e:
        send_log(f"❌ Error clearing OpenAI session: {e}")
        return False
