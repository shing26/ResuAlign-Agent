# 02 — API Cleanup + TailorRequest Schema

**What to build:** 
1. 裁撤 4 个遗留端点 (/analyze, /analyze/stream, /analyze/upload, /analyze/{id}/stream)
2. TailorRequest 新增 4 个可选字段: api_key (Optional[str]), model (Optional[str]), base_url (Optional[str]), provider (Optional[str])
3. /tailor 端点逻辑改为: 若 request.api_key 非空则用传入参数创建 LLM Client, 否则 fallback 到 core/config.py 的全局默认配置
4. 最终保留 4 个 API 端点

**Blocked by:** #01 Directory Restructure (路径依赖)

**Status:** ready-for-agent

- [ ] 裁撤 4 个遗留端点, 删除对应代码
- [ ] TailorRequest 新增 api_key / model / base_url / provider (Optional[str])
- [ ] /tailor 端点根据 api_key 是否为空决定 LLM Client 创建策略
- [ ] /docs (Swagger) 只显示 4 个端点
- [ ] curl /api/v1/tailor 且不传 api_key → fallback 到 .env (兼容旧行为)
- [ ] curl /api/v1/tailor 且传入 api_key → 日志显示该 Key 被使用
