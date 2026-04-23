from typing import Optional, List, Dict, Any
import os
import logging
import openai
from .base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider implementation."""

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        api_key: str = None
    ):
        super().__init__(model_name, temperature, max_tokens)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        logger.info(f"OpenAI provider initialized with model: {model_name}")

    async def generate(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Generate response using OpenAI API."""
        try:
            messages = []
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return {
                "response": response.choices[0].message.content,
                "model": self.model_name,
                "tokens": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                }
            }

        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {str(e)}")
            raise

    async def generate_streaming(self, prompt: str, context: Optional[str] = None):
        """Generate response with streaming."""
        try:
            messages = []
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            messages.append({"role": "user", "content": prompt})

            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in streaming generation: {str(e)}")
            raise

    async def embed_text(self, text: str) -> List[float]:
        """Embed text using OpenAI API."""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Error embedding text: {str(e)}")
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts using OpenAI API."""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [data.embedding for data in response.data]

        except Exception as e:
            logger.error(f"Error embedding batch: {str(e)}")
            raise

