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
from .token_utils import TokenManager

class AntigravityChatSession:
    def __init__(self, provider, history=None):
        self.provider = provider
        self.history = history or []

    def send_message(self, prompt: str):
        # Add user message to history
        self.history.append({"role": "user", "parts": [{"text": prompt}]})
        
        # Generate response using the provider
        response_text = self.provider.generate_content_interaction(self.history)
        
        # Add model response to history
        self.history.append({"role": "model", "parts": [{"text": response_text}]})
        
        return MockResponse(response_text)

class AntigravityProvider(LLMProvider):
    # Vertex AI Configuration
    PROJECT_ID = "cloudaicompanion" 
    REGION = "us-central1"
    MODEL = "gemini-1.5-pro" # Can be updated to gemini-3-pro-preview if needed
    
    def __init__(self):
        self.api_key = ANTIGRAVITY_KEY # This is expected to be the REFRESH TOKEN
        # Construct Vertex AI Endpoint
        default_endpoint = f"https://{self.REGION}-aiplatform.googleapis.com/v1/projects/{self.PROJECT_ID}/locations/{self.REGION}/publishers/google/models/{self.MODEL}:generateContent"
        
        self.endpoint = ANTIGRAVITY_ENDPOINT or default_endpoint
        if ANTIGRAVITY_ENDPOINT:
            if "v1beta" in ANTIGRAVITY_ENDPOINT or "generativelanguage" in ANTIGRAVITY_ENDPOINT:
                print(f"WARNING: Configured ANTIGRAVITY_ENDPOINT '{ANTIGRAVITY_ENDPOINT}' appears to be invalid (v1beta/generativelanguage). Ignoring and using default Vertex AI endpoint.")
                self.endpoint = default_endpoint
                print(f"DEBUG: Using default Vertex AI Endpoint: {self.endpoint}")
            else:
                print(f"DEBUG: Using configured ANTIGRAVITY_ENDPOINT: {self.endpoint}")
        else:
            print(f"DEBUG: Using default Vertex AI Endpoint: {self.endpoint}")

        self.token_manager = TokenManager(self.api_key) if self.api_key else None

    def _call_api(self, payload):
        import requests
        
        if not self.token_manager:
            return "Error: Antigravity Provider requires ANTIGRAVITY_KEY (Refresh Token) to be set."

        try:
            token = self.token_manager.get_access_token()
        except Exception as e:
            return f"Authentication Error: {e}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=payload)
            
            if response.status_code != 200:
                return f"Antigravity API Error ({response.status_code}): {response.text}"
                
            data = response.json()
            
            # Parse response (Gemini structure)
            if "candidates" in data and len(data["candidates"]) > 0:
                parts = data["candidates"][0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            return "Empty response from Antigravity."
        except Exception as e:
            return f"{gemini_err_info}\nAntigravity API Exception: {e}"

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
        payload = {
            "contents": messages
        }
        return self._call_api(payload)

    def generate_content_with_image(self, prompt: str, image_bytes: BytesIO) -> str:
        import base64
        image_data = base64.b64encode(image_bytes.getvalue()).decode('utf-8')
        
        payload = {
            "contents": [{
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg", 
                            "data": image_data
                        }
                    }
                ]
            }]
        }
        return self._call_api(payload)

    def list_models(self):
        print(f"Antigravity (Vertex AI) Provider: Project={self.PROJECT_ID}, Model={self.MODEL}")


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
