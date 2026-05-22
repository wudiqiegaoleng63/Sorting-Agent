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
    mcp_excel_args: str = "excel-mcp-server,stdio"
    mcp_excel_env: dict[str, str] = {}

    # Redis (short-term memory)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    redis_memory_ttl: int = 7200
    redis_max_messages: int = 20

    @property
    def mcp_excel_args_list(self) -> list[str]:
        return [a.strip() for a in self.mcp_excel_args.split(",") if a.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
