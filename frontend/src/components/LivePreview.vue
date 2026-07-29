<script setup lang="ts">
import { computed } from "vue"
import { marked } from "marked"

const props = defineProps({ content: String, resumeText: String })
const text = computed(() => props.content || props.resumeText || "")
const rendered = computed(() => { try { return String(marked.parse(text.value)) } catch { return "<pre>" + text.value + "</pre>" } })

function copyText() { if (text.value) navigator.clipboard.writeText(text.value) }
</script>

<template>
  <aside class="preview-pane">
    <div class="pane-header"><h3>Final Resume</h3><button class="btn-ghost" @click="copyText">Copy</button></div>
    <div class="pane-body" v-html="rendered"></div>
  </aside>
</template>

<style scoped>
.preview-pane { width: 350px; background: #0b0f19; border-left: 1px solid #1e293b; display: flex; flex-direction: column; }
.pane-header { display: flex; justify-content: space-between; align-items: center; padding: 16px; border-bottom: 1px solid #1e293b; }
.pane-header h3 { font-size: 14px; font-weight: 600; color: #38bdf8; margin: 0; }
.btn-ghost { background: none; border: 1px solid #334155; color: #94a3b8; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; }
.btn-ghost:hover { border-color: #38bdf8; color: #38bdf8; }
.pane-body { flex: 1; padding: 20px; overflow-y: auto; font-size: 14px; line-height: 1.7; color: #cbd5e1; }
.pane-body :deep(h1) { font-size: 22px; font-weight: 700; color: #f1f5f9; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 16px; }
.pane-body :deep(h2) { font-size: 18px; font-weight: 600; color: #38bdf8; margin-top: 20px; margin-bottom: 8px; }
.pane-body :deep(h3) { font-size: 15px; font-weight: 600; color: #94a3b8; margin-top: 16px; margin-bottom: 6px; }
.pane-body :deep(ul) { padding-left: 20px; list-style: disc; }
.pane-body :deep(li) { margin-bottom: 4px; }
.pane-body :deep(strong) { color: #f1f5f9; }
.pane-body :deep(code) { background: #1e293b; padding: 2px 6px; border-radius: 4px; font-size: 13px; color: #38bdf8; font-family: monospace; }
.pane-body :deep(pre) { background: #1e293b; padding: 12px; border-radius: 8px; overflow-x: auto; border: 1px solid #334155; }
.pane-body :deep(pre code) { background: none; padding: 0; }
</style>
