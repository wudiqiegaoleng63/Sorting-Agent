from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.core.config import settings
from app.core.logger import logger


class MCPConnectionError(Exception):
    """Raised when MCP client cannot connect to the server."""


class ExcelMCPClient:
    """Manages the connection to excel-mcp-server via stdio transport.

    Lifecycle:
        connect()  →  list_tools() / call_tool()  →  disconnect()
    """

    def __init__(self):
        self._session: ClientSession | None = None
        self._read = None
        self._write = None
        self._stdio_cm = None
        self._session_cm = None
        self._tools: list[dict] = []
        self._connected = False

    # ── properties ──────────────────────────────────────────────

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def tools(self) -> list[dict]:
        """Cached tool list from the last list_tools() call."""
        return self._tools

    # ── connection ──────────────────────────────────────────────

    async def connect(self):
        """Connect to excel-mcp-server and cache the tool list.

        Raises MCPConnectionError on failure so callers can report clearly.
        """
        try:
            server_params = StdioServerParameters(
                command=settings.mcp_excel_command,
                args=settings.mcp_excel_args,
                env=settings.mcp_excel_env or None,
            )
            cmd_str = f"{settings.mcp_excel_command} {' '.join(settings.mcp_excel_args)}"
            logger.info(f"Connecting to excel-mcp-server: {cmd_str}")

            # Open stdio transport
            self._stdio_cm = stdio_client(server_params)
            self._read, self._write = await self._stdio_cm.__aenter__()

            # Open session
            self._session_cm = ClientSession(self._read, self._write)
            self._session = await self._session_cm.__aenter__()
            await self._session.initialize()

            # Cache available tools
            await self.list_tools()

            self._connected = True
            logger.info(f"Connected. Available tools: {[t['name'] for t in self._tools]}")
        except Exception as e:
            self._connected = False
            self._tools = []
            raise MCPConnectionError(
                f"Failed to connect to excel-mcp-server "
                f"({settings.mcp_excel_command} {' '.join(settings.mcp_excel_args)}): {e}"
            ) from e

    async def disconnect(self):
        """Gracefully close the MCP session and stdio transport."""
        for cm, name in [(self._session_cm, "session"), (self._stdio_cm, "stdio")]:
            if cm is not None:
                try:
                    await cm.__aexit__(None, None, None)
                except Exception as e:
                    logger.debug(f"Error closing {name}: {e}")
        self._session = None
        self._session_cm = None
        self._stdio_cm = None
        self._read = None
        self._write = None
        self._connected = False
        logger.info("MCP client disconnected")

    async def reconnect(self):
        """Disconnect then connect again."""
        await self.disconnect()
        await self.connect()

    # ── tool operations ─────────────────────────────────────────

    async def list_tools(self) -> list[dict]:
        """Query the MCP server for available tools and cache the result.

        Returns:
            List of dicts with keys: name, description, inputSchema
        """
        if self._session is None:
            raise MCPConnectionError("Not connected. Call connect() first.")

        result = await self._session.list_tools()
        self._tools = [
            {
                "name": t.name,
                "description": t.description or "",
                "inputSchema": t.inputSchema,
            }
            for t in result.tools
        ]
        logger.debug(f"list_tools: {[t['name'] for t in self._tools]}")
        return self._tools

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Call an MCP tool by name with the given arguments.

        Args:
            tool_name: Name of the tool (e.g. "read_excel_file")
            arguments: Dict of arguments to pass to the tool

        Returns:
            Concatenated text content from the tool result

        Raises:
            MCPConnectionError: if not connected
            ValueError: if the tool name is not available
        """
        if not self._connected or self._session is None:
            raise MCPConnectionError("Not connected. Call connect() first.")

        available = {t["name"] for t in self._tools}
        if tool_name not in available:
            raise ValueError(
                f"Tool '{tool_name}' not found. Available: {sorted(available)}"
            )

        logger.info(f"call_tool: {tool_name}({arguments})")
        result = await self._session.call_tool(tool_name, arguments)

        text_parts = [c.text for c in result.content if hasattr(c, "text")]
        return "\n".join(text_parts)
