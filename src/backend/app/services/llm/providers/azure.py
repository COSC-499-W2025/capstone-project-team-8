from openai import AzureOpenAI
from decouple import config
from .base import LLMProvider, DEFAULT_SYSTEM_MESSAGE


class AzureProvider(LLMProvider):
    """
    Azure OpenAI implementation for LLM requests.
    """

    def __init__(self):
        endpoint = config('AZURE_OPENAI_ENDPOINT')
        api_key = config('AZURE_OPENAI_API_KEY')
        api_version = config('AZURE_OPENAI_API_VERSION', default='2024-12-01-preview')
        
        self.client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=api_key
        )

    def analyze(self, prompt: str, system_message: str = None, model: str = None) -> str:
        if system_message is None:
            system_message = DEFAULT_SYSTEM_MESSAGE
            
        if model is None:
            model = config('AZURE_OPENAI_DEPLOYMENT', default='gpt-5-nano')
            
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        messages.append({"role": "user", "content": prompt})
            
        response = self.client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        return response.choices[0].message.content
