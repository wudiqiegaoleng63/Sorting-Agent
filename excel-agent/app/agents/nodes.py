import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.prompts import PLANNER_SYSTEM_PROMPT, RESPONSE_SYSTEM_PROMPT
from app.agents.state import AgentState
from app.core.logger import logger
from app.mcp_client.excel_mcp_client import ExcelMCPClient


def make_planner_node(mcp_client: ExcelMCPClient):
    """Create the planner_node: analyzes the task and decides which MCP tools to call."""

    async def planner_node(state: AgentState) -> dict:
        tool_descriptions = "\n".join(
            f"- {t['name']}: {t['description']}" for t in mcp_client.tools
        )
        user_msg = (
            f"Task: {state['task']}\n"
            f"File: {state['file_path']}\n\n"
            f"Available tools:\n{tool_descriptions}"
        )
        # TODO: replace with actual LLM call
        logger.info(f"[planner_node] Task: {state['task']}, File: {state['file_path']}")
        logger.info(f"[planner_node] Available tools: {[t['name'] for t in mcp_client.tools]}")

        # Placeholder: return empty plan for now (LLM integration in next phase)
        return {"plan": user_msg, "tool_calls": [], "tools_used": []}

    return planner_node


def make_mcp_tool_node(mcp_client: ExcelMCPClient):
    """Create the mcp_tool_node: executes MCP tool calls from the plan."""

    async def mcp_tool_node(state: AgentState) -> dict:
        tool_calls = state.get("tool_calls", [])
        results = []
        tools_used = []

        for call in tool_calls:
            tool_name = call["tool"]
            arguments = call.get("arguments", {})
            logger.info(f"[mcp_tool_node] Calling {tool_name} with {arguments}")
            try:
                result = await mcp_client.call_tool(tool_name, arguments)
                results.append(result)
                tools_used.append(tool_name)
            except Exception as e:
                logger.error(f"[mcp_tool_node] Error calling {tool_name}: {e}")
                results.append(f"Error calling {tool_name}: {e}")

        return {"result": "\n---\n".join(results), "tools_used": tools_used}

    return mcp_tool_node


def make_response_node():
    """Create the response_node: formats the final response."""

    async def response_node(state: AgentState) -> dict:
        logger.info(f"[response_node] Formatting response for task: {state['task']}")

        if not state.get("tool_calls"):
            return {"result": f"No tools were needed for task: {state['task']}"}

        # TODO: replace with actual LLM call for summarization
        return {"result": state.get("result", "Task completed.")}

    return response_node
