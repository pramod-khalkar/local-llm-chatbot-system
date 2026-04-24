import json
import logging
import re
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel
from .provider.base import LLMProvider

logger = logging.getLogger(__name__)


class QueryDecision(BaseModel):
    """Query routing decision."""
    query_type: str  # "chat", "rag", "tool"
    confidence: float  # 0-1
    tool_name: Optional[str] = None
    tool_action: Optional[str] = None  # e.g., "create", "list", "complete"
    rag_required: bool = False
    rationale: str


class QueryRouter:
    """Intelligent query router for chat, RAG, and tool calls using LLM."""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    async def route_query(self, query: str, context: Optional[str] = None) -> QueryDecision:
        """Route query to appropriate handler using LLM."""
        start_time = time.time()
        try:
            logger.info(f"Query router: Intelligent routing for query='{query}'")
            prompt = f"""You are a routing assistant. Analyze the user's query and return ONLY a valid JSON object. Do not include markdown, explanations, or filler.

            Query: "{query}"

            JSON format:
            {{"query_type": "chat", "confidence": 0.9, "tool_name": null, "tool_action": null, "rag_required": false, "rationale": "reasoning"}}

            {{"""

            response = await self.llm_provider.generate(prompt=prompt)
            raw_content = response.get("response", "").strip()

            # Detailed Logging
            logger.info(f"Query router: --- START LLM RAW RESPONSE ---")
            logger.info(f"Query router: '{raw_content}'")
            logger.info(f"Query router: --- END LLM RAW RESPONSE ---")

            # The prompt ends with '{', so the model likely completed the JSON.
            # We reconstruct it by prepending the '{' that we primed.
            json_str = "{" + raw_content

            # Simple, greedy regex to extract the first valid JSON
            match = re.search(r'(\{.*\})', json_str, re.DOTALL)

            if not match:
                raise ValueError(f"No valid JSON structure found in: {json_str}")

            # Final extraction and clean
            json_str = match.group(0)
            decision_data = json.loads(json_str)
            decision = QueryDecision(**decision_data)

            duration = time.time() - start_time
            logger.info(f"Query router: Decision made in {duration:.2f}s: {decision.query_type}")
            return decision

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error in intelligent routing (took {duration:.2f}s): {str(e)}")
            return QueryDecision(
                query_type="chat",
                confidence=0.0,
                rag_required=False,
                rationale=f"Fallback due to routing error: {str(e)}"
            )
