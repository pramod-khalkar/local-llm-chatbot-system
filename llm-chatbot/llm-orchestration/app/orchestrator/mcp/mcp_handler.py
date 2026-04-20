import httpx
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class MCPHandler:
    """MCP Server integration for tool management."""
    
    def __init__(self, host: str = "localhost", port: int = 8002):
        self.base_url = f"http://{host}:{port}"
        self.client = httpx.AsyncClient()
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools."""
        try:
            response = await self.client.get(f"{self.base_url}/tools", timeout=10.0)
            if response.status_code == 200:
                return response.json().get("tools", [])
            logger.warning(f"Failed to get tools: {response.status_code}")
            return []
        
        except Exception as e:
            logger.error(f"Error getting MCP tools: {str(e)}")
            return []
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/{tool_name}/call",
                json={"params": params},
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            
            logger.warning(f"Tool call failed: {response.status_code}")
            return {"error": "Tool call failed"}
        
        except Exception as e:
            logger.error(f"Error calling MCP tool: {str(e)}")
            return {"error": str(e)}
    
    async def create_todo(self, title: str, description: str = "", due_date: Optional[str] = None) -> Dict[str, Any]:
        """Create a todo task via MCP."""
        return await self.call_tool("create_todo", {
            "title": title,
            "description": description,
            "due_date": due_date
        })
    
    async def list_todos(self) -> Dict[str, Any]:
        """List all todo tasks via MCP."""
        return await self.call_tool("list_todos", {})
    
    async def complete_todo(self, todo_id: str) -> Dict[str, Any]:
        """Mark a todo as complete via MCP."""
        return await self.call_tool("complete_todo", {"id": todo_id})
