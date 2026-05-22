# Excel Agent

Excel 智能自动化 Agent — 基于 Python + FastAPI + LangGraph + MCP + Redis + React。

LLM 自动决策调用 excel-mcp-server 工具，无需手动编写工具选择逻辑。前端提供 ChatGPT 风格的聊天式交互界面，支持伪流式阶段输出。

## 架构

```
React (ChatGPT-style UI)
  → FastAPI
    → AgentService
      → create_react_agent (LLM 自动选工具)
        → MCP Tool Adapter (MCP tools → LangChain tools)
          → ExcelMCPClient (stdio → excel-mcp-server)
            → excel-mcp-server (MCP Server, via uvx)
    → Redis (session 短期记忆)
```

## 前置条件

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 包管理器
- Node.js 18+ (uvx 运行 excel-mcp-server 需要)
- Redis 7+ (短期记忆)
- LLM API Key (DeepSeek / Qwen / OpenAI / 其他 OpenAI-compatible)

## 安装

### 后端

```bash
cd excel-agent
uv sync
```

### 前端

```bash
cd frontend
npm install
```

## 配置

### 后端配置

```bash
cd excel-agent
cp .env.example .env
```

编辑 `.env`，填入：

```env
# LLM (支持任何 OpenAI-compatible API)
MODEL_NAME=deepseek-chat
MODEL_API_KEY=your-api-key-here
MODEL_BASE_URL=https://api.deepseek.com

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_MEMORY_TTL=7200
REDIS_MAX_MESSAGES=20

# MCP Server
MCP_EXCEL_COMMAND=uvx
MCP_EXCEL_ARGS=excel-mcp-server,stdio
```

### 前端配置

```bash
cd frontend
cp .env.example .env
```

默认配置即可，无需修改：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## 启动

需要依次启动 Redis、后端、前端三个服务。

### 1. 启动 Redis

```bash
# 本地安装
redis-server --daemonize yes

# 或使用 Docker
docker run -d --name agent-redis -p 6379:6379 redis:7
```

验证 Redis 连接：

```bash
redis-cli ping
# 应返回 PONG
```

### 2. 启动后端

```bash
cd excel-agent
uv run uvicorn app.main:app --reload
```

启动成功后日志应显示：

```
Excel MCP client connected
Redis connected: localhost:6379/0
Excel agent created successfully
Uvicorn running on http://0.0.0.0:8000
```

### 3. 启动前端

```bash
cd frontend
npm run dev
```

访问 http://localhost:5173 即可使用。

后端 API 文档：http://localhost:8000/docs

## 使用流程

1. 打开前端页面 http://localhost:5173
2. 点击 📎 上传 Excel 文件
3. 在输入框中输入任务，例如：
   - `查看这个 Excel 有哪些 sheet，并预览前几行`
   - `按销售额降序排序，并导出结果文件`
   - `按地区统计销售额，生成汇总表`
4. 按 Enter 发送，Agent 自动选择 MCP 工具执行
5. 等待期间，聊天界面逐步展示 Agent 执行阶段（伪流式）：
   - 正在分析任务 → 正在检查文件上下文 → 正在选择 MCP 工具 → 正在执行工具调用 → 正在整理工具结果 → 正在生成最终回复
   - 每个阶段约 800ms 依次出现，当前阶段标记为"执行中..."
   - 接口返回后，伪步骤替换为真实的工具调用过程
6. 查看最终回答和结果文件下载链接

同一个页面内支持连续对话，Agent 会记住上下文。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /health | 健康检查 |
| POST | /api/files/upload | 上传 Excel 文件 |
| GET | /api/files/download/{filename} | 下载文件 |
| POST | /api/agent/run | 执行 Agent 任务 |
| GET | /api/agent/tools | 查看 MCP 可用工具 |
| GET | /api/memory/{session_id} | 查看会话记忆 |
| DELETE | /api/memory/{session_id} | 清除会话记忆 |

### 上传文件

```bash
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@/path/to/your/file.xlsx"
```

返回：

```json
{
  "file_id": "test",
  "filename": "test.xlsx",
  "file_path": "uploads/test.xlsx"
}
```

### 执行任务

```bash
curl -X POST http://localhost:8000/api/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "task": "查看有哪些sheet",
    "file_path": "uploads/test.xlsx"
  }'
```

返回：

```json
{
  "session_id": "sess_xxx",
  "answer": "该文件包含 1 个 Sheet...",
  "steps": [
    { "type": "input", "title": "用户任务", "status": "success" },
    { "type": "tool_selection", "title": "工具决策", "tool_name": "get_workbook_metadata", "status": "success" },
    { "type": "tool_result", "title": "工具执行结果", "status": "success" },
    { "type": "final", "title": "最终回答", "status": "success" }
  ],
  "output_file": null,
  "history_count": 2
}
```

### 连续对话

```bash
# 第一次请求 — 不传 session_id，后端自动生成
curl -X POST http://localhost:8000/api/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "你好，我叫 lsy"}'
# 返回 session_id: "sess_xxx"

# 第二次请求 — 携带 session_id，Agent 记住上下文
curl -X POST http://localhost:8000/api/agent/run \
  -H "Content-Type: application/json" \
  -d '{"session_id": "sess_xxx", "task": "我刚才说我叫什么？"}'
# 返回 answer: "你说你叫 lsy！"
```

## 项目结构

```
excel-agent/                  # 后端
├── app/
│   ├── main.py               # FastAPI 入口 + lifespan
│   ├── api/                  # HTTP 路由
│   │   ├── agent_api.py      # /api/agent/*
│   │   ├── file_api.py       # /api/files/*
│   │   ├── health_api.py     # /health
│   │   └── memory_api.py     # /api/memory/*
│   ├── agents/
│   │   └── agent_factory.py  # create_react_agent + System Prompt
│   ├── core/
│   │   ├── config.py         # pydantic-settings 配置
│   │   └── logger.py         # 日志
│   ├── mcp_client/
│   │   ├── excel_mcp_client.py  # stdio 连接 excel-mcp-server
│   │   └── mcp_tool_adapter.py  # MCP tools → LangChain @tool
│   ├── memory/
│   │   ├── redis_memory.py   # Redis 短期记忆 (agent:chat:{sid} / agent:state:{sid})
│   │   └── memory_manager.py # 高层记忆接口
│   ├── schemas/              # Pydantic 模型
│   ├── services/
│   │   ├── agent_service.py  # Agent 调用 + steps 提取 + 记忆读写
│   │   └── file_service.py   # 文件上传保存
│   └── utils/
│       └── path_utils.py     # 路径安全校验
├── uploads/                  # 上传文件目录
├── outputs/                  # 输出文件目录
├── .env.example
└── pyproject.toml

frontend/                     # 前端
├── src/
│   ├── App.tsx               # 状态管理 + 主逻辑
│   ├── styles.css            # ChatGPT 风格样式
│   ├── api/
│   │   └── agentApi.ts       # 后端接口封装
│   ├── components/
│   │   ├── ChatLayout.tsx    # 左右分栏布局
│   │   ├── Sidebar.tsx       # 侧边栏
│   │   ├── ChatMessages.tsx  # 消息列表
│   │   ├── ChatMessage.tsx   # 用户/Agent 消息气泡
│   │   ├── ChatInput.tsx     # 底部输入框 + 文件上传
│   │   ├── FileBadge.tsx     # 已上传文件标记
│   │   ├── AgentStepCard.tsx # Agent 执行步骤卡片
│   │   ├── DownloadButton.tsx # 结果文件下载
│   │   └── EmptyState.tsx    # 空状态引导页
│   ├── types/
│   │   └── agent.ts          # TypeScript 类型定义
│   └── utils/
│       ├── id.ts             # 消息 ID 生成
│       └── fakeSteps.ts      # 伪流式阶段输出工具函数
├── .env.example
├── vite.config.ts            # Vite + API proxy
└── package.json
```

## MCP 可用工具

后端通过 excel-mcp-server 提供 25 个 Excel 操作工具，LLM 自动选择：

| 分类 | 工具 |
|------|------|
| 读写 | read_data_from_excel, write_data_to_excel |
| 工作簿 | create_workbook, get_workbook_metadata |
| 工作表 | create_worksheet, copy_worksheet, delete_worksheet, rename_worksheet |
| 公式 | apply_formula, validate_formula_syntax |
| 格式 | format_range, merge_cells, unmerge_cells, get_merged_cells |
| 范围 | copy_range, delete_range, validate_excel_range |
| 行列 | insert_rows, insert_columns, delete_sheet_rows, delete_sheet_columns |
| 分析 | create_chart, create_pivot_table, create_table |
| 验证 | get_data_validation_info |

## 注意事项

- 所有 Excel 操作通过 MCP Client → excel-mcp-server，不使用 pandas/openpyxl
- 工具选择由 LLM 自动决策，不使用关键词 if/else 规则
- Redis 短期记忆只依赖 session_id，不使用 user_id/anonymous_id
- 文件路径限制在项目目录内，防止任意文件访问
- Redis 异常降级为空历史，不阻塞 Agent 主流程
- 前端仅展示公开的 Agent 执行过程，不暴露思维链、系统 Prompt 或 API Key
- 前端伪流式输出：等待后端响应期间逐步展示执行阶段，接口返回后替换为真实步骤
- 不使用 SSE / WebSocket，伪流式纯前端 setInterval 实现
