from google import genai
from google.genai import types
from decouple import config
from .base import LLMProvider, DEFAULT_SYSTEM_MESSAGE


class GeminiProvider(LLMProvider):
    """
    Google Gemini implementation for LLM requests.
    Uses the new google-genai SDK.
    """

    def __init__(self):
        api_key = config('GEMINI_API_KEY')
        self.client = genai.Client(api_key=api_key)

    def analyze(self, prompt: str, system_message: str = None, model: str = None) -> str:
        if system_message is None:
            system_message = DEFAULT_SYSTEM_MESSAGE
            
        if model is None:
            model = config('GEMINI_MODEL', default='gemini-2.5-flash')
            
        # Initialize the generation config to include system instructions
        gemini_config = types.GenerateContentConfig()
        if system_message:
            gemini_config.system_instruction = system_message
            
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=gemini_config
        )
        
        return response.text
