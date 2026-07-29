# ResuAlign-Agent: Architecture Context

## 核心价值
解决 AI 润色简历时的"造假"问题与"海投对齐"效率问题, 让求职者安全、精准、高效地生成 ATS 定制简历。

## 四阶段工作流
| 阶段 | 名称 | 输入 | 输出 | 关键模块 |
|------|------|------|------|----------|
| 一 | 真理源就绪 | PDF 简历 | Base Resume (结构化文本) | pdf_parser → ResumeContext |
| 二 | AI 靶向生成 | Base Resume + JD | DiffDelta (结构化增量包) | Diagnoser + Tailor + Assertion Shield |
| 三 | 人机交互审阅 | DiffDelta | Accepted Diff 集合 | 前端 DiffCard + Pinia 替换引擎 |
| 四 | 交付与海投 | Base + Accepted Diffs | 定制简历 (Markdown 导出) | LivePreview + 导出模块 |
## 组件边界决策 (2026-07-29)

### 1. JobTargetSidebar
- 视觉上: 保持单侧边栏布局
- 代码上: 内部拆分为子组件 (UploadPanel, TargetList, SidebarFooter)
- emit 事件向上冒泡, 不在子组件中直接操作 store

### 2. DiffCard ↔ LivePreview
- 保持现状: 极其清晰的单向数据流
- DiffCard: 显示单条 DiffItem, emit accept/toggle
- LivePreview: 读取 store.finalResumeText, 纯展示
- 中间由 Pinia 的 finalResumeText getter 做字符串替换

### 3. SettingsPanel ↔ tailorStore.settings
- 配置的唯一真理源: Pinia tailorStore.settings
- sessionStorage: 仅仅是持久化适配器, 不直接读写
- SettingsPanel 必须通过 store.settings 读写配置
- store 负责在初始化时从 sessionStorage 加载, 并在 settings 变更时同步回 sessionStorage
## 数据流修复决策 (2026-07-29)

### 1. 简历解析反馈
- Base Resume 加载成功后, 侧边栏显示: "已加载主简历 (N 字符 / M 个段落)"
- 支持点击展开查看原始 Markdown 内容

### 2. Settings → API Key 链路
- SettingsPanel → 写入 store.settings
- store.settings 变更 → 自动同步到 sessionStorage (持久化)
- createTargetAndAnalyze → 读取 store.settings → 传入 /tailor 请求
- /tailor 端点接收 api_key / model / base_url 参数 → 用传入配置创建 LLM Client
- 端到端: SettingsPanel → store → API → LLM Client, 不再读 .env

### 3. 当前问题根因
- store.settings 存在但从未被写入 (SettingsPanel 直接读写 sessionStorage)
- TailorRequest schema 缺少 api_key / model / base_url 字段
- LLM Client 的 create_llm_client() 缺少显示的 api_key 参数透传
## API 端点决策 (2026-07-29)

### 保留 (4 个)
| 端点 | 阶段 | 说明 |
|------|------|------|
| POST /api/v1/resume/parse-pdf | 一 | PDF → Markdown |
| POST /api/v1/tailor | 二 | Base Resume + JD → DiffDelta |
| POST /api/v1/session/configure | 系统 | 设置 API Key / Model / Base URL |
| POST /api/v1/session/test | 系统 | 校验连通性 |

### 裁撤 (4 个)
| 端点 | 原因 |
|------|------|
| POST /analyze | 旧架构, DiffDelta 替代 |
| POST /analyze/stream | 旧架构, 不再需要流式 |
| POST /analyze/upload | 旧架构, parse-pdf + tailor 替代 |
| GET /analyze/{id}/stream | 旧架构 SSE stub |

## 目录结构决策 (2026-07-29)

| 新路径 | 旧路径 | 职责 |
|--------|--------|------|
| api/v1/resume.py | api/routes.py (部分) | 简历解析 |
| api/v1/tailor.py | api/routes.py (部分) | 对齐 |
| api/v1/session.py | api/routes.py (部分) | 会话管理 |
| api/schemas.py | api/schemas.py | Pydantic 模型 (不拆分) |
| core/pipeline.py | pipeline.py | 编排引擎 |
| core/config.py | config.py | 环境配置 |
| core/session_store.py | session_store.py | LLM 配置存储 |
| domain/diff.py | models/diff.py | DiffDelta 模型 |
| domain/resume.py | models/resume.py (Pydantic 部分) | ResumeContext |
| domain/job.py | models/job.py (Pydantic 部分) | JobContext |
| services/agents/ | agents/ | Agent 逻辑 |
| services/parsers/ | parsers/ | 解析器 |
| infra/llm/ | llm/ | LLM Client |
| infra/redis_cache.py | shield/redis_cache.py | 缓存 |
| infra/rate_limiter.py | shield/rate_limiter.py | 限流 |
| shield/assertion_checker.py | shield/assertion_checker.py | 反幻觉断言 |
| mcp/server.py | mcp/server.py | MCP 集成 |
