from fastapi import APIRouter, HTTPException

from app.mcp_client.excel_mcp_client import MCPConnectionError
from app.schemas.agent_schema import AgentRunRequest, AgentRunResponse, MCPToolInfo, MCPToolsResponse
from app.services.agent_service import run_agent

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/run", response_model=AgentRunResponse)
async def agent_run(req: AgentRunRequest):
    try:
        return await run_agent(req)
    except MCPConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/tools", response_model=MCPToolsResponse)
async def list_mcp_tools():
    from app.main import app

    mcp_client = app.state.mcp_client
    if not mcp_client.connected:
        return MCPToolsResponse(
            connected=False,
            tools=[],
            error="MCP server not connected. Check that excel-mcp-server is running.",
        )

    tools = [
        MCPToolInfo(name=t["name"], description=t["description"], input_schema=t["inputSchema"])
        for t in mcp_client.tools
    ]
    return MCPToolsResponse(connected=True, tools=tools)
