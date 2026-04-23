"""
Gemini-based routing and parameter extraction for orchestration.
"""
import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiRouter:
    """Routes queries and extracts parameters using Gemini."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        """
        Initialize Gemini router.
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model: Model to use (default: gemini-2.5-flash)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=self.api_key, transport='rest')
        self.model_name = model
        self.model = genai.GenerativeModel(model_name=model)
        logger.info(f"Gemini router initialized with model: {model}")
    
    async def route_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Route query to determine its type and required tools.
        """
        try:
            prompt = f"""Analyze this query and decide the routing.

Query: "{query}"
Context: {context if context else "None"}

Determine:
1. query_type: One of ["chat", "tool", "rag"]
   - "chat": General conversation, no tools needed
   - "tool": User wants to call a tool (todo, calendar, search)
   - "rag": User asking about documents/knowledge base

2. tool_name: If tool is needed, which tool? ("todo", "calendar", "search", or "none")

3. tool_action: If tool is todo, what action? ("create", "complete", "list", "update", "delete", or "none")

4. rag_required: Boolean - should we search documents?

Return ONLY valid JSON:
{{
    "query_type": "chat|tool|rag",
    "tool_name": "todo|calendar|search|none",
    "tool_action": "create|complete|list|update|delete|none",
    "rag_required": true|false,
    "confidence": 0.0-1.0
}}

Examples:
- "Create a todo to fix the bug" → {{"query_type": "tool", "tool_name": "todo", "tool_action": "create", "rag_required": false, "confidence": 0.95}}
- "Show my todos" → {{"query_type": "tool", "tool_name": "todo", "tool_action": "list", "rag_required": false, "confidence": 0.95}}
- "Tell me about company policies" → {{"query_type": "rag", "tool_name": "none", "tool_action": "none", "rag_required": true, "confidence": 0.90}}"""
            
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            response_text = response.text.strip()
            
            # Clean JSON if model wrapped it in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            logger.info(f"Gemini routing response: {response_text}")
            routing = json.loads(response_text)
            
            return {
                "query_type": routing.get("query_type", "chat"),
                "tool_name": routing.get("tool_name", "none"),
                "tool_action": routing.get("tool_action", "none"),
                "rag_required": routing.get("rag_required", False),
                "confidence": routing.get("confidence", 0.5)
            }
        
        except Exception as e:
            logger.error(f"Error in Gemini routing: {str(e)}", exc_info=True)
            return {"query_type": "chat", "tool_name": "none", "tool_action": "none", "rag_required": False, "confidence": 0.0}

    async def extract_todo_params(self, query: str) -> Dict[str, str]:
        """Extract todo parameters (title, description) from query."""
        try:
            prompt = f"""Extract todo task details from this request:
"{query}"

Return ONLY a JSON object with exactly:
{{"title": "task title here", "description": "optional description here"}}"""
            
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            response_text = response.text.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            
            extracted = json.loads(response_text)
            return {
                "title": extracted.get("title", query[:50]),
                "description": extracted.get("description", "")
            }
        except Exception as e:
            logger.error(f"Error extracting todo params: {str(e)}")
            return {"title": query[:50], "description": ""}

    async def refine_with_rag_results(self, original_query: str, rag_results: List[str]) -> str:
        """Refine response using RAG search results."""
        try:
            rag_context = "\n\n".join([f"- {result}" for result in rag_results if result])
            prompt = f"""You are a helpful assistant. A user asked: "{original_query}"
            
Here are relevant documents:
{rag_context}

Using ONLY the information from these documents, provide a helpful answer."""
            
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error refining with RAG results: {str(e)}")
            return f"I found some relevant information but encountered an error."

    async def extract_todo_id_for_completion(self, query: str) -> Dict[str, Optional[str]]:
        """Extract todo ID or title for completion request."""
        try:
            prompt = f"""Extract the todo ID or title from this completion request: "{query}"
Return ONLY JSON: {{"todo_id": "id if mentioned", "todo_title": "title if mentioned"}}"""
            
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            response_text = response.text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            
            extracted = json.loads(response_text)
            return {
                "todo_id": extracted.get("todo_id") or None,
                "todo_title": extracted.get("todo_title") or None
            }
        except Exception as e:
            logger.error(f"Error extracting todo ID: {str(e)}")
            return {"todo_id": None, "todo_title": None}
