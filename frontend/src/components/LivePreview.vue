<template>
  <div class="preview-panel card">
    <div class="preview-header">
      <h3>{{ t('optimized_resume') }}</h3>
      <button class="btn btn-sm" @click="copyText">&#128203; Copy</button>
    </div>
    <div class="preview-body">
      <pre class="preview-text">{{ resumeText || t('no_content') }}</pre>
    </div>
  </div>
</template>

<script setup>
import { t } from '../i18n'
const props = defineProps({ resumeText: String })
function copyText() {
  if (props.resumeText) navigator.clipboard.writeText(props.resumeText)
}
</script>

<style scoped>
.preview-panel { position: sticky; top: 24px; display: flex; flex-direction: column; }
.preview-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.preview-header h3 { font-size: 14px; }
.preview-body { overflow-y: auto; flex: 1; max-height: calc(100vh - 200px); }
.preview-text { white-space: pre-wrap; font-size: 13px; line-height: 1.6; font-family: var(--font); color: var(--color-text); }
</style>
