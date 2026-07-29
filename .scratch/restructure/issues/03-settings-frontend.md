# 03 — Settings → API Frontend Chain

**What to build:** 打通 SettingsPanel → store.settings → /tailor 请求的完整前端链路。用户在前端设完 API Key 后, 点击分析时该 Key 确实被发送到后端并被使用。

**Blocked by:** None — frontend only, parallel with #01.

**Status:** ready-for-agent

- [ ] tailorStore.settings 作为配置唯一真理源: apiKey, model, baseUrl, provider
- [ ] Store 初始化时从 localStorage 加载 settings (持久化)
- [ ] Store 监听 settings 变更, 自动写回 localStorage (watcher)
- [ ] SettingsPanel 改为读写 store.settings, 不再直接操作 localStorage/sessionStorage
- [ ] createTargetAndAnalyze() 读取 store.settings, 传入 /tailor 请求的 JSON body
- [ ] DevTools Network 抓包: /tailor 的 Payload 包含 apiKey / model / baseUrl / provider
