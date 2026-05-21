from app.core.logger import logger
from app.mcp_client.excel_mcp_client import MCPConnectionError
from app.schemas.agent_schema import AgentRunRequest, AgentRunResponse
from app.utils.path_utils import safe_path


async def run_agent(req: AgentRunRequest) -> AgentRunResponse:
    from app.main import app

    mcp_client = app.state.mcp_client
    agent = app.state.agent

    if not mcp_client.connected:
        raise MCPConnectionError("MCP server not connected. Check that excel-mcp-server is running.")

    # Build user message content
    parts = [req.task]
    if req.file_path:
        resolved = safe_path(req.file_path)
        parts.append(f"文件路径: {resolved}")
    user_content = "\n".join(parts)

    logger.info(f"Running agent for task: {req.task}")

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_content}]}
    )

    # Extract the last AI message as the answer
    messages = result.get("messages", [])
    answer = ""
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content and msg.type == "ai":
            # Skip messages that are just tool calls with no text content
            if msg.content and not msg.tool_calls:
                answer = msg.content
                break
            if msg.content:
                answer = msg.content
                break

    if not answer:
        # Fallback: use the last message content
        answer = messages[-1].content if messages else "Agent completed but produced no answer."

    logger.info(f"Agent answer length={len(answer)}")
    return AgentRunResponse(answer=answer, session_id=req.session_id)
