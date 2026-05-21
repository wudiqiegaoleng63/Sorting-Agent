from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.core.config import settings
from app.core.logger import logger
from app.mcp_client.excel_mcp_client import ExcelMCPClient
from app.mcp_client.mcp_tool_adapter import build_langchain_tools

SYSTEM_PROMPT = """你是一个 Excel 自动化 Agent。
你不能直接读取或修改 Excel 文件。
你只能通过提供的 MCP Excel 工具操作 Excel。

当用户要求读取、查看、清洗、排序、统计、写入、保存 Excel 时，请根据工具描述和参数 schema 自动选择合适工具。
不要编造不存在的工具。
不要编造工具 schema 中不存在的参数。
如果缺少必要参数（如 file_path），请向用户询问。
如果用户没有指定 sheet_name，默认使用 "Sheet1"。
所有输出文件应保存到 outputs 目录。
最终回答使用中文，简洁说明你做了什么、结果是什么、输出文件在哪里。"""


def create_excel_agent(mcp_client: ExcelMCPClient):
    """Create a ReAct agent with LLM + MCP Excel tools.

    Called once at FastAPI startup, the returned agent is reused across requests.
    """
    model = ChatOpenAI(
        model=settings.model_name,
        api_key=settings.model_api_key,
        base_url=settings.model_base_url,
        temperature=0,
    )

    tools = build_langchain_tools(mcp_client)
    logger.info(f"Built {len(tools)} LangChain tools from MCP: {[t.name for t in tools]}")

    agent = create_react_agent(model, tools, prompt=SYSTEM_PROMPT)
    logger.info("Excel agent created successfully")
    return agent
