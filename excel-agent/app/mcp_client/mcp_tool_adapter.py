import json

from langchain_core.tools import tool

from app.mcp_client.excel_mcp_client import ExcelMCPClient


def _schema_to_description(schema: dict) -> str:
    """Convert a JSON Schema into a human-readable parameter description for the LLM."""
    if not schema:
        return ""
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    lines = []
    for name, prop in props.items():
        req = " (required)" if name in required else " (optional)"
        typ = prop.get("type", "any")
        desc = prop.get("description", prop.get("title", ""))
        default = f', default={prop.get("default")}' if "default" in prop else ""
        lines.append(f"  - {name}: {typ}{req}{default} — {desc}")
    return "\n".join(lines)


def build_langchain_tools(mcp_client: ExcelMCPClient) -> list:
    """Convert all MCP tools from excel-mcp-server into LangChain @tool functions.

    Each MCP tool becomes its own LangChain tool with:
      - name = MCP tool name
      - description = MCP description + full parameter schema
      - single `arguments` dict parameter (so LLM can pass any valid JSON)
      - internally delegates to mcp_client.call_tool()
    """
    tools = []
    for tool_info in mcp_client.tools:
        name = tool_info["name"]
        description = tool_info.get("description", "")
        schema = tool_info.get("inputSchema", {})

        # Build a rich description that includes the parameter schema
        param_docs = _schema_to_description(schema)
        full_description = description
        if param_docs:
            full_description += f"\n\nParameters:\n{param_docs}"

        # Create a closure that captures name and mcp_client
        def _make_tool(tool_name: str, tool_desc: str, client: ExcelMCPClient):
            @tool(tool_name)
            async def mcp_tool(arguments: str) -> str:
                """{tool_desc}"""
                args = json.loads(arguments) if isinstance(arguments, str) else arguments
                return await client.call_tool(tool_name, args)
            mcp_tool.description = tool_desc
            return mcp_tool

        tools.append(_make_tool(name, full_description, mcp_client))

    return tools
