import uuid

from app.core.logger import logger
from app.mcp_client.excel_mcp_client import MCPConnectionError
from app.schemas.agent_schema import AgentRunResponse, AgentStep, OutputFile
from app.utils.path_utils import safe_path


def _extract_steps(messages: list, task: str, file_path: str | None) -> list[AgentStep]:
    """Walk the agent message chain and extract a public decision summary."""
    steps: list[AgentStep] = []

    # Step 1: user input
    input_parts = [task]
    if file_path:
        input_parts.append(f"文件: {file_path}")
    steps.append(AgentStep(type="input", title="用户任务", content="\n".join(input_parts)))

    for msg in messages:
        # AI messages with tool calls → tool selection
        if getattr(msg, "type", None) == "ai" and getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                steps.append(AgentStep(
                    type="tool_selection",
                    title="工具决策",
                    content=f"LLM 选择调用工具: {tc['name']}",
                    tool_name=tc["name"],
                    arguments=tc.get("args", {}),
                ))
            continue

        # Tool result messages
        if getattr(msg, "type", None) == "tool":
            tool_name = getattr(msg, "name", "unknown")
            content = getattr(msg, "content", "")
            if isinstance(content, list):
                content = " ".join(c.text for c in content if hasattr(c, "text"))
            # Truncate very long results for display
            if len(content) > 500:
                content = content[:500] + "..."
            steps.append(AgentStep(
                type="tool_result",
                title="工具执行结果",
                content=content,
                tool_name=tool_name,
            ))
            continue

    return steps


def _detect_output_file(steps: list[AgentStep]) -> OutputFile | None:
    """Check if any tool step created an output file in the outputs/ directory."""
    for step in steps:
        if step.type == "tool_result" and step.content:
            # Only detect files explicitly under outputs/ directory
            for keyword in ("outputs/", "output/"):
                idx = step.content.find(keyword)
                if idx != -1:
                    snippet = step.content[idx:idx + 80]
                    for ext in (".xlsx", ".xls", ".csv"):
                        end = snippet.find(ext)
                        if end != -1:
                            filepath = snippet[:end + len(ext)].split()[0].rstrip("'\")},")
                            filename = filepath.split("/")[-1]
                            if filename.endswith(ext) and len(filename) > ext.__len__():
                                return OutputFile(
                                    file_id=filename,
                                    filename=filename,
                                    download_url=f"/api/files/download/{filename}",
                                )
    return None


async def run_agent(req) -> AgentRunResponse:
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

    # Extract decision steps from the full message chain (only current turn)
    steps = _extract_steps(result_messages, req.task, req.file_path)

    # Add final answer step
    steps.append(AgentStep(type="final", title="最终回答", content=answer))

    # Detect output file
    output_file = _detect_output_file(steps)

    # Save assistant answer to Redis
    await memory.append_assistant_message(session_id, answer)

    # Get updated history count
    updated_history = await memory.get_chat_history(session_id)
    history_count = len(updated_history)

    logger.info(f"Agent answer length={len(answer)}, steps={len(steps)}, history_count={history_count}")
    return AgentRunResponse(
        session_id=session_id,
        answer=answer,
        steps=steps,
        output_file=output_file,
        history_count=history_count,
    )
