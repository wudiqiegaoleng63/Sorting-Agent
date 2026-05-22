import uuid

from app.core.logger import logger
from app.mcp_client.excel_mcp_client import MCPConnectionError
from app.schemas.agent_schema import AgentRunRequest, AgentRunResponse
from app.utils.path_utils import safe_path


async def run_agent(req: AgentRunRequest) -> AgentRunResponse:
    from app.main import app

    mcp_client = app.state.mcp_client
    agent = app.state.agent
    memory = app.state.memory_manager

    if not mcp_client.connected:
        raise MCPConnectionError("MCP server not connected. Check that excel-mcp-server is running.")

    if agent is None:
        raise RuntimeError("Agent not available. Check MODEL_API_KEY in .env.")

    # Resolve session_id: reuse if provided, otherwise generate
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:16]}"

    # Load chat history from Redis (graceful fallback to empty)
    history = await memory.get_chat_history(session_id)
    logger.info(f"Session {session_id}: loaded {len(history)} history messages")

    # Build messages list: history + current user input
    messages = []
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": content})

    # Current user message
    parts = [req.task]
    if req.file_path:
        resolved = safe_path(req.file_path)
        parts.append(f"文件路径: {resolved}")
    user_content = "\n".join(parts)
    messages.append({"role": "user", "content": user_content})

    # Save user message to Redis
    await memory.append_user_message(session_id, user_content)

    logger.info(f"Running agent for task: {req.task} (session={session_id})")

    # Invoke agent
    result = await agent.ainvoke({"messages": messages})

    # Extract the last AI message as the answer
    result_messages = result.get("messages", [])
    answer = ""
    for msg in reversed(result_messages):
        if hasattr(msg, "content") and msg.content and msg.type == "ai":
            if msg.content and not msg.tool_calls:
                answer = msg.content
                break
            if msg.content:
                answer = msg.content
                break

    if not answer:
        answer = result_messages[-1].content if result_messages else "Agent completed but produced no answer."

    # Save assistant answer to Redis
    await memory.append_assistant_message(session_id, answer)

    # Get updated history count
    updated_history = await memory.get_chat_history(session_id)
    history_count = len(updated_history)

    logger.info(f"Agent answer length={len(answer)}, history_count={history_count}")
    return AgentRunResponse(session_id=session_id, answer=answer, history_count=history_count)
