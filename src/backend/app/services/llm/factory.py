from decouple import config
from app.services.llm.providers.base import LLMProvider
import logging

logger = logging.getLogger(__name__)

class LLMFactory:
    """
    Factory to instantiate the appropriate LLM provider 
    based on application configuration.
    """
    
    _providers = {}

    @classmethod
    def get_provider(cls, provider_name: str = None) -> LLMProvider:
        """
        Get an instance of the configured LLM provider.
        
        Args:
            provider_name: Override the configured provider (e.g., 'azure', 'gemini', 'ollama')
            
        Returns:
            An instance of a class implementing LLMProvider
        """
        if provider_name is None:
            provider_name = config('LLM_PROVIDER', default='ollama').lower()
            
        if provider_name in cls._providers:
            return cls._providers[provider_name]
            
        try:
            if provider_name == 'azure':
                from app.services.llm.providers.azure import AzureProvider
                provider = AzureProvider()
            elif provider_name == 'gemini':
                from app.services.llm.providers.gemini import GeminiProvider
                provider = GeminiProvider()
            elif provider_name == 'ollama':
                from app.services.llm.providers.ollama import OllamaProvider
                provider = OllamaProvider()
            else:
                logger.warning(f"Unknown LLM provider '{provider_name}', falling back to Azure.")
                from app.services.llm.providers.azure import AzureProvider
                provider = AzureProvider()
                
            cls._providers[provider_name] = provider
            return provider
            
        except ImportError as e:
            logger.error(f"Failed to import provider {provider_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize provider {provider_name}: {e}")
            raise
