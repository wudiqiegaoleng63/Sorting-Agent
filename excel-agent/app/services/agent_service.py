from app.agents.graph import build_agent_graph
from app.agents.state import AgentState
from app.core.logger import logger
from app.schemas.agent_schema import AgentRunRequest, AgentRunResponse
from app.utils.path_utils import safe_path


async def run_agent(req: AgentRunRequest) -> AgentRunResponse:
    from app.main import app

    mcp_client = app.state.mcp_client
    graph = build_agent_graph(mcp_client)

    # Validate file path is within project
    safe_path(req.file_path)

    initial_state: AgentState = {
        "task": req.task,
        "file_path": req.file_path,
        "plan": "",
        "tool_calls": [],
        "tools_used": [],
        "result": "",
    }

    logger.info(f"Running agent for task: {req.task}")
    result = await graph.ainvoke(initial_state)

    return AgentRunResponse(
        task=req.task,
        result=result.get("result", ""),
        tools_used=result.get("tools_used", []),
    )
