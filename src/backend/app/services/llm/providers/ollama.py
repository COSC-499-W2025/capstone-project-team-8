import requests
from decouple import config
from .base import LLMProvider, DEFAULT_SYSTEM_MESSAGE


class OllamaProvider(LLMProvider):
    """
    Ollama backend implementation for LLM requests.
    This routes requests to the local Express `llm-service`.
    """

    def __init__(self):
        # Default to the express service running on port 3001
        self.endpoint = config('OLLAMA_SERVICE_URL', default='http://localhost:3001/api/query')
        self.api_key = config('OLLAMA_API_KEY', default='dev_secret_key')

    def analyze(self, prompt: str, system_message: str = None, model: str = None) -> str:
        if system_message is None:
            system_message = DEFAULT_SYSTEM_MESSAGE
            
        if model is None:
            model = config('OLLAMA_MODEL', default='mistral:latest')
            
        # If a system message is provided, prepend it to the prompt 
        # (since the basic Express API currently only accepts a 'prompt' string)
        combined_prompt = prompt
        if system_message:
            combined_prompt = f"{system_message}\n\nUser Input:\n{prompt}"
            
        data = {
            'prompt': combined_prompt,
            'model': model
        }
        
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            self.endpoint,
            json=data,
            headers=headers,
            timeout=120 # Local models could take a while
        )
        
        response.raise_for_status()
        result = response.json()
        
        return result.get('response', '')
