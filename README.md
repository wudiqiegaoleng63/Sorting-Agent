# Excel Agent

Excel 智能自动化 Agent — 基于 Python + FastAPI + LangGraph + MCP。

LLM 自动决策调用 excel-mcp-server 工具，无需手动编写工具选择逻辑。

## 架构

```
FastAPI
  → AgentService
    → create_react_agent (LLM 自动选工具)
      → MCP Tool Adapter (MCP tools → LangChain tools)
        → ExcelMCPClient (stdio → excel-mcp-server)
          → excel-mcp-server (MCP Server, via uvx)
```

## 前置条件

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 包管理器
- Node.js 18+ (uvx 运行 excel-mcp-server 需要)
- LLM API Key (DeepSeek / OpenAI / 其他 OpenAI-compatible)

## 安装

```bash
cd excel-agent
uv sync
```

## 配置

```bash
cp .env.example .env
```

编辑 `.env`，填入：

```
MODEL_NAME=deepseek-chat
MODEL_API_KEY=your-api-key-here
MODEL_BASE_URL=https://api.deepseek.com
```

支持任何 OpenAI-compatible API（DeepSeek、Qwen、OpenAI 等）。

## 启动

```bash
uv run uvicorn app.main:app --reload
```

服务启动后访问 http://localhost:8000/docs 查看 API 文档。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /health | 健康检查 |
| POST | /api/files/upload | 上传 Excel 文件 |
| POST | /api/agent/run | 执行 Agent 任务 |
| GET | /api/agent/tools | 查看 MCP 可用工具 |

### 上传文件

```bash
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@/path/to/your/file.xlsx"
```

### 执行任务

```bash
curl -X POST http://localhost:8000/api/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "task": "读取第一个sheet的所有数据",
    "file_path": "uploads/file.xlsx"
  }'
```

Agent 会自动选择合适的 MCP 工具完成任务。

## 注意事项

- 所有 Excel 操作通过 MCP Client → excel-mcp-server，不使用 pandas/openpyxl
- 工具选择由 LLM 自动决策，不使用关键词规则
- 文件路径限制在项目目录内，防止任意文件访问
