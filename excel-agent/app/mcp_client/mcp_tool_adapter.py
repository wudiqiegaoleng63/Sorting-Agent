from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.mcp_client.excel_mcp_client import ExcelMCPClient


class MCPToolArgs(BaseModel):
    """Generic args model — tool_name + free-form arguments dict."""
    tool_name: str = Field(description="Name of the MCP tool to call")
    tool_args: dict = Field(default_factory=dict, description="Arguments to pass to the tool")


class MCPToolAdapter(BaseTool):
    """LangChain-compatible tool that delegates to ExcelMCPClient.

    Used by LangGraph nodes to call MCP tools by name at runtime,
    rather than creating one BaseTool per MCP tool at startup.
    """

    name: str = "mcp_excel_tool"
    description: str = (
        "Call an excel-mcp-server tool. "
        "Pass 'tool_name' and 'tool_args' to specify which tool and arguments."
    )
    args_schema: type[BaseModel] = MCPToolArgs
    mcp_client: ExcelMCPClient

    class Config:
        arbitrary_types_allowed = True

    def _run(self, tool_name: str, tool_args: dict = None) -> str:
        raise NotImplementedError("Use _arun for async execution")

    async def _arun(self, tool_name: str, tool_args: dict = None) -> str:
        return await self.mcp_client.call_tool(tool_name, tool_args or {})
