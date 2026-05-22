# Sorting Agent — Agent 开发规范

本文档定义了在 Sorting-Agent 项目中新增 Agent 时必须遵守的目录结构和代码约定。

## 项目整体结构

```
Sorting-Agent/
├── CLAUDE.md                # 项目级指引（所有 Agent 共享）
├── CONTRIBUTING.md           # 本文档
├── .gitignore
├── excel-agent/              # Excel 自动化 Agent（已有）
├── xxx-agent/                # 新 Agent，结构对齐 excel-agent
└── shared/                   # 可选：多 Agent 共用的工具/配置
```

## 1. 目录结构

每个 Agent 必须是一个独立顶层目录，命名格式 `{功能}-agent`，内部结构如下：

```
xxx-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 入口 + lifespan
│   ├── api/
│   │   ├── __init__.py
│   │   ├── agent_api.py         # 必须：POST /api/agent/run, GET /api/agent/tools
│   │   └── health_api.py        # 必须：GET /health
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # pydantic-settings 配置
│   │   └── logger.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── agent_schema.py      # 请求/响应模型
│   ├── services/
│   │   ├── __init__.py
│   │   └── agent_service.py     # 调 agent.ainvoke()
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agent_factory.py     # create_xxx_agent()
│   ├── mcp_client/
│   │   ├── __init__.py
│   │   ├── xxx_mcp_client.py    # MCP Client 连接逻辑
│   │   └── mcp_tool_adapter.py  # MCP tools → LangChain @tool
│   └── utils/
│       ├── __init__.py
│       └── path_utils.py        # 路径安全校验
├── data/                        # 数据目录（加 .gitkeep）
├── uploads/                     # 上传目录（加 .gitkeep）
├── outputs/                     # 输出目录（加 .gitkeep）
├── tests/
├── pyproject.toml
├── .env.example
└── README.md
```

## 2. 必须遵守的约定

### 2.1 技术栈

| 项目 | 要求 |
|------|------|
| Python | 3.11+ |
| 包管理 | uv |
| Web 框架 | FastAPI |
| Agent 框架 | LangGraph `create_react_agent` |
| LLM | `langchain-openai` ChatOpenAI（OpenAI-compatible） |
| MCP Client | `mcp` Python SDK（stdio transport） |
| 配置 | `pydantic-settings` |

### 2.2 API 接口

每个 Agent 必须实现以下接口：

**`GET /health`**

```json
{"status": "ok"}
```

**`POST /api/agent/run`**

请求：
```json
{
  "user_id": "10001",
  "session_id": "sess_001",
  "task": "帮我读取这个文件",
  "file_path": "uploads/file.xlsx"
}
```

响应：
```json
{
  "answer": "我读取了文件，共有 3 个 sheet...",
  "session_id": "sess_001"
}
```

**`GET /api/agent/tools`**

响应：
```json
{
  "connected": true,
  "tools": [
    {"name": "read_data", "description": "...", "inputSchema": {...}}
  ],
  "error": null
}
```

### 2.3 配置规范

`app/core/config.py` 使用 `pydantic-settings`，必须包含：

```python
class Settings(BaseSettings):
    # LLM
    model_name: str = "deepseek-chat"
    model_api_key: str = ""
    model_base_url: str = "https://api.deepseek.com"

    # MCP Server — 用 Agent 功能名作前缀
    mcp_xxx_command: str = "uvx"       # xxx 替换为功能名
    mcp_xxx_args: list[str] = ["xxx-mcp-server", "stdio"]
    mcp_xxx_env: dict[str, str] = {}

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
```

`.env.example` 必须包含：

```
MODEL_NAME=
MODEL_API_KEY=
MODEL_BASE_URL=
MCP_XXX_COMMAND=
MCP_XXX_ARGS=
DEBUG=false
```

### 2.4 Agent 创建

`app/agents/agent_factory.py` 必须使用 `create_react_agent`：

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

def create_xxx_agent(mcp_client):
    model = ChatOpenAI(
        model=settings.model_name,
        api_key=settings.model_api_key,
        base_url=settings.model_base_url,
        temperature=0,
    )
    tools = build_langchain_tools(mcp_client)
    agent = create_react_agent(model, tools, prompt=SYSTEM_PROMPT)
    return agent
```

### 2.5 MCP Client

`app/mcp_client/xxx_mcp_client.py` 必须实现：

- `connect()` — 通过 stdio 连接 MCP Server，失败时抛 `MCPConnectionError`
- `disconnect()` — 优雅关闭
- `list_tools()` → `list[dict]` — 返回 `[{name, description, inputSchema}]`
- `call_tool(tool_name, arguments)` → `str` — 调用 MCP 工具并返回结果

### 2.6 MCP Tool Adapter

`app/mcp_client/mcp_tool_adapter.py` 必须实现：

- `build_langchain_tools(mcp_client)` → `list` — 把每个 MCP tool 包装为 LangChain `@tool`
- 每个 `@tool` 的 description 必须包含完整的参数说明（从 inputSchema 提取）
- 内部调用 `mcp_client.call_tool()`

### 2.7 FastAPI 生命周期

`app/main.py` 的 lifespan 必须：

1. 启动时连接 MCP Server
2. 创建 Agent（`create_xxx_agent`）
3. MCP 连接失败或 API key 缺失时**不崩溃**，log warning，`/api/agent/run` 返回 503
4. 关闭时断开 MCP 连接

## 3. 禁止事项

| 禁止 | 原因 |
|------|------|
| 关键词 if/else 选工具 | 工具选择必须由 LLM 决策 |
| 自定义业务工具逻辑 | 所有操作通过 MCP Client → MCP Server |
| 在应用代码中用 pandas/openpyxl | MCP Server 内部使用，Agent 代码不直接依赖 |
| 自定义 MCP Server | 使用现成的 MCP Server |
| 硬编码文件路径 | 通过 config 读取，路径必须经过 path_utils 校验 |
| 向 stdout 打印非 JSON | MCP stdio 模式下 stdout 只能是合法 JSON |

## 4. 依赖要求

`pyproject.toml` 必须包含：

```toml
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "python-multipart>=0.0.9",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "langchain>=0.3.0",
    "langchain-openai>=0.3.0",
    "langgraph>=0.2.0",
    "mcp>=1.0.0",
    "python-dotenv>=1.0.0",
]
```

## 5. README 要求

每个 Agent 的 `README.md` 必须包含：

1. 功能简介
2. 架构图（FastAPI → AgentService → create_react_agent → MCP tools → MCP Server）
3. 前置条件
4. 安装步骤（`uv sync`）
5. 配置说明（`.env` 字段）
6. 启动命令
7. API 接口及 curl 示例
8. 注意事项

## 6. 验收清单

新增 Agent 合入前，确认以下全部通过：

- [ ] 目录结构符合规范
- [ ] API 接口符合规范（`/health`、`/api/agent/run`、`/api/agent/tools`）
- [ ] 配置通过 pydantic-settings + .env
- [ ] Agent 使用 `create_react_agent`，无关键词规则
- [ ] MCP Client 实现 `connect`/`disconnect`/`list_tools`/`call_tool`
- [ ] MCP 连接失败或 API key 缺失时服务不崩溃
- [ ] 代码中无 pandas/openpyxl 直接使用
- [ ] 代码中无自定义业务工具逻辑
- [ ] 路径经过安全校验
- [ ] README 完整
- [ ] `uv sync` 可安装依赖
- [ ] `uvicorn app.main:app` 可启动
