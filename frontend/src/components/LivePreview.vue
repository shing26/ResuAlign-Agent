<script setup lang="ts">
import { ref, computed, watch } from "vue"
import { marked } from "marked"

const props = defineProps({ content: String, resumeText: String })
const text = computed(() => props.content || props.resumeText || "")
const rendered = computed(() => { try { return marked.parse(text.value) as string } catch { return "<pre>" + text.value + "</pre>" } })
const wordCount = computed(() => { const t = text.value; return t ? t.replace(/\s/g, "").length : 0 })
const zoom = ref(100)
const isFlashing = ref(false)
const zoomIn = () => { if (zoom.value < 150) zoom.value += 10 }
const zoomOut = () => { if (zoom.value > 50) zoom.value -= 10 }
function copyText() { if (text.value) navigator.clipboard.writeText(text.value) }

watch(text, () => { isFlashing.value = true; setTimeout(() => isFlashing.value = false, 1000) })
</script>

<template>
  <aside class="preview-pane">
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="tb-btn" @click="copyText">Copy MD</button>
        <span class="word-count">{{ wordCount }} chars</span>
      </div>
      <div class="toolbar-right">
        <button class="tb-btn" @click="zoomOut">-</button>
        <span class="zoom-label">{{ zoom }}%</span>
        <button class="tb-btn" @click="zoomIn">+</button>
      </div>
    </div>
    <div class="preview-scroll">
      <div class="a4-card" :style="{ transform: 'scale(' + zoom/100 + ')' }">
        <div class="a4-content" :class="{ flash: isFlashing }" v-html="rendered"></div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.preview-pane { width: var(--preview-width, 350px); background: var(--sidebar-bg, #0b0f19); border-left: 1px solid var(--sidebar-border, #1e293b); display: flex; flex-direction: column; }
.toolbar { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; border-bottom: 1px solid var(--sidebar-border, #1e293b); flex-shrink: 0; }
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 8px; }
.tb-btn { background: var(--card-bg, #1e293b); border: 1px solid var(--card-border, #1e293b); color: var(--text-secondary, #94a3b8); padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; }
.tb-btn:hover { border-color: var(--neon-cyan, #00F0FF); color: var(--neon-cyan, #00F0FF); }
.word-count { font-size: 11px; color: var(--text-muted, #64748b); }
.zoom-label { font-size: 12px; color: var(--text-secondary, #94a3b8); min-width: 36px; text-align: center; }
.preview-scroll { flex: 1; overflow-y: auto; display: flex; justify-content: center; padding: 16px; }
.a4-card { width: min(450px, 100%); aspect-ratio: 210 / 297; background: #fff; color: #1a1a2e; padding: 32px 36px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); transform-origin: top center; }
.a4-content { font-size: 14px; line-height: 1.7; }
.a4-content :deep(h1) { font-size: 20px; font-weight: 700; color: #111; border-bottom: 1px solid #ddd; padding-bottom: 6px; margin-bottom: 12px; }
.a4-content :deep(h2) { font-size: 16px; font-weight: 600; color: #333; margin-top: 16px; margin-bottom: 8px; }
.a4-content :deep(h3) { font-size: 14px; font-weight: 600; color: #555; margin-top: 12px; }
.a4-content :deep(ul) { padding-left: 18px; list-style: disc; }
.a4-content :deep(li) { margin-bottom: 3px; }
.a4-content :deep(strong) { color: #111; }
.a4-content :deep(code) { background: #f1f5f9; padding: 1px 5px; border-radius: 3px; font-size: 13px; color: #2563eb; }
.a4-content :deep(pre) { background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0; overflow-x: auto; }
@keyframes flash-green { 0% { background-color: rgba(0,255,102,0.12); } 100% { background-color: transparent; } }
.flash { animation: flash-green 0.8s ease-out; }
</style>
