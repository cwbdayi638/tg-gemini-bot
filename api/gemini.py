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
class AntigravityProvider(LLMProvider):
    def __init__(self):
        # TODO: Initialize Antigravity client here using ANTIGRAVITY_KEY and ANTIGRAVITY_ENDPOINT
        self.api_key = ANTIGRAVITY_KEY
        self.endpoint = ANTIGRAVITY_ENDPOINT
        # self.client = ...
    
    def start_chat(self, history=None):
        # TODO: Return an object that has send_message(prompt) and history property
        # For now, returning a mock chat object
        return MockChatSession(self)

    def generate_content(self, prompt: str) -> str:
        # TODO: Implement actual API call
        return f"[Antigravity] Received: {prompt}. (This is a placeholder response. Please implement API logic.)"

    def generate_content_with_image(self, prompt: str, image_bytes: BytesIO) -> str:
        # TODO: Implement image processing
        return f"[Antigravity] Received image with prompt: {prompt}. (Placeholder)"

    def list_models(self):
        print("Antigravity Models: (Placeholder)")


class MockChatSession:
    def __init__(self, provider, history=None):
        self.provider = provider
        self.history = history or []

    def send_message(self, prompt):
        # Simulate storing history
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
