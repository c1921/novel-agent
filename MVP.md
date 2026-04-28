你是一个资深全栈工程师，请帮我开发一个“辅助创作小说的 Agent MVP”。

技术栈要求：

后端：
- Python 3.11+
- FastAPI
- LangGraph
- LlamaIndex
- SQLite
- Chroma 或本地向量存储
- Pydantic
- Uvicorn

前端：
- Vite
- Vue 3
- TypeScript
- Pinia
- Vue Router
- Axios
- 简洁但可用的 UI，不要求精美

目标：
开发一个最小可运行的小说创作 Agent。它不是自动替用户决定剧情，而是作为“创作副驾驶”，通过提问、检索设定、生成大纲、生成正文、润色和一致性检查，辅助用户完成单章创作。

核心原则：
1. 用户拥有剧情决策权。
2. Agent 在遇到重大剧情走向时必须向用户提问。
3. 未经用户确认，不得擅自改变主线剧情、人物关系、核心设定。
4. Agent 可以自动处理不影响主线的小细节，例如环境描写、动作衔接、路人对白。
5. MVP 的重点是完成“写一章”的闭环，而不是自动写完整本小说。

请你实现一个 monorepo 项目结构：

novel-agent-mvp/
  backend/
    app/
      main.py
      config.py
      database.py
      models.py
      schemas.py
      crud.py
      rag/
        indexer.py
        retriever.py
      agent/
        state.py
        graph.py
        prompts.py
        nodes.py
      api/
        projects.py
        characters.py
        worldbuilding.py
        outlines.py
        chapters.py
        agent.py
    requirements.txt
    README.md
  frontend/
    index.html
    package.json
    vite.config.ts
    tsconfig.json
    src/
      main.ts
      App.vue
      router/
        index.ts
      stores/
        projectStore.ts
      api/
        client.ts
        projects.ts
        agent.ts
      views/
        ProjectListView.vue
        ProjectDetailView.vue
        ChapterWorkspaceView.vue
      components/
        ProjectForm.vue
        CharacterEditor.vue
        WorldSettingEditor.vue
        ChapterEditor.vue
        AgentPanel.vue
        QuestionCard.vue
        ConsistencyReport.vue
  README.md

后端功能要求：

一、数据模型

请用 SQLAlchemy 或 SQLModel 实现以下核心数据表：

Project:
- id
- title
- genre
- target_audience
- style_guide
- created_at
- updated_at

Character:
- id
- project_id
- name
- role
- personality
- goal
- speech_style
- constraints
- background

WorldSetting:
- id
- project_id
- title
- content
- category

Outline:
- id
- project_id
- title
- content

Chapter:
- id
- project_id
- chapter_number
- title
- goal
- outline
- draft
- polished_draft
- status
- created_at
- updated_at

Foreshadowing:
- id
- project_id
- name
- setup
- payoff_plan
- status

二、RAG 知识库

用 LlamaIndex 实现一个最小知识库能力。

需要支持：
1. 将项目下的人物卡、世界观、大纲、已写章节、伏笔写入索引。
2. 给定 project_id 和当前章节目标，检索相关上下文。
3. 提供 rebuild_project_index(project_id) 方法。
4. 提供 retrieve_project_context(project_id, query) 方法。

MVP 阶段可以先使用本地持久化目录，例如：

backend/storage/indexes/{project_id}/

如果 LlamaIndex 集成复杂，可以先封装接口，并实现一个简单版本：
- 从数据库读取项目资料
- 拼接为文本
- 使用 LlamaIndex 建索引
- 查询时返回 top_k 相关片段

三、LangGraph Agent 流程

实现一个章节创作工作流，流程如下：

Start
  ↓
Load Project Context
  ↓
Retrieve Relevant Knowledge
  ↓
Generate Plot Questions
  ↓
Wait For User Answers
  ↓
Generate Chapter Outline
  ↓
Wait For Outline Approval
  ↓
Generate Draft
  ↓
Polish Draft
  ↓
Consistency Check
  ↓
Save Chapter

请把 Agent 状态定义为 Pydantic 或 TypedDict：

NovelAgentState:
- project_id
- chapter_id
- user_goal
- retrieved_context
- plot_questions
- user_answers
- chapter_outline
- outline_approved
- draft
- polished_draft
- consistency_report
- next_action
- messages

关键要求：
1. Generate Plot Questions 节点必须输出 3 到 5 个问题。
2. 问题应该围绕本章重大剧情走向。
3. 问题要区分 must_ask、optional、auto_decidable。
4. 如果存在 must_ask 问题，流程必须暂停，等待用户回答。
5. 用户回答后，才能继续生成章节大纲。
6. 章节大纲生成后，也要暂停，等待用户确认。
7. 用户确认后，才能生成正文。
8. 一致性检查要基于人物卡、世界观、前文和本章草稿。

四、Agent API

实现以下接口：

POST /api/agent/start-chapter
请求：
{
  "project_id": 1,
  "chapter_id": 1,
  "user_goal": "本章希望男主发现妹妹失踪前留下的线索"
}

返回：
{
  "session_id": "xxx",
  "next_action": "answer_plot_questions",
  "plot_questions": [...]
}

POST /api/agent/answer-questions
请求：
{
  "session_id": "xxx",
  "answers": [...]
}

返回：
{
  "next_action": "approve_outline",
  "chapter_outline": "..."
}

POST /api/agent/approve-outline
请求：
{
  "session_id": "xxx",
  "approved": true,
  "revision_instruction": ""
}

如果 approved 为 false，则根据 revision_instruction 重新生成大纲。

如果 approved 为 true，则继续生成正文、润色、一致性检查，并返回：
{
  "next_action": "review_draft",
  "draft": "...",
  "polished_draft": "...",
  "consistency_report": {...}
}

POST /api/agent/save-chapter
请求：
{
  "session_id": "xxx",
  "use_polished": true
}

返回保存后的 Chapter。

五、普通 CRUD API

实现：
- Project 创建、列表、详情、更新、删除
- Character 创建、列表、更新、删除
- WorldSetting 创建、列表、更新、删除
- Outline 创建、列表、更新、删除
- Chapter 创建、列表、详情、更新、删除
- rebuild index 接口

六、Prompt 设计

请在 backend/app/agent/prompts.py 中写清楚以下 Prompt：

1. 生成剧情问题 Prompt

要求：
- 你是小说创作副驾驶，不是剧情决策者。
- 你必须识别本章中需要用户决定的重大剧情点。
- 未经用户确认，不得决定死亡、背叛、恋爱、黑化、核心设定变化、重大伏笔揭晓、章节结尾反转。
- 输出 JSON。
- JSON 格式：

{
  "questions": [
    {
      "id": "q1",
      "type": "must_ask",
      "question": "本章结尾是否要让男主确认妹妹还活着？",
      "reason": "这会改变主线推进方向。",
      "options": [
        "确认妹妹还活着",
        "只发现疑似线索",
        "发现线索其实是误导"
      ]
    }
  ],
  "auto_decidable": [
    "天气",
    "路人对白",
    "普通动作衔接"
  ]
}

2. 生成章节大纲 Prompt

输入：
- 项目设定
- 人物卡
- 世界观
- 前文章节摘要
- 用户回答
- 本章目标

输出：
- 本章标题
- 本章目标
- 主要冲突
- 场景列表
- 情绪曲线
- 结尾钩子
- 需要埋下或回收的伏笔

3. 生成正文 Prompt

要求：
- 严格遵守用户确认的大纲。
- 不得擅自增加重大剧情反转。
- 遵守人物性格、说话风格和约束。
- 写出完整章节正文。
- 默认字数 1500 到 2500 中文字，MVP 阶段可以短一点。

4. 润色 Prompt

要求：
- 保留剧情事实不变。
- 优化节奏、描写、对话和转场。
- 不新增重大情节。
- 不改变人物关系。

5. 一致性检查 Prompt

检查：
- 人物性格是否跑偏
- 人物称呼是否一致
- 时间线是否冲突
- 世界观规则是否冲突
- 是否违反用户确认的大纲
- 是否擅自增加重大剧情
- 伏笔是否合理

输出 JSON：
{
  "summary": "整体评价",
  "issues": [
    {
      "severity": "high | medium | low",
      "type": "character | timeline | worldbuilding | plot | foreshadowing | style",
      "description": "问题描述",
      "suggestion": "修改建议"
    }
  ]
}

七、前端页面要求

1. ProjectListView
- 展示项目列表
- 创建新项目

2. ProjectDetailView
- 展示项目基本信息
- 编辑风格指南
- 管理人物卡
- 管理世界观设定
- 管理大纲
- 管理章节列表

3. ChapterWorkspaceView
页面布局：
左侧：
- 项目资料摘要
- 人物列表
- 世界观列表
- 章节列表

中间：
- 当前章节目标输入
- 章节大纲
- 正文编辑器
- 润色版本

右侧：
- AgentPanel
- Agent 提问
- 用户回答输入
- 大纲确认按钮
- 一致性检查报告

八、交互流程

用户进入章节工作台：
1. 输入本章目标。
2. 点击“开始创作”。
3. 前端调用 /api/agent/start-chapter。
4. 右侧展示 Agent 提出的问题。
5. 用户回答问题。
6. 调用 /api/agent/answer-questions。
7. 展示章节大纲。
8. 用户确认或要求修改。
9. 如果确认，调用 /api/agent/approve-outline。
10. 展示草稿、润色稿、一致性报告。
11. 用户可以选择保存草稿或润色稿。

九、LLM 接口

请设计一个可替换的 LLM Provider 封装：

backend/app/agent/llm.py

要求：
- 支持从环境变量读取模型配置。
- 默认兼容 OpenAI API 风格接口。
- 环境变量：
  - OPENAI_API_KEY
  - OPENAI_BASE_URL
  - OPENAI_MODEL
- 提供函数：
  - chat_completion(messages, temperature=0.7)
  - json_completion(messages, temperature=0.3)

不要把 API key 写死在代码里。

十、工程要求

1. 代码要能运行。
2. 给出详细 README。
3. README 包含：
   - 安装依赖
   - 配置环境变量
   - 初始化数据库
   - 启动后端
   - 启动前端
   - MVP 使用流程
4. 后端要有 CORS 配置，允许前端 localhost 访问。
5. 所有接口要有基础错误处理。
6. 前端要有 loading 和 error 状态。
7. 不需要登录系统。
8. 不需要复杂权限。
9. 不需要部署配置。
10. 优先保证 MVP 闭环跑通。

十一、不要做的功能

请不要实现：
- 用户登录
- 付费系统
- 多人协作
- 小说发布平台
- 图片生成
- 版权检测
- 自动生成整本小说
- 复杂富文本编辑器

十二、最终交付

请输出：
1. 完整项目代码。
2. 后端启动命令。
3. 前端启动命令。
4. 环境变量示例。
5. 一段测试数据。
6. 一个完整的手动测试流程。
