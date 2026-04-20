from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, model_name: str, temperature: float = 0.7, max_tokens: int = 2048):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    async def generate(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Generate response from LLM."""
        pass
    
    @abstractmethod
    async def generate_streaming(self, prompt: str, context: Optional[str] = None):
        """Generate response from LLM with streaming."""
        pass
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass


class ProviderFactory:
    """Factory for creating LLM providers."""
    
    _providers = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class):
        """Register a provider."""
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, provider_type: str, **kwargs) -> LLMProvider:
        """Create a provider instance."""
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_type}")
        
        return cls._providers[provider_type](**kwargs)
