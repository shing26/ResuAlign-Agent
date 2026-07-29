# 01 — Directory Restructure (Wide Refactor)

**What to build:** 将 backend/resume_align/ 下散落的文件按 6 层职责布局重新组织: api/v1/, core/, domain/, services/, infra/, shield/。所有内部 import 路径同步更新, 旧文件删除。纯机械性重构, 不改业务逻辑。

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] 创建 6 层目录结构 + 所需 __init__.py
- [ ] git mv 移动文件到新路径 (保留 git history)
- [ ] 更新所有内部 Python import 路径
- [ ] 删除旧路径下的所有源文件 (保留备份确认)
- [ ] pytest -q 13/13 通过
- [ ] uvicorn 启动无报错
