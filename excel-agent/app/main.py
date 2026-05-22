from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import agent_api, file_api, health_api, memory_api
from app.core.config import settings
from app.core.logger import logger
from app.mcp_client.excel_mcp_client import ExcelMCPClient, MCPConnectionError
from app.memory.memory_manager import MemoryManager
from app.memory.redis_memory import RedisMemory


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect MCP, connect Redis, build tools, create agent
    mcp_client = ExcelMCPClient()
    try:
        await mcp_client.connect()
        logger.info("Excel MCP client connected")
    except MCPConnectionError as e:
        logger.warning(f"{e}")
        logger.warning("FastAPI started, but MCP tools are unavailable.")

    app.state.mcp_client = mcp_client

    # Redis + Memory
    redis_memory = RedisMemory()
    await redis_memory.connect()
    memory_manager = MemoryManager(redis_memory)
    app.state.redis_memory = redis_memory
    app.state.memory_manager = memory_manager

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
    await redis_memory.close()
    logger.info("Redis connection closed")
    await mcp_client.disconnect()
    logger.info("Excel MCP client disconnected")


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_api.router)
app.include_router(file_api.router)
app.include_router(agent_api.router)
app.include_router(memory_api.router)