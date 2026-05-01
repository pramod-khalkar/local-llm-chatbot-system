import asyncio
import json
import logging
import re
import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from .provider.base import LLMProvider

logger = logging.getLogger(__name__)


class QueryDecision(BaseModel):
    """Query routing decision."""
    query_type: str  # "chat", "rag", "tool"
    confidence: float  # 0-1
    tool_name: Optional[str] = None
    tool_action: Optional[str] = None  # e.g., "create", "list", "complete"
    tool_params: Optional[Dict[str, Any]] = None # New field for tool parameters
    rag_required: bool = False
    rationale: str


class QueryRouter:
    """Intelligent query router for chat, RAG, and tool calls using LLM."""
    
    def __init__(self, llm_provider: LLMProvider, mcp_handler: 'MCPHandler'):
        self.llm_provider = llm_provider
        self.mcp_handler = mcp_handler
        logger.info(f"QueryRouter.__init__: mcp_handler received = {self.mcp_handler}")
        self.available_tools: List[Dict[str, Any]] = []

    async def _fetch_tools(self):
        """Fetches available tools from the MCPHandler."""
        logger.info(f"QueryRouter._fetch_tools: self.mcp_handler = {self.mcp_handler}")
        try:
            self.available_tools = await self.mcp_handler.get_available_tools()
            logger.info(f"Query router: Fetched {len(self.available_tools)} tools from MCP.")
        except Exception as e:
            logger.error(f"Error fetching tools from MCP: {str(e)}")
            self.available_tools = []

    def _get_tools_description(self) -> str:
        """Generates a formatted string of available tools for the LLM prompt."""
        if not self.available_tools:
            return "No specific tools are available."

        description = "Available tools:\n"
        for tool in self.available_tools:
            name = tool.get("name", "unknown")
            tool_description = tool.get("description", "No description provided.")
            params = tool.get("params", {})
            param_str = ", ".join([f"{k}: {v}" for k, v in params.items()])
            description += f"- Name: {name}\n  Description: {tool_description}\n  Parameters: {{{param_str}}}\n"
        return description

    async def route_query(self, query: str, context: Optional[str] = None) -> QueryDecision:
        """Route query to appropriate handler using LLM."""
        start_time = time.time()
        try:
            logger.info(f"Query router: Intelligent routing for query='{query}'")

            # Get tool descriptions
            tools_desc = self._get_tools_description()

            # Construct the prompt with tool information
            prompt = f"""You are an intelligent routing assistant for an LLM application. Your primary goal is to accurately categorize user queries to determine the best handling mechanism: a specific tool call, a RAG (Retrieval Augmented Generation) search, or a general chat response. Respond ONLY with a valid JSON object. Do not include any other text, explanations, or markdown formatting.

**Decision Hierarchy:**
1.  **Tool:** If the query clearly indicates an intent to perform a specific action that matches one of the `Available tools`, prioritize this. Extract all necessary parameters.
2.  **RAG:** If the query asks for information retrieval, summarization of documents, answering factual questions based on external knowledge, or extracting details from "my documents," route to RAG.
3.  **Chat:** If the query is a general conversation, greeting, or does not fit the criteria for a Tool or RAG, classify it as Chat.

{tools_desc}

Consider the full intent of the 'Query'. If a query implies an action, it's likely a tool. If it implies needing information from a knowledge base or documents, it's RAG.

Query: "{query}"

JSON format examples:

1. General chat:
{{"query_type": "chat", "confidence": 0.9, "tool_name": null, "tool_action": null, "tool_params": null, "rag_required": false, "rationale": "The user is engaging in general conversation."}}

2. RAG query (e.g., summarizing documents, extracting info):
{{"query_type": "rag", "confidence": 0.9, "tool_name": null, "tool_action": null, "tool_params": null, "rag_required": true, "rationale": "The user requires information extraction or summarization from documents."}}

3. Tool call (e.g., creating a todo):
{{"query_type": "tool", "confidence": 0.95, "tool_name": "create_todo", "tool_action": "create", "tool_params": {{"title": "Buy groceries", "description": "milk, eggs, bread"}}, "rag_required": false, "rationale": "The user wants to create a new todo task."}}

4. Tool call (e.g., listing todos):
{{"query_type": "tool", "confidence": 0.9, "tool_name": "list_todos", "tool_action": "list", "tool_params": {{}}, "rag_required": false, "rationale": "The user wants to see their todo list."}}

Your JSON response:
"""
            
            response = await self.llm_provider.generate(prompt=prompt)
            raw_content = response.get("response", "").strip()
            
            # Detailed Logging
            logger.info(f"Query router: --- START LLM RAW RESPONSE ---")
            logger.info(f"Query router: '{raw_content}'")
            logger.info(f"Query router: --- END LLM RAW RESPONSE ---")
            
            decision_data = {}
            json_str_to_parse = raw_content

            try:
                # Attempt to parse raw_content directly (ideal scenario)
                decision_data = json.loads(raw_content)
                logger.info(f"Query router: Successfully parsed raw_content directly.")
            except json.JSONDecodeError as e:
                logger.warning(f"Query router: Direct JSON parse failed, attempting regex extraction. Error: {e}")
                # Fallback: Use regex to find the first valid JSON object, robust against leading/trailing text
                match = re.search(r'(\{.*?\})', raw_content, re.DOTALL) # Non-greedy match
                
                if not match:
                    raise ValueError(f"No valid JSON structure found in LLM response. Raw: {raw_content}")
                
                json_str_to_parse = match.group(0)
                logger.info(f"Query router: JSON string extracted for parsing: '{json_str_to_parse}'")
                decision_data = json.loads(json_str_to_parse)

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
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Returns routing statistics (placeholder for now)."""
        return {}
