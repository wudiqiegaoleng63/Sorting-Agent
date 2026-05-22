from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    session_id: str | None = Field(None, description="Session identifier; auto-generated if omitted")
    task: str = Field(..., description="The task description for the agent")
    file_path: str | None = Field(None, description="Path to the Excel file (relative to uploads dir)")


class AgentRunResponse(BaseModel):
    session_id: str
    answer: str
    history_count: int = 0


class MCPToolInfo(BaseModel):
    name: str
    description: str = ""
    input_schema: dict = Field(default_factory=dict, alias="inputSchema")

    model_config = {"populate_by_name": True}


class MCPToolsResponse(BaseModel):
    connected: bool
    tools: list[MCPToolInfo] = Field(default_factory=list)
    error: str | None = None
