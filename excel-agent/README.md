# Excel Agent

Excel 智能自动化 Agent — 基于 Python + FastAPI + LangGraph + MCP。

## 架构

```
FastAPI
  ↓
AgentService
  ↓
LangGraph (planner_node → mcp_tool_node → response_node)
  ↓
MCP Tool Adapter
  ↓
excel-mcp-server (MCP Server)
  ↓
Excel 文件
```

## 前置条件

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 包管理器
- Node.js 18+ (用于运行 excel-mcp-server)
- npm / npx

## 安装

```bash
cd excel-agent
uv sync
```

## 启动

### 1. 安装 excel-mcp-server

```bash
npm install -g excel-mcp-server
```

或直接使用 npx 运行（默认配置已使用 npx，无需全局安装）。

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY 等配置
```

### 3. 启动 FastAPI 服务

```bash
uv run uvicorn app.main:app --reload
```

服务启动后访问 http://localhost:8000/docs 查看 API 文档。

## API 接口

| 方法   | 路径                | 说明              |
|--------|---------------------|-------------------|
| GET    | /health             | 健康检查          |
| POST   | /api/files/upload   | 上传 Excel 文件   |
| POST   | /api/agent/run      | 执行 Agent 任务   |

### 上传文件

```bash
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@/path/to/your/file.xlsx"
```

### 执行任务

```bash
curl -X POST http://localhost:8000/api/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "读取第一个sheet的所有数据", "file_path": "uploads/file.xlsx"}'
```

## 项目结构

```
excel-agent/
├── app/
│   ├── main.py              # FastAPI 入口 + lifespan
│   ├── api/                  # HTTP 路由
│   ├── core/                 # 配置、日志
│   ├── schemas/              # Pydantic 模型
│   ├── services/             # 业务逻辑
│   ├── agents/               # LangGraph 图、节点、状态
│   ├── mcp_client/           # MCP Client + Tool Adapter
│   └── utils/                # 工具函数
├── data/                     # 数据目录
├── uploads/                  # 上传文件目录
├── outputs/                  # 输出文件目录
├── tests/                    # 测试
├── pyproject.toml
├── .env.example
└── README.md
```

## 注意事项

- 所有 Excel 操作通过 MCP Client 调用 excel-mcp-server，不使用 pandas/openpyxl
- 文件路径限制在项目目录内，防止任意文件访问
- uploads/ 和 outputs/ 目录需有读写权限
