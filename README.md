# Novel Agent MVP

一个辅助创作小说单章的 Agent MVP。系统不会替用户决定重大剧情，而是在写作前提问、检索项目设定、生成章节大纲、生成正文、润色并做一致性检查。

## 技术栈

- Backend: Python 3.11+, FastAPI, SQLAlchemy, SQLite, LangGraph, LlamaIndex, Pydantic, Uvicorn
- Frontend: Vite, Vue 3, TypeScript, Pinia, Vue Router, Axios
- RAG: 本地 LlamaIndex 索引，持久化在 `backend/storage/indexes/{project_id}/`
- LLM: 默认 OpenAI API 风格接口；没有 API key 时自动使用 Mock，方便跑通闭环

## 环境变量

复制 `backend/.env.example` 为 `backend/.env`，按需填写：

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
LLM_PROVIDER=auto
DATABASE_URL=sqlite:///./storage/novel_agent.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
APP_LOG_LEVEL=INFO
APP_LOG_TO_FILE=true
APP_LOG_FILE=./storage/logs/app.log
```

`LLM_PROVIDER=auto` 时，如果没有 `OPENAI_API_KEY` 会使用 Mock Provider；设置 key 后会调用 OpenAI 风格 `/chat/completions` 接口。

## 安装和启动

后端：

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

后端启动后访问：

```text
http://localhost:8000/api/health
```

前端：

```powershell
cd frontend
npm install
npm run dev
```

前端默认访问：

```text
http://localhost:5173
```

如果 8000 或 5173 已被占用，可以改端口启动：

```powershell
cd backend
uv run uvicorn app.main:app --reload --port 8001

cd ../frontend
$env:VITE_API_PROXY_TARGET="http://localhost:8001"
npm run dev -- --port 5174
```

SQLite 表会在后端启动时自动创建，不需要手动迁移。

## 日志

后端会输出应用日志到控制台，并在 `APP_LOG_TO_FILE=true` 时写入：

```text
backend/storage/logs/app.log
```

日志默认不记录完整 prompt、模型响应正文或 API key，只记录 provider、model、耗时、输入/输出长度、Agent 阶段、RAG 命中数量和 API 请求耗时。调试时可以调整：

```env
APP_LOG_LEVEL=INFO
APP_LOG_TO_FILE=true
APP_LOG_FILE=./storage/logs/app.log
```

## MVP 使用流程

1. 打开前端项目列表，创建一个小说项目。
2. 进入项目详情，填写风格指南。
3. 新增人物卡、世界观设定、全局大纲、伏笔。
4. 新增一个章节，进入章节工作台。
5. 输入本章目标，点击“开始创作”。
6. 回答 Agent 提出的剧情问题。
7. 查看章节大纲，确认或填写修改要求。
8. 批准大纲后，系统生成草稿、润色稿和一致性检查报告。
9. 选择保存草稿或润色稿。

## 测试数据

项目：

```text
标题：旧港谜案
类型：都市悬疑
目标读者：成人读者
风格指南：克制、悬疑、重视细节，避免过度解释。
```

人物：

```text
姓名：林澈
角色：男主
性格：冷静但压抑，遇到妹妹相关线索会失控
目标：找到失踪的妹妹
说话风格：短句，少解释
约束：不会轻易相信陌生人
背景：前记者，因一次报道事故离职
```

世界观：

```text
标题：旧港
分类：地点
内容：废弃仓库群，夜间有人非法活动，警方记录不完整。
```

伏笔：

```text
名称：蓝色布扣
埋设：妹妹失踪前把蓝色布扣缝在书包拉链旁
回收计划：后续证明书包确实由妹妹亲手留下
状态：planned
```

章节：

```text
章节标题：线索
本章目标：本章希望男主发现妹妹失踪前留下的线索
```

## 手动验收

1. 后端 `GET /api/health` 返回 `{"ok": true}`。
2. 前端能创建项目并进入项目详情。
3. 能新增人物、世界观、大纲、伏笔和章节。
4. 章节工作台点击“开始创作”后，右侧出现 3 到 5 个剧情问题。
5. 提交回答后，中间显示章节大纲。
6. 批准大纲后，中间显示正文草稿和润色稿，右侧显示一致性检查。
7. 点击保存后，章节状态变为 `saved`，回到项目详情仍能看到章节内容。

## 主要 API

- `POST /api/agent/start-chapter`
- `POST /api/agent/answer-questions`
- `POST /api/agent/approve-outline`
- `POST /api/agent/save-chapter`
- `POST /api/projects/{project_id}/rebuild-index`

普通 CRUD 使用嵌套路由：

- `/api/projects`
- `/api/projects/{project_id}/characters`
- `/api/projects/{project_id}/worldbuilding`
- `/api/projects/{project_id}/outlines`
- `/api/projects/{project_id}/chapters`
- `/api/projects/{project_id}/foreshadowing`
