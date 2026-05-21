from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Excel Agent"
    debug: bool = False

    # Directories
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    uploads_dir: Path = base_dir / "uploads"
    outputs_dir: Path = base_dir / "outputs"

    # LLM (OpenAI-compatible)
    model_name: str = "deepseek-chat"
    model_api_key: str = ""
    model_base_url: str = "https://api.deepseek.com"

    # excel-mcp-server
    mcp_excel_command: str = "uvx"
    mcp_excel_args: list[str] = ["excel-mcp-server", "stdio"]
    mcp_excel_env: dict[str, str] = {}

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
