import ollama
import asyncio
from typing import Optional, List, Dict, Any
from .base import LLMProvider
import logging

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama LLM provider implementation."""
    
    def __init__(
        self,
        model_name: str = "tinyllama",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        host: str = "http://localhost:11434",
        embedding_model: str = "nomic-embed-text"
    ):
        super().__init__(model_name, temperature, max_tokens)
        self.host = host
        self.embedding_model = embedding_model
        self.client = ollama.Client(host=host)
    
    async def generate(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Generate response using Ollama."""
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._generate_sync,
                full_prompt
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error generating response from Ollama: {str(e)}")
            raise
    
    def _generate_sync(self, prompt: str) -> Dict[str, Any]:
        """Synchronous generation (for executor)."""
        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            stream=False,
            options={
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        )
        
        return {
            "response": response.get("response", ""),
            "model": self.model_name,
            "tokens": {
                "prompt": response.get("prompt_eval_count", 0),
                "completion": response.get("eval_count", 0)
            }
        }
    
    async def generate_streaming(self, prompt: str, context: Optional[str] = None):
        """Generate response with streaming."""
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
            
            loop = asyncio.get_event_loop()
            async for chunk in self._generate_streaming_sync(full_prompt):
                yield chunk
        
        except Exception as e:
            logger.error(f"Error in streaming generation: {str(e)}")
            raise
    
    async def _generate_streaming_sync(self, prompt: str):
        """Async streaming wrapper."""
        loop = asyncio.get_event_loop()
        
        def stream_generator():
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                stream=True,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            )
            for chunk in response:
                yield chunk.get("response", "")
        
        for chunk in await loop.run_in_executor(None, lambda: list(stream_generator())):
            yield chunk
    
    async def embed_text(self, text: str) -> List[float]:
        """Embed a single text."""
        try:
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                self._embed_text_sync,
                text
            )
            return embedding
        
        except Exception as e:
            logger.error(f"Error embedding text: {str(e)}")
            raise
    
    def _embed_text_sync(self, text: str) -> List[float]:
        """Synchronous text embedding."""
        response = self.client.embeddings(
            model=self.embedding_model,
            prompt=text
        )
        return response.get("embedding", [])
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        try:
            embeddings = []
            for text in texts:
                embedding = await self.embed_text(text)
                embeddings.append(embedding)
            return embeddings
        
        except Exception as e:
            logger.error(f"Error embedding batch: {str(e)}")
            raise
