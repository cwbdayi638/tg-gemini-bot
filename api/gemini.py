from io import BytesIO
import abc
import google.generativeai as genai
import PIL.Image

from .config import GOOGLE_API_KEY, generation_config, safety_settings, gemini_err_info, new_chat_info, LLM_PROVIDER, ANTIGRAVITY_KEY, ANTIGRAVITY_ENDPOINT

# Abstract Base Class for LLM Providers
class LLMProvider(abc.ABC):
    @abc.abstractmethod
    def start_chat(self, history=None):
        pass
    
    @abc.abstractmethod
    def generate_content(self, prompt: str) -> str:
        pass

    @abc.abstractmethod
    def generate_content_with_image(self, prompt: str, image_bytes: BytesIO) -> str:
        pass
    
    @abc.abstractmethod
    def list_models(self):
        pass

# Google Gemini Provider Implementation
class GoogleGeminiProvider(LLMProvider):
    def __init__(self):
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY[0])
        self.model_usual = genai.GenerativeModel(
            model_name="gemini-3-pro-preview",
            generation_config=generation_config,
            safety_settings=safety_settings)
        self.model_vision = genai.GenerativeModel(
            model_name="gemini-3-pro-preview",
            generation_config=generation_config,
            safety_settings=safety_settings)

    def start_chat(self, history=None):
        if history is None:
            history = []
        return self.model_usual.start_chat(history=history)

    def generate_content(self, prompt: str) -> str:
        try:
            response = self.model_usual.generate_content(prompt)
            result = response.text
        except Exception as e:
            result = f"{gemini_err_info}\n{repr(e)}"
        return result

    def generate_content_with_image(self, prompt: str, image_bytes: BytesIO) -> str:
        img = PIL.Image.open(image_bytes)
        try:
            response = self.model_vision.generate_content([prompt, img])
            result = response.text
        except Exception as e:
            result = f"{gemini_err_info}\n{repr(e)}"
        return result

    def list_models(self):
        for m in genai.list_models():
            print(m)
            if "generateContent" in m.supported_generation_methods:
                print(m.name)

# Antigravity Provider Implementation (Placeholder)
# Antigravity Provider Implementation
class AntigravityChatSession:
    def __init__(self, provider, history=None):
        self.provider = provider
        self.history = history or []

    def send_message(self, prompt: str):
        # Add user message to history
        self.history.append({"role": "user", "parts": [{"text": prompt}]})
        
        # Generate response using the provider, passing the full history
        # Note: The actual API call in generate_content might need to be adjusted 
        # to accept history if we want multi-turn chat. 
        # For now, we'll implement a simple one-shot or pass context if supported.
        # Assuming generate_content can take a list of messages or we construct the prompt.
        # But LLMProvider.generate_content takes `prompt: str`.
        # We might need a specific method for chat or format the prompt.
        
        # Better approach: AntigravityProvider.generate_content calls the API.
        # For chat, we simply pass the full history to the API if it supports it.
        # However, to keep it simple and consistent with the interface:
        
        response_text = self.provider.generate_content_interaction(self.history)
        
        # Add model response to history
        self.history.append({"role": "model", "parts": [{"text": response_text}]})
        
        return MockResponse(response_text)

class AntigravityProvider(LLMProvider):
    # Constants from OpenClaw (Antigravity) reference
    CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
    CLIENT_SECRET = "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" # Decoded from reference
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    # Default endpoint from reference (Cloud Code Assist)
    DEFAULT_ENDPOINT = "https://cloudcode-pa.googleapis.com/v1internal:loadCodeAssist" 
    # Actually, the generating endpoint in reference for Gemini seems to be standard or via cloudcode-pa
    # Reference: src/media-understanding/providers/google/video.ts -> `${baseUrl}/models/${model}:generateContent`
    # We will use the configured ANTIGRAVITY_ENDPOINT or a safe default compatible with Gemini API
    
    def __init__(self):
        self.api_key = ANTIGRAVITY_KEY # This is expected to be the REFRESH TOKEN
        self.endpoint = ANTIGRAVITY_ENDPOINT or "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
        self.access_token = None
        self.token_expiry = 0

    def _get_access_token(self):
        import time
        import requests
        
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token

        if not self.api_key:
             return None # Can't refresh without a refresh token

        try:
            response = requests.post(self.TOKEN_URL, data={
                "client_id": self.CLIENT_ID,
                "client_secret": self.CLIENT_SECRET,
                "refresh_token": self.api_key,
                "grant_type": "refresh_token"
            })
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.token_expiry = time.time() + data.get("expires_in", 3600) - 60 # Buffer
            return self.access_token
        except Exception as e:
            print(f"Error refreshing Antigravity token: {e}")
            return None

    def _call_api(self, payload):
        import requests
        token = self._get_access_token()
        if not token:
            return "Error: Could not authenticate with Antigravity (Missing or Invalid Refresh Token)."
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            # We assume the endpoint expects a Gemini-like payload: { "contents": [...] }
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Parse response (Gemini structure)
            if "candidates" in data and len(data["candidates"]) > 0:
                parts = data["candidates"][0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            return "Empty response from Antigravity."
        except Exception as e:
            return f"{gemini_err_info}\nAntigravity API Error: {e}"

    def start_chat(self, history=None):
        return AntigravityChatSession(self, history)

    def generate_content(self, prompt: str) -> str:
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }]
        }
        return self._call_api(payload)
    
    def generate_content_interaction(self, messages: list) -> str:
        # Helper for chat session to send full history
        # messages are expected to be in Gemini format: {"role": "...", "parts": [...]}
        payload = {
            "contents": messages
        }
        return self._call_api(payload)

    def generate_content_with_image(self, prompt: str, image_bytes: BytesIO) -> str:
        import base64
        # Convert image to base64
        image_data = base64.b64encode(image_bytes.getvalue()).decode('utf-8')
        
        payload = {
            "contents": [{
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg", # Assuming JPEG or matching byte stream
                            "data": image_data
                        }
                    }
                ]
            }]
        }
        return self._call_api(payload)

    def list_models(self):
        print("Antigravity Models: (Managed via Endpoint Configuration)")


class MockChatSession:
    # Kept for fallback or other providers if needed
    def __init__(self, provider, history=None):
        self.provider = provider
        self.history = history or []

    def send_message(self, prompt):
        self.history.append({"role": "user", "parts": [prompt]})
        response = self.provider.generate_content(prompt)
        self.history.append({"role": "model", "parts": [response]})
        return MockResponse(response)

class MockResponse:
    def __init__(self, text):
        self.text = text


# Factory to get the configured provider
def get_provider() -> LLMProvider:
    if LLM_PROVIDER == 'antigravity':
        return AntigravityProvider()
    return GoogleGeminiProvider()

# Initialize the global provider
PROVIDER = get_provider()

# Expose functions to maintain compatibility with existing calls, but route them to the provider
def list_models() -> None:
    """list all models"""
    PROVIDER.list_models()

""" This function is deprecated """
def generate_content(prompt: str) -> str:
    """generate text from prompt"""
    return PROVIDER.generate_content(prompt)

def generate_text_with_image(prompt: str, image_bytes: BytesIO) -> str:
    """generate text from prompt and image"""
    return PROVIDER.generate_content_with_image(prompt, image_bytes)


class ChatConversation:
    """
    Kicks off an ongoing chat. If the input is /new,
    it triggers the start of a fresh conversation.
    """

    def __init__(self) -> None:
        self.chat = PROVIDER.start_chat(history=[])

    def send_message(self, prompt: str) -> str:
        """send message"""
        if prompt.startswith("/new"):
            self.__init__()
            result = new_chat_info
        else:
            try:
                # Assuming the chat object returned by start_chat has a send_message method
                # that returns an object with a .text attribute (like Gemini's)
                response = self.chat.send_message(prompt)
                result = response.text
            except Exception as e:
                result = f"{gemini_err_info}\n{repr(e)}"
        return result

    @property
    def history(self):
        return self.chat.history

    @property
    def history_length(self):
        return len(self.chat.history)


if __name__ == "__main__":
    print(list_models())
