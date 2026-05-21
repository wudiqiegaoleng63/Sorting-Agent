from typing import TypedDict


class AgentState(TypedDict):
    task: str
    file_path: str
    plan: str
    tool_calls: list[dict]
    tools_used: list[str]
    result: str
