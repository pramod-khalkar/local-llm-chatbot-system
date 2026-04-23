from typing import Optional, List, Dict, Any
import os
import logging
import asyncio
import google.generativeai as genai
from .base import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider implementation."""
    
    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        api_key: str = None
    ):
        super().__init__(model_name, temperature, max_tokens)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=self.api_key, transport='rest')
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            }
        )
        logger.info(f"Gemini provider initialized with model: {model_name}")
    
    async def generate(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Generate response using Gemini API."""
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nUser: {prompt}"
            
            # Run synchronous generate_content in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(full_prompt)
            )
            
            return {
                "response": response.text,
                "model": self.model_name,
                "tokens": {
                    "prompt": 0,
                    "completion": 0,
                    "total": 0
                }
            }
        
        except Exception as e:
            logger.error(f"Error generating response from Gemini: {str(e)}")
            raise
    
    async def generate_streaming(self, prompt: str, context: Optional[str] = None):
        """Generate response with streaming."""
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nUser: {prompt}"
            
            # Streaming also needs to be handled carefully with REST
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(full_prompt, stream=True)
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            logger.error(f"Error in Gemini streaming generation: {str(e)}")
            raise
    
    async def embed_text(self, text: str) -> List[float]:
        """Embed text using Gemini API."""
        try:
            embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
            result = genai.embed_content(
                model=embedding_model,
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        
        except Exception as e:
            logger.error(f"Error embedding text with Gemini: {str(e)}")
            raise
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts using Gemini API."""
        try:
            embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
            result = genai.embed_content(
                model=embedding_model,
                content=texts,
                task_type="retrieval_document"
            )
            return result['embeddings']
        
        except Exception as e:
            logger.error(f"Error embedding batch with Gemini: {str(e)}")
            raise
