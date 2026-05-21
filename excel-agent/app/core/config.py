from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Excel Agent"
    debug: bool = False

    # Directories
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    uploads_dir: Path = base_dir / "uploads"
    outputs_dir: Path = base_dir / "outputs"

    # excel-mcp-server — started via uvx
    mcp_server_command: str = "uvx"
    mcp_server_args: list[str] = ["excel-mcp-server", "stdio"]
    mcp_server_env: dict[str, str] = {}

    # LLM
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_base_url: str | None = None

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
