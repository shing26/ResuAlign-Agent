<template>
  <div class="settings-panel">
    <div class="settings-header" @click="open = !open">
      <span class="settings-icon">&#9881;</span>
      <span>{{ t("model_settings") }}</span>
      <span class="toggle-arrow">{{ open ? '&#9660;' : '&#9654;' }}</span>
    </div>

    <div v-if="open" class="settings-body">
      <div class="mode-toggle">
        <label class="radio-label">
          <input type="radio" value="simple" v-model="mode" />
          <span>{{ t("simple_mode") }}</span>
        </label>
        <label class="radio-label">
          <input type="radio" value="advanced" v-model="mode" />
          <span>{{ t("advanced_mode") }}</span>
        </label>
      </div>

      <!-- Simple Mode -->
      <div v-if="mode === 'simple'" class="stage-config">
        <div class="config-row">
          <label>{{ t("provider") }}</label>
          <select v-model="config.provider">
            <option v-for="p in providers" :key="p.value" :value="p.value">{{ tp(p.value) }}</option>
          </select>
        </div>
        <div class="config-row">
          <label>{{ t("api_key") }}</label>
          <div class="key-input">
            <input :type="showKey ? 'text' : 'password'" v-model="config.api_key" :placeholder="t('enter_api_key')" />
            <button class="btn-icon" @click="showKey = !showKey">{{ showKey ? '&#128064;' : '&#128065;' }}</button>
          </div>
        </div>
        <div class="config-row">
          <label>{{ t("model") }}</label>
          <input v-model="config.model" :placeholder="defaultModel" />
        </div>
        <div class="config-row">
          <label>{{ t("base_url") }}</label>
          <input v-model="config.base_url" :placeholder="defaultBaseUrl" />
        </div>
      </div>

      <!-- Advanced Mode -->
      <div v-if="mode === 'advanced'" class="advanced-config">
        <div v-for="(stage, key) in stages" :key="key" class="stage-card">
          <h4>{{ {jd_structurer: t("stage_jd"), diagnoser: t("stage_diag"), tailor: t("stage_tailor")}[key] }}</h4>
          <div class="config-row">
            <label>{{ t("provider") }}</label>
            <select v-model="stageConfigs[key].provider">
              <option value="">{{ t("use_default") }}</option>
              <option v-for="p in providers" :key="p.value" :value="p.value">{{ tp(p.value) }}</option>
            </select>
          </div>
          <div class="config-row" v-if="stageConfigs[key].provider">
            <label>{{ t("api_key") }}</label>
            <input type="password" v-model="stageConfigs[key].api_key" :placeholder="t('optional_override')" />
          </div>
          <div class="config-row" v-if="stageConfigs[key].provider">
            <label>{{ t("model") }}</label>
            <input v-model="stageConfigs[key].model" :placeholder="'Default for ' + stageConfigs[key].provider" />
          </div>
        </div>
      </div>

      <div class="settings-actions">
        <button class="btn btn-primary btn-sm" @click="testConnection">
          {{ testing ? t('testing') : t('test_connection') }}
        </button>
        <span v-if="testResult" :class="'test-status ' + (testResult.ok ? 'ok' : 'fail')">
          {{ testResult.msg }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { t, tp, setLocale } from '../i18n'

const emit = defineEmits(['config-change'])

const providers = [
  { value: 'deepseek', label: 'DeepSeek' },
  { value: 'gemini', label: 'Gemini' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'glm', label: 'GLM (Zhipu)' },
  { value: 'moonshot', label: 'Moonshot (Kimi)' },
  { value: 'openrouter', label: 'OpenRouter' },
  { value: 'ollama', label: 'Ollama (Local)' },
  { value: 'mock', label: 'Mock (Demo)' },
]

const defaultModels = {
  deepseek: 'deepseek-chat', gemini: 'gemini-2.0-flash', openai: 'gpt-4o',
  anthropic: 'claude-sonnet-4-20250514', glm: 'glm-4', moonshot: 'moonshot-v1-8k',
  openrouter: 'openai/gpt-4o', ollama: 'qwen2.5:3b',
}

const defaultUrls = {
  deepseek: 'https://api.deepseek.com', openai: 'https://api.openai.com/v1',
  glm: 'https://open.bigmodel.cn/api/paas/v4', moonshot: 'https://api.moonshot.cn/v1',
  openrouter: 'https://openrouter.ai/api/v1',
}

const stages = {
  jd_structurer: { label: t('stage_jd') },
  diagnoser: { label: t('stage_diag') },
  tailor: { label: t('stage_tailor') },
}

const open = ref(false)
const mode = ref('simple')
const showKey = ref(false)
const testing = ref(false)
const testResult = ref(null)
const sessionId = ref(sessionStorage.getItem('resualign_session') || '')
const maskedKey = ref(sessionStorage.getItem('resualign_masked') || '')

const saved = JSON.parse(localStorage.getItem('resualign_config') || 'null')

const config = ref(saved?.config || { provider: 'deepseek', api_key: '', model: '', base_url: '' })
const stageConfigs = ref(saved?.stageConfigs || Object.fromEntries(
  Object.keys(stages).map(k => [k, { provider: '', api_key: '', model: '' }])
))

const defaultModel = computed(() => defaultModels[config.value.provider] || '')
const defaultBaseUrl = computed(() => defaultUrls[config.value.provider] || '')

watch([config, stageConfigs, mode], async () => {
  if (config.value.api_key && !sessionId.value) {
    await configureSession()
  }
  emit('config-change', getActiveConfig())
}, { deep: true })

async function configureSession() {
  if (!config.value.api_key) return false
  try {
    const res = await fetch('/api/v1/session/configure', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider: config.value.provider,
        api_key: config.value.api_key,
        model: config.value.model || undefined,
        base_url: config.value.base_url || undefined,
      })
    })
    if (res.ok) {
      const data = await res.json()
      sessionId.value = data.session_id
      maskedKey.value = data.masked_key
      sessionStorage.setItem('resualign_session', data.session_id)
      sessionStorage.setItem('resualign_masked', data.masked_key)
      return true
    }
  } catch {}
  return false
}

function clearKey() {
  sessionId.value = ''
  maskedKey.value = ''
  config.value.api_key = ''
  sessionStorage.removeItem('resualign_session')
  sessionStorage.removeItem('resualign_masked')
}

function getActiveConfig() {
  if (mode.value === 'simple') {
    if (sessionId.value) {
      return { session_id: sessionId.value }
    }
    return { default: { provider: config.value.provider, api_key: config.value.api_key, model: config.value.model || defaultModels[config.value.provider], base_url: config.value.base_url || defaultUrls[config.value.provider] } }
  }
  const result = {}
  for (const [key, sc] of Object.entries(stageConfigs.value)) {
    if (sc.provider) {
      result[key] = { provider: sc.provider, api_key: sc.api_key, model: sc.model || defaultModels[sc.provider], base_url: defaultUrls[sc.provider] }
    }
  }
  return Object.keys(result).length > 0 ? result : null
}

async function testConnection() {
  testing.value = true
  testResult.value = null
  try {
    const cfg = getActiveConfig()
    const provider = cfg?.default?.provider || 'deepseek'
    const apiKey = cfg?.default?.api_key || config.value.api_key
    if (!apiKey && provider !== 'mock' && provider !== 'ollama') {
      testResult.value = { ok: false, msg: t('api_key_required') }
      return
    }
    const res = await fetch('/health')
    const data = await res.json()
    if (data.status === 'ok') {
      testResult.value = { ok: true, msg: t('backend_connected') }
    }
  } catch {
    testResult.value = { ok: false, msg: t('backend_down') }
  } finally {
    testing.value = false
  }
}

defineExpose({ getActiveConfig })
</script>

<style scoped>
.settings-panel { border: 1px solid var(--color-border); border-radius: var(--radius); margin-bottom: 16px; overflow: hidden; }
.settings-header { display: flex; align-items: center; gap: 8px; padding: 10px 16px; cursor: pointer; background: var(--color-surface); font-size: 14px; font-weight: 600; user-select: none; }
.settings-header:hover { background: var(--color-bg); }
.settings-icon { font-size: 16px; }
.toggle-arrow { margin-left: auto; font-size: 10px; }
.settings-body { padding: 12px 16px; border-top: 1px solid var(--color-border); background: var(--color-surface); }
.mode-toggle { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.radio-label { display: flex; align-items: center; gap: 6px; font-size: 13px; cursor: pointer; }
.stage-config, .advanced-config { display: flex; flex-direction: column; gap: 8px; }
.config-row { display: flex; align-items: center; gap: 8px; }
.config-row label { min-width: 72px; font-size: 12px; color: var(--color-text-secondary); }
.config-row select, .config-row input { flex: 1; padding: 6px 8px; border: 1px solid var(--color-border); border-radius: 4px; font-size: 13px; outline: none; }
.config-row select:focus, .config-row input:focus { border-color: var(--color-primary); }
.key-input { flex: 1; display: flex; gap: 4px; }
.key-masked { flex: 1; display: flex; align-items: center; gap: 6px; padding: 6px 8px; border: 1px solid var(--color-border); border-radius: 4px; background: var(--color-bg); }
.masked-dots { letter-spacing: 2px; color: var(--color-text-secondary); font-size: 12px; }
.masked-suffix { font-family: monospace; font-size: 13px; font-weight: 600; color: var(--color-primary); }
.key-input input { flex: 1; }
.btn-icon { border: 1px solid var(--color-border); border-radius: 4px; background: var(--color-bg); cursor: pointer; padding: 4px 8px; font-size: 14px; }
.stage-card { padding: 10px; border: 1px solid var(--color-border); border-radius: 6px; margin-bottom: 8px; }
.stage-card h4 { font-size: 13px; margin-bottom: 6px; color: var(--color-primary); }
.stage-card .config-row { margin-bottom: 4px; }
.settings-actions { display: flex; align-items: center; gap: 12px; margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--color-border); }
.btn-sm { padding: 4px 12px; font-size: 12px; }
.test-status { font-size: 12px; }
.test-status.ok { color: var(--color-success); }
.test-status.fail { color: var(--color-error); }
</style>
