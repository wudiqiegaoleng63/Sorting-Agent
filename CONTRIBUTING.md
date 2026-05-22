# Sorting Agent — 项目开发规范

本文档定义了 Sorting-Agent 项目的整体技术栈、目录结构和开发约定。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | React + Vite | TypeScript，负责 Agent 交互界面 |
| 后端 | Python + FastAPI | 提供 HTTP API，管理 Agent 生命周期 |
| Agent | LangGraph `create_react_agent` | LLM 自动决策调用工具，不用关键词规则 |
| LLM | langchain-openai ChatOpenAI | OpenAI-compatible（DeepSeek / Qwen / OpenAI） |
| 工具层 | MCP（Model Context Protocol） | 通过 MCP Client 调用现成 MCP Server |
| 短期记忆 | Redis | 会话历史存储，支持多轮对话 |
| 包管理 | uv（Python）/ npm（Node.js） | |

## 项目整体结构

```
Sorting-Agent/
├── CLAUDE.md                  # 项目级指引
├── CONTRIBUTING.md            # 本文档
├── .gitignore
├── frontend/                  # React + Vite 前端
├── excel-agent/               # Excel 自动化 Agent（已有）
├── xxx-agent/                 # 新 Agent，结构对齐 excel-agent
└── shared/                    # 可选：多 Agent 共用的工具/配置
```

## 1. 前端规范（frontend/）

```
frontend/
├── src/
│   ├── App.tsx                # 根组件
│   ├── main.tsx               # 入口
│   ├── api/                   # 后端 API 调用封装
│   │   └── agent.ts           # Agent 相关请求
│   ├── components/            # UI 组件
│   │   ├── TaskInput.tsx      # 任务输入
│   │   ├── FileUpload.tsx     # 文件上传
│   │   ├── AgentSteps.tsx     # Agent 执行步骤展示
│   │   └── ResultPanel.tsx    # 结果面板
│   ├── types/                 # TypeScript 类型定义
│   │   └── agent.ts           # 对齐后端 schema
│   └── hooks/                 # 自定义 hooks
├── public/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
└── .env                       # VITE_API_BASE_URL 等
```

### 1.1 前端约定

- **框架**：React 18+ + TypeScript
- **构建**：Vite
- **API 通信**：通过 `src/api/` 封装 fetch/axios，不直接在组件中调用
- **类型定义**：`src/types/` 必须与后端 `agent_schema.py` 对齐
- **环境变量**：`VITE_` 前缀，如 `VITE_API_BASE_URL=http://localhost:8000`
- **不硬编码后端地址**：通过 `.env` 配置

### 1.2 前端必须实现的功能

| 功能 | 说明 |
|------|------|
| 任务输入 | 用户输入自然语言 task |
| 文件上传 | 上传文件到后端 `/api/files/upload` |
| 执行任务 | 调用 `/api/agent/run`，展示执行步骤 |
| 结果展示 | 显示 Agent 最终回答、输出文件下载 |
| 工具列表 | 可选：展示当前 Agent 可用的 MCP 工具 |

## 2. 后端 Agent 规范（xxx-agent/）

每个 Agent 是一个独立顶层目录，命名格式 `{功能}-agent`：

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

### 2.1 后端技术栈

| 项目 | 要求 |
|------|------|
| Python | 3.11+ |
| 包管理 | uv |
| Web 框架 | FastAPI |
| Agent 框架 | LangGraph `create_react_agent` |
| LLM | `langchain-openai` ChatOpenAI（OpenAI-compatible） |
| MCP Client | `mcp` Python SDK（stdio transport） |
| 短期记忆 | Redis |
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
  "session_id": "sess_001",
  "task": "帮我读取这个文件",
  "file_path": "uploads/file.xlsx"
}
```

响应：
```json
{
  "session_id": "sess_001",
  "answer": "我读取了文件，共有 3 个 sheet...",
  "steps": [
    {"type": "tool_call", "title": "read_data_from_excel", "content": "...", "tool_name": "read_data_from_excel", "arguments": {"filepath": "..."}, "status": "success"}
  ],
  "output_file": null,
  "history_count": 0
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
    mcp_xxx_args: str = "xxx-mcp-server,stdio"
    mcp_xxx_env: dict[str, str] = {}

    # Redis（短期记忆）
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    redis_memory_ttl: int = 7200
    redis_max_messages: int = 20

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
```

`.env.example` 必须包含：

```
MODEL_NAME=
MODEL_API_KEY=
MODEL_BASE_URL=
MCP_XXX_COMMAND=
MCP_XXX_ARGS=
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_MEMORY_TTL=7200
REDIS_MAX_MESSAGES=20
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

### 2.7 Redis 短期记忆

`agent_service.py` 必须支持 Redis 会话记忆：

```python
async def run_agent(req: AgentRunRequest) -> AgentRunResponse:
    # 1. 从 Redis 读取历史 messages
    # 2. 拼入当前用户消息
    # 3. 调 agent.ainvoke({"messages": history + [user_msg]})
    # 4. 将新 messages 写回 Redis
    # 5. 返回 answer + steps
```

- `session_id` 缺失时自动生成
- 历史消息按 `redis_max_messages` 截断
- 过期时间按 `redis_memory_ttl` 设置

### 2.8 FastAPI 生命周期

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
| 前端硬编码后端地址 | 必须通过 `.env` 配置 `VITE_API_BASE_URL` |

## 4. 依赖要求

### Python（`pyproject.toml`）

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
    "redis>=5.0.0",
]
```

### Node.js（`frontend/package.json`）

```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "typescript": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0"
  }
}
```

## 5. README 要求

每个 Agent 的 `README.md` 必须包含：

1. 功能简介
2. 架构图（FastAPI → AgentService → create_react_agent → MCP tools → MCP Server）
3. 前置条件（Python、Node.js、Redis、uv）
4. 安装步骤（`uv sync`、`npm install`）
5. 配置说明（`.env` 字段）
6. 启动命令（后端 `uvicorn`、前端 `npm run dev`）
7. API 接口及 curl 示例
8. 注意事项

## 6. 验收清单

新增 Agent 合入前，确认以下全部通过：

- [ ] 目录结构符合规范
- [ ] 后端技术栈符合规范（Python + FastAPI + LangGraph + MCP + Redis）
- [ ] 前端技术栈符合规范（React + Vite + TypeScript）
- [ ] API 接口符合规范（`/health`、`/api/agent/run`、`/api/agent/tools`）
- [ ] 响应格式符合规范（包含 `steps`、`output_file`、`history_count`）
- [ ] 配置通过 pydantic-settings + .env
- [ ] Agent 使用 `create_react_agent`，无关键词规则
- [ ] MCP Client 实现 `connect`/`disconnect`/`list_tools`/`call_tool`
- [ ] Redis 短期记忆正常工作
- [ ] MCP 连接失败或 API key 缺失时服务不崩溃
- [ ] 代码中无 pandas/openpyxl 直接使用
- [ ] 代码中无自定义业务工具逻辑
- [ ] 路径经过安全校验
- [ ] 前端不硬编码后端地址
- [ ] README 完整
- [ ] `uv sync` 可安装依赖
- [ ] `uvicorn app.main:app` 可启动
