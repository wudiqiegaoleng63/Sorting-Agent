from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    session_id: str | None = Field(None, description="Session identifier; auto-generated if omitted")
    task: str = Field(..., description="The task description for the agent")
    file_path: str | None = Field(None, description="Path to the Excel file (relative to uploads dir)")


class AgentStep(BaseModel):
    type: str
    title: str
    content: str = ""
    tool_name: str | None = None
    arguments: dict | None = None
    status: str = "success"


class OutputFile(BaseModel):
    file_id: str = ""
    filename: str = ""
    download_url: str = ""


class AgentRunResponse(BaseModel):
    session_id: str
    answer: str
    steps: list[AgentStep] = Field(default_factory=list)
    output_file: OutputFile | None = None
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
