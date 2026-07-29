# ResuAlign-Agent: 重构规格书 (Specification)

## 元信息
- 状态: 已批准, 待实现
- 优先级: P0
- 影响范围: 后端全量 + 前端 store

---

## 第一期：功能链路重构 (P0)

### 1.1 目录结构重构

#### 操作
将现有后端文件按 6 层布局重新组织:

| 新路径 | 操作 | 旧路径 |
|--------|------|--------|
| api/v1/resume.py | 新建 | api/routes.py (抽出 parse-pdf) |
| api/v1/tailor.py | 新建 | api/routes.py (抽出 tailor) |
| api/v1/session.py | 新建 | api/routes.py (抽出 session) |
| api/schemas.py | 保留 | api/schemas.py |
| api/__init__.py | 新建 | - |
| api/v1/__init__.py | 新建 | - |
| core/config.py | 移动 | config.py |
| core/pipeline.py | 移动 | pipeline.py |
| core/session_store.py | 移动 | session_store.py |
| core/__init__.py | 新建 | - |
| domain/diff.py | 移动 + 维持 | models/diff.py |
| domain/resume.py | 移动 (仅 Pydantic 部分) | models/resume.py (ResumeContext) |
| domain/job.py | 移动 (仅 Pydantic 部分) | models/job.py (JobContext) |
| domain/__init__.py | 新建 | - |
| services/agents/ | 移动 | agents/ |
| services/parsers/ | 移动 | parsers/ |
| services/__init__.py | 新建 | - |
| infra/llm/ | 移动 | llm/ |
| infra/redis_cache.py | 移动 | shield/redis_cache.py |
| infra/rate_limiter.py | 移动 | shield/rate_limiter.py |
| infra/__init__.py | 新建 | - |
| shield/assertion_checker.py | 保留 | shield/assertion_checker.py |
| shield/__init__.py | 新建 | - |
| mcp/server.py | 保留 | mcp/server.py |
| main.py | 保留 | main.py (更新导入路径) |

#### 关键约束
- 所有内部 import 路径必须同步更新 (from agents.tailor → from services.agents.tailor)
- 迁移后 python -m pytest tests/ -q 必须 13/13 通过
- 旧文件在迁移完成后删除, 不留副本

### 1.2 API 端点清理

#### 保留 (4 个)
| 端点 | Schema | 说明 |
|------|--------|------|
| POST /api/v1/resume/parse-pdf | UploadFile → {"raw_text", "sections", "md5"} | PDF → Markdown |
| POST /api/v1/tailor | TailorRequest → {"diagnostic", "diff_delta", ...} | Base Resume + JD → DiffDelta |
| POST /api/v1/session/configure | SessionConfigRequest → SessionConfigResponse | 设置 API Key/Model |
| POST /api/v1/session/test | SessionTestRequest → {"ok", "msg"} | 校验连通性 |

#### TailorRequest 字段补充
`python
class TailorRequest(BaseModel):
    resume_text: str
    job_text: str
    company_name: str = ""
    job_title: str = ""
    # 新增: Settings → API 链路
    api_key: str | None = None
    model: str | None = None
    base_url: str | None = None
    provider: str | None = None
`

#### 裁撤 (4 个)
| 端点 | 文件 | 操作 |
|------|------|------|
| POST /analyze | api/routes.py | 删除 |
| POST /analyze/stream | api/routes.py | 删除 |
| POST /analyze/upload | api/routes.py | 删除 |
| GET /analyze/{id}/stream | api/routes.py | 删除 |

**routes.py 完成迁移后删除整个文件** (不再有单文件路由)。

### 1.3 Settings → API 链路打通

#### 后端改动
1. TailorRequest 增加 pi_key / model / ase_url / provider 字段
2. /tailor 端点收到请求后: 若 pi_key 非空, 用传入参数创建 LLM Client, 否则回退 session_store 或 .env

#### 前端改动
1. 	ailorStore.settings 作为配置唯一真理源
2. Store 初始化时从 sessionStorage 加载 settings
3. Store 监听 settings 变更, 自动写回 sessionStorage
4. SettingsPanel 改为读写 store.settings, 不再直接接触 sessionStorage
5. createTargetAndAnalyze 读取 store.settings, 传入 /tailor 请求

#### 数据流
`
SettingsPanel → store.settings = { apiKey, model, baseUrl, provider }
       ↓
store 自动同步到 sessionStorage (持久化)
       ↓
createTargetAndAnalyze → POST /tailor { ..., apiKey, model, baseUrl, provider }
       ↓
后端 TailorRequest.api_key 非空 → LLM Client 用传入 Key
`

---

## 第二期：前端 UI 打磨 (P1, 待排期)

### 2.1 CyberTerminalHero 风格
- CyberTerminalHero.vue 作为新建的 Landing 或 Header 组件
- 网格背景、霓虹发光边框、终端打字机效果

### 2.2 DiffCard 视觉升级
- 现有 DiffCard.vue 已经存在, 待融合 Cyber 设计语言
- 发光边框、动画悬浮效果

### 2.3 LivePreview 增强
- 高保真 Markdown 渲染 (非 <pre>)
- 复制 + PDF 导出按钮

### 2.4 响应式布局
- 三栏布局在窄屏下的折叠/展开行为
- 移动端适配

---

## 验收标准 (第一期)

| 检查项 | 验证方法 |
|--------|----------|
| 目录结构已重构 | 	ree backend/resume_align 显示 6 层结构 |
| 路由精简到 4 个 | curl /api/v1/resume/parse-pdf 返回 JSON |
| Settings → API 链路打通 | 设 Key → 调 tailor → 日志显示 Key 已被使用 |
| store.settings 持久化 | 刷新页面后 settings 从 sessionStorage 恢复 |
| 13 个测试全部通过 | pytest -q 输出 13 passed |
