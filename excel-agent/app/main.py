from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import agent_api, file_api, health_api
from app.core.config import settings
from app.core.logger import logger
from app.mcp_client.excel_mcp_client import ExcelMCPClient, MCPConnectionError


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect MCP, build tools, create agent
    mcp_client = ExcelMCPClient()
    try:
        await mcp_client.connect()
        logger.info("Excel MCP client connected")
    except MCPConnectionError as e:
        logger.warning(f"{e}")
        logger.warning("FastAPI started, but MCP tools are unavailable.")

    app.state.mcp_client = mcp_client

    # Create agent (even if MCP failed — will error on /run instead of crash)
    agent = None
    if mcp_client.connected:
        try:
            from app.agents.agent_factory import create_excel_agent
            agent = create_excel_agent(mcp_client)
        except Exception as e:
            logger.warning(f"Failed to create agent: {e}")
            logger.warning("FastAPI started, but agent is unavailable. Check MODEL_API_KEY in .env.")
    app.state.agent = agent

    yield

    # Shutdown
    await mcp_client.disconnect()
    logger.info("Excel MCP client disconnected")


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(health_api.router)
app.include_router(file_api.router)
app.include_router(agent_api.router)
