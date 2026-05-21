# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Excel 智能自动化 Agent — 通过自然语言指令操作 Excel 文件。
技术栈：Python + FastAPI + LangGraph + MCP（excel-mcp-server）。

## Environment

- **Python 3.11+**
- **uv** for package and venv management
- **Node.js 18+** (required for excel-mcp-server)
- Project root: `excel-agent/`

## Commands

```bash
cd excel-agent
uv sync                    # Install dependencies
uv run uvicorn app.main:app --reload   # Start dev server
uv run pytest              # Run tests
```

## Architecture

```
FastAPI (HTTP API)
  → AgentService (business logic)
    → LangGraph (planner_node → mcp_tool_node → response_node)
      → MCPToolAdapter (wraps MCP tools as LangChain tools)
        → ExcelMCPClient (stdio connection to excel-mcp-server)
          → excel-mcp-server (MCP Server, via npx)
```

Key flow:
- `app/main.py`: FastAPI app with lifespan that connects/disconnects MCP client
- `app/agents/graph.py`: LangGraph StateGraph with 3 nodes
- `app/mcp_client/excel_mcp_client.py`: stdio transport to excel-mcp-server
- `app/mcp_client/mcp_tool_adapter.py`: converts MCP tools → LangChain BaseTool
- `app/services/agent_service.py`: orchestrates graph invocation

## Constraints

- **No custom Excel logic** — all Excel operations go through MCP Client → excel-mcp-server
- **No pandas/openpyxl** in application code
- **No custom MCP Server** — use existing excel-mcp-server only
- **Path safety** — all file paths validated via `app/utils/path_utils.py` to prevent traversal
- Uploaded files → `uploads/`, output files → `outputs/`

## Workflow Rules

- **Always invoke superpowers skills** before writing any code — brainstorming, TDD, debugging, etc. as applicable
- **Always call context7 MCP** (`mcp__context7__resolve-library-id` → `mcp__context7__query-docs`) to check the latest API/usage before writing code that uses any library or framework
- **Use tavily MCP** (`mcp__tavily__tavily_search` etc.) for web searches instead of WebSearch tool
- **Git 版本管理** — 每次大版本更新（完成一个阶段性功能/里程碑）必须用 git commit 提交，commit message 用语义化版本号前缀，如 `v0.1.0: 实现 MCP Client 层`

## Repository

- Remote: `https://github.com/wudiqiegaoleng63/Sorting-Agent.git`
- Branch: `main`
