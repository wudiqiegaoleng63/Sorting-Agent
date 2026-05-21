from langgraph.graph import StateGraph, START, END

from app.agents.nodes import make_planner_node, make_mcp_tool_node, make_response_node
from app.agents.state import AgentState
from app.mcp_client.excel_mcp_client import ExcelMCPClient


def build_agent_graph(mcp_client: ExcelMCPClient) -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("planner_node", make_planner_node(mcp_client))
    graph.add_node("mcp_tool_node", make_mcp_tool_node(mcp_client))
    graph.add_node("response_node", make_response_node())

    graph.add_edge(START, "planner_node")
    graph.add_edge("planner_node", "mcp_tool_node")
    graph.add_edge("mcp_tool_node", "response_node")
    graph.add_edge("response_node", END)

    return graph.compile()
