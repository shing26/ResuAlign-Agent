<template>
  <div class="app-layout" :class="{ 'dark-mode': isDark }">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
        <div>
          <h1>ResuAlign-Agent</h1>
          <p class="subtitle">{{ t("app_subtitle") }}</p>
        </div>
      </div>
      <div class="header-right">
        <span class="status-dot" :class="connected ? 'online' : 'offline'" :title="connected ? t('connected') : t('disconnected')"></span>
        <button class="btn-icon" @click="isDark = !isDark" :title="isDark ? 'Light mode' : 'Dark mode'">{{ isDark ? '&#127774;' : '&#127769;' }}</button>
        <button class="btn btn-lang" @click="toggleLang">{{ locale === 'en' ? '中文' : 'EN' }}</button>
      </div>
    </header>

    <!-- Main -->
    <main class="app-main">
      <aside class="sidebar">
        <!-- Settings Panel -->
        <SettingsPanel ref="settingsRef" @config-change="onConfigChange" />

        <!-- Input Panel -->
        <section class="card input-panel">
          <h2>{{ t("jd_input") }}</h2>
          <textarea v-model="jdText" :placeholder="t('jd_placeholder')" rows="6"></textarea>

          <h2>{{ t("resume") }}</h2>
          <div class="upload-zone" @drop.prevent="handleDrop" @dragover.prevent @click="triggerUpload">
            <input type="file" ref="fileInput" accept=".pdf" @change="handleFileUpload" hidden />
            <p v-if="!resumeFileName">{{ t("drop_pdf") }}</p>
            <p v-else class="file-name">{{ resumeFileName }}</p>
          </div>

          <button class="btn btn-primary" @click="analyze" :disabled="loading || !resumeFileName">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? t('processing') : t('analyze') }}
          </button>
        </section>
      </aside>

      <section class="content">
        <!-- Progress Indicator -->
        <div v-if="loading" class="card progress-card">
          <div class="stages">
            <div v-for="(stage, i) in stages" :key="stage.key" class="stage" :class="{ active: currentStage === i, done: i < currentStage }">
              <div class="stage-dot">{{ i < currentStage ? '&#10003;' : (currentStage === i ? '&#9679;' : '&#9675;') }}</div>
              <span class="stage-label">{{ stage.label }}</span>
            </div>
          </div>
          <div class="progress-bar"><div class="progress-fill" :style="{ width: ((currentStage + 1) / stages.length * 100) + '%' }"></div></div>
          <p class="stage-message">{{ stages[currentStage]?.message || '' }}</p>
        </div>

        <!-- Results -->
        <div v-if="diagnostic && !loading" class="results">
          <!-- Diagnostic Report -->
          <div class="card">
            <div class="card-header">
              <h2>{{ t("diagnostic_report") }}</h2>
              <div class="header-badges">
                <span class="badge" :class="cached ? 'badge-info' : 'badge-success'">{{ cached ? t('cached') : t('fresh') }}</span>
                <span class="badge badge-info">{{ processingTime }}ms</span>
              </div>
            </div>

            <div class="score-grid">
              <div class="score-item">
                <label>{{ t("star_label") }}</label>
                <div class="score-bar"><div class="score-fill" :style="{ width: (diagnostic.star_score * 100) + '%' }" :class="scoreClass(diagnostic.star_score)"></div></div>
                <span class="score-value">{{ (diagnostic.star_score * 100).toFixed(0) }}%</span>
              </div>
              <div class="score-item">
                <label>{{ t("quant_label") }}</label>
                <div class="score-bar"><div class="score-fill" :style="{ width: (diagnostic.quant_score * 100) + '%' }" :class="scoreClass(diagnostic.quant_score)"></div></div>
                <span class="score-value">{{ (diagnostic.quant_score * 100).toFixed(0) }}%</span>
              </div>
            </div>

            <h3>{{ t("detected_skills") }}</h3>
            <div class="tags">
              <span v-for="skill in diagnostic.skill_breadth" :key="skill" class="tag">{{ skill }}</span>
              <span v-if="!diagnostic.skill_breadth.length" class="none-text">{{ t("no_skills") }}</span>
            </div>

            <div v-if="diagnostic.issues.length" class="section">
              <h3>{{ t("issues") }} ({{ diagnostic.issues.length }})</h3>
              <ul class="issue-list">
                <li v-for="(issue, i) in diagnostic.issues.slice(0, 8)" :key="i">{{ typeof issue === 'string' ? issue : issue.message || JSON.stringify(issue) }}</li>
              </ul>
            </div>

            <div v-if="diagnostic.suggestions.length" class="section">
              <h3>{{ t("suggestions") }}</h3>
              <ul class="suggestion-list">
                <li v-for="(s, i) in diagnostic.suggestions.slice(0, 5)" :key="i">{{ s }}</li>
              </ul>
            </div>
          </div>

          <!-- Tailoring Result -->
          <div v-if="tailoring" class="card">
            <div class="card-header">
              <h2>{{ t("optimized_resume") }}</h2>
              <button class="btn btn-sm" @click="exportMarkdown">&#128196; {{ t("export_md") }}</button>
            </div>

            <div v-if="missingSkills.length" class="alert alert-warning">
              <strong>{{ t("missing_skills") }}:</strong>
              <span v-for="s in missingSkills" :key="s" class="tag missing">{{ s }}</span>
            </div>

            <div v-for="(section, i) in tailoring.tailored_sections" :key="i" class="section-block">
              <h3>{{ section.section || 'Section ' + (i+1) }}</h3>
              <pre class="tailored-content">{{ section.content }}</pre>
            </div>

            <div v-if="tailoring.full_output" class="section-block">
              <h3>{{ t("full_output") }}</h3>
              <pre class="tailored-content">{{ tailoring.full_output }}</pre>
            </div>
          </div>
        </div>

        <!-- Error -->
        <div v-if="error" class="card alert alert-error">
          <h3>{{ t("error") }}</h3>
          <p>{{ error }}</p>
          <button class="btn" @click="error = ''">{{ t("dismiss") }}</button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { t, locale, setLocale } from './i18n'
import SettingsPanel from './components/SettingsPanel.vue'

const settingsRef = ref(null)
const fileInput = ref(null)
const jdText = ref('')
const resumeFile = ref(null)
const resumeFileName = ref('')
const loading = ref(false)
const connected = ref(false)
const isDark = ref(localStorage.getItem('resualign_dark') === 'true')
const error = ref('')
const diagnostic = ref(null)
const tailoring = ref(null)
const missingSkills = ref([])
const processingTime = ref(0)
const cached = ref(false)
const currentConfig = ref(null)
const currentStage = ref(0)
const stages = [
  { key: 'parse', label: t('stage_parse'), message: t('msg_parse') },
  { key: 'diagnose', label: t('stage_diagnose'), message: t('msg_diagnose') },
  { key: 'structure', label: t('stage_structure'), message: t('msg_structure') },
  { key: 'tailor', label: t('stage_tailoring'), message: t('msg_tailoring') },
  { key: 'check', label: t('stage_check'), message: t('msg_check') },
  { key: 'done', label: t('stage_done'), message: t('msg_done') },
]

onMounted(() => {
  checkHealth()
  applyTheme()
})

function toggleLang() {
  setLocale(locale.value === 'en' ? 'zh' : 'en')
}

function applyTheme() {
  localStorage.setItem('resualign_dark', isDark.value)
  document.documentElement.style.colorScheme = isDark.value ? 'dark' : 'light'
}

function checkHealth() {
  fetch('/health').then(r => r.json()).then(d => { connected.value = d.status === 'ok' }).catch(() => { connected.value = false })
}

function handleFileUpload(event) {
  const input = event.target
  if (input.files && input.files[0]) {
    resumeFile.value = input.files[0]; resumeFileName.value = input.files[0].name
  }
}

function handleDrop(event) {
  const file = event.dataTransfer.files[0]
  if (file && file.name.endsWith('.pdf')) {
    resumeFile.value = file; resumeFileName.value = file.name
  }
}

function triggerUpload() { fileInput.value?.click() }

function onConfigChange(config) { currentConfig.value = config }

async function analyze() {
  if (!resumeFile.value) return
  loading.value = true; error.value = ''; diagnostic.value = null; tailoring.value = null; currentStage.value = 0

  try {
    const formData = new FormData()
    formData.append('file', resumeFile.value)
    if (jdText.value) formData.append('jd_text', jdText.value)

    if (currentConfig.value) {
      if (currentConfig.value.session_id) {
        formData.append('session_id', currentConfig.value.session_id)
      } else {
        const cfg = currentConfig.value
        const def = cfg.default
        if (def) {
          formData.append('provider', def.provider || '')
          formData.append('api_key', def.api_key || '')
          formData.append('model', def.model || '')
          formData.append('base_url', def.base_url || '')
        }
        for (const key of ['jd_structurer', 'diagnoser', 'tailor']) {
          if (cfg[key]) {
            formData.append(key + '_provider', cfg[key].provider || '')
            formData.append(key + '_api_key', cfg[key].api_key || '')
            formData.append(key + '_model', cfg[key].model || '')
          }
        }
      }
    }

    currentStage.value = 1
    const res = await fetch('/api/v1/analyze/upload', { method: 'POST', body: formData })

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'HTTP ' + res.status }))
      throw new Error(err.detail || 'Analysis failed')
    }

    currentStage.value = 4
    const data = await res.json()
    diagnostic.value = data.diagnostic
    tailoring.value = data.tailoring
    missingSkills.value = data.tailoring?.missing_skills || []
    processingTime.value = data.processing_time_ms
    cached.value = data.cached
    currentStage.value = 5
  } catch (err) {
    error.value = err.message
  } finally {
    setTimeout(() => { loading.value = false }, 500)
  }
}

function scoreClass(score) {
  if (score >= 0.7) return 'good'
  if (score >= 0.4) return 'warn'
  return 'bad'
}

function exportMarkdown() {
  if (!diagnostic.value) return
  let md = '# ResuAlign Diagnostic Report\n\n'
  md += '## Resume Scores\n'
  md += '- STAR Compliance: ' + (diagnostic.value.star_score * 100).toFixed(0) + '%\n'
  md += '- Quant Metrics: ' + (diagnostic.value.quant_score * 100).toFixed(0) + '%\n\n'
  md += '## Detected Skills\n' + diagnostic.value.skill_breadth.join(', ') + '\n\n'
  if (diagnostic.value.issues.length) {
    md += '## Issues\n'
    diagnostic.value.issues.forEach(i => { md += '- ' + (typeof i === 'string' ? i : i.message || JSON.stringify(i)) + '\n' })
    md += '\n'
  }
  if (tailoring.value) {
    md += '## Optimized Resume\n\n'
    tailoring.value.tailored_sections.forEach(s => {
      md += '### ' + (s.section || 'Section') + '\n' + s.content + '\n\n'
    })
    if (tailoring.value.missing_skills.length) {
      md += '## Missing Skills\n' + tailoring.value.missing_skills.join(', ') + '\n'
    }
  }
  const blob = new Blob([md], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = 'resualign-report.md'; a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.app-layout { display: flex; flex-direction: column; gap: 20px; min-height: 100vh; }

.app-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 0; border-bottom: 1px solid var(--color-border); }
.header-left { display: flex; align-items: center; gap: 12px; }
.header-left h1 { font-size: 22px; font-weight: 700; color: var(--color-primary); }
.subtitle { font-size: 12px; color: var(--color-text-secondary); }
.header-right { display: flex; align-items: center; gap: 12px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.online { background: var(--color-success); }
.status-dot.offline { background: var(--color-error); }
.btn-icon { border: 1px solid var(--color-border); border-radius: 4px; background: var(--color-surface); cursor: pointer; padding: 4px 8px; font-size: 16px; }
.btn-lang { border: 1px solid var(--color-border); border-radius: 4px; background: var(--color-primary); color: white; cursor: pointer; padding: 2px 10px; font-size: 13px; font-weight: 600; }

.app-main { display: grid; grid-template-columns: 380px 1fr; gap: 20px; align-items: start; }
@media (max-width: 860px) { .app-main { grid-template-columns: 1fr; } }

.sidebar { display: flex; flex-direction: column; gap: 16px; }
.input-panel { display: flex; flex-direction: column; gap: 12px; }
.input-panel h2 { font-size: 14px; margin-bottom: 4px; }

.upload-zone { border: 2px dashed var(--color-border); border-radius: var(--radius); padding: 24px; text-align: center; cursor: pointer; font-size: 13px; color: var(--color-text-secondary); transition: border-color 0.2s; }
.upload-zone:hover { border-color: var(--color-primary); }
.file-name { color: var(--color-primary); font-weight: 600; }

.content { display: flex; flex-direction: column; gap: 16px; }

.progress-card { padding: 16px; }
.stages { display: flex; justify-content: space-between; margin-bottom: 12px; }
.stage { display: flex; flex-direction: column; align-items: center; gap: 4px; font-size: 11px; color: var(--color-text-secondary); }
.stage.active { color: var(--color-primary); font-weight: 600; }
.stage.done { color: var(--color-success); }
.stage-dot { width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; border: 2px solid var(--color-border); }
.stage.active .stage-dot { border-color: var(--color-primary); background: var(--color-primary); color: white; }
.stage.done .stage-dot { border-color: var(--color-success); background: var(--color-success); color: white; }
.stage-label { text-align: center; }
.progress-bar { height: 4px; background: var(--color-border); border-radius: 2px; margin-bottom: 8px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 2px; background: var(--color-primary); transition: width 0.3s; }
.stage-message { font-size: 12px; color: var(--color-text-secondary); text-align: center; }

.card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.header-badges { display: flex; gap: 6px; }
.badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; }
.badge-success { background: #dcfce7; color: #16a34a; }
.badge-info { background: #e0f2fe; color: #0369a1; }

.score-grid { display: flex; gap: 20px; margin-bottom: 16px; }
.score-item { flex: 1; }
.score-item label { font-size: 12px; color: var(--color-text-secondary); }
.score-bar { height: 8px; background: var(--color-border); border-radius: 4px; margin: 4px 0; overflow: hidden; }
.score-fill { height: 100%; border-radius: 4px; transition: width 0.5s; }
.score-fill.good { background: var(--color-success); }
.score-fill.warn { background: var(--color-warning); }
.score-fill.bad { background: var(--color-error); }
.score-value { font-size: 14px; font-weight: 600; }

.section { margin: 12px 0; }
h3 { font-size: 14px; margin-bottom: 6px; }
.tags { display: flex; flex-wrap: wrap; gap: 4px; margin: 8px 0; }
.tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; background: #e0f2fe; color: #0369a1; }
.tag.missing { background: #fef2f2; color: #dc2626; }
.none-text { font-size: 12px; color: var(--color-text-secondary); font-style: italic; }

.issue-list, .suggestion-list { padding-left: 16px; font-size: 13px; }
.issue-list li { margin-bottom: 4px; color: var(--color-text-secondary); }
.suggestion-list li { margin-bottom: 4px; color: var(--color-primary); }

.alert { padding: 12px; border-radius: var(--radius); margin: 12px 0; font-size: 13px; }
.alert-warning { background: #fffbeb; border: 1px solid #fde68a; color: #92400e; }
.alert-error { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }

.section-block { margin: 12px 0; padding: 12px; background: var(--color-bg); border-radius: var(--radius); }
.tailored-content { white-space: pre-wrap; font-size: 13px; line-height: 1.6; font-family: var(--font); }

.btn-sm { padding: 4px 12px; font-size: 12px; }
.spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: white; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
