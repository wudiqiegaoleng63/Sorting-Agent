from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    task: str = Field(..., description="The task description for the agent")
    file_path: str = Field(..., description="Path to the Excel file (relative to uploads dir)")


class AgentRunResponse(BaseModel):
    task: str
    result: str
    tools_used: list[str] = Field(default_factory=list)


class MCPToolInfo(BaseModel):
    name: str
    description: str = ""
    input_schema: dict = Field(default_factory=dict, alias="inputSchema")

    model_config = {"populate_by_name": True}


class MCPToolsResponse(BaseModel):
    connected: bool
    tools: list[MCPToolInfo] = Field(default_factory=list)
    error: str | None = None
