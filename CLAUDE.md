# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Excel 智能自动化 Agent — 通过自然语言指令操作 Excel 文件。
技术栈：Python + FastAPI + LangGraph + MCP（excel-mcp-server）。
LLM 自动决策调用 MCP 工具，不使用关键词规则。

## Environment

- **Python 3.11+**
- **uv** for package and venv management
- **Node.js 18+** (required for excel-mcp-server via uvx)
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
  → AgentService
    → create_react_agent (LLM 自动选工具、填参数、多步循环)
      → build_langchain_tools (MCP tools → LangChain @tool)
        → ExcelMCPClient (stdio connection to excel-mcp-server)
          → excel-mcp-server (MCP Server, via uvx)
```

Key flow:
- `app/main.py`: FastAPI app with lifespan — connects MCP, creates agent on startup
- `app/agents/agent_factory.py`: creates `create_react_agent` with ChatOpenAI + MCP tools
- `app/mcp_client/excel_mcp_client.py`: stdio transport to excel-mcp-server
- `app/mcp_client/mcp_tool_adapter.py`: converts each MCP tool → LangChain @tool with description + schema
- `app/services/agent_service.py`: invokes agent.ainvoke() and extracts answer

## Constraints

- **No custom Excel logic** — all Excel operations go through MCP Client → excel-mcp-server
- **No pandas/openpyxl** in application code
- **No custom MCP Server** — use existing excel-mcp-server only
- **No keyword rules** — tool selection is done by LLM via create_react_agent, not if/else
- **Path safety** — all file paths validated via `app/utils/path_utils.py` to prevent traversal
- Uploaded files → `uploads/`, output files → `outputs/`

## Workflow Rules

- **Always invoke superpowers skills** before writing any code — brainstorming, TDD, debugging, etc. as applicable
- **Always call context7 MCP** (`mcp__context7__resolve-library-id` → `mcp__context7__query-docs`) to check the latest API/usage before writing code that uses any library or framework
- **Use tavily MCP** (`mcp__tavily__tavily_search` etc.) for web searches instead of WebSearch tool
- **Git 版本管理** — 每次大版本更新（完成一个阶段性功能/里程碑）必须用 git commit 提交，commit message 用语义化版本号前缀，如 `v0.2.0: LLM 自动决策重构`

## Repository

- Remote: `https://github.com/wudiqiegaoleng63/Sorting-Agent.git`
- Branch: `main`
