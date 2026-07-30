<script setup lang="ts">
defineProps<{ companyName: string; jobTitle: string; scoreBefore: number; scoreAfter: number; highConfidenceCount: number }>()
const emit = defineEmits<{ (e: "accept-all-high"): void; (e: "export-pdf"): void }>()
</script>

<template>
  <header class="target-header">
    <div class="header-info">
      <div class="info-top">
        <h3>{{ companyName }} <span class="separator">&#8212;</span> <span class="job-title">{{ jobTitle }}</span></h3>
      </div>
      <div class="score-row">
        <div class="score-box before">{{ scoreBefore }}<span class="score-label">Before</span></div>
        <div class="score-arrow">&#10140;</div>
        <div class="score-box after">{{ scoreAfter }}<span class="score-label">After</span></div>
        <div class="improvement-badge">+{{ scoreAfter - scoreBefore }}%</div>
      </div>
    </div>
    <div class="header-actions">
      <button class="btn-accept-all" :disabled="highConfidenceCount === 0" @click="emit('accept-all-high')">&#9889; Accept HIGH ({{ highConfidenceCount }})</button>
    </div>
  </header>
</template>

<style scoped>
.target-header { background: var(--workspace-header-bg); border-bottom: 1px solid var(--sidebar-border, #1e293b); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.info-top h3 { font-size: 15px; font-weight: 600; color: var(--text-primary, #e2e8f0); margin: 0; }
.separator { color: var(--text-muted, #64748b); }
.job-title { color: var(--text-secondary, #94a3b8); font-weight: 400; }
.score-row { display: flex; align-items: center; gap: 8px; margin-top: 6px; }
.score-box { display: flex; align-items: baseline; gap: 4px; font-size: 22px; font-weight: 800; }
.score-box.before { color: var(--accent-rose, #f43f5e); }
.score-box.after { color: var(--neon-green, #00FF66); }
.score-label { font-size: 10px; font-weight: 500; color: var(--text-muted, #64748b); }
.score-arrow { color: var(--text-muted, #64748b); font-size: 16px; }
.improvement-badge { background: rgba(0,255,102,0.12); color: var(--neon-green, #00FF66); padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 700; }
.header-actions { flex-shrink: 0; }
.btn-accept-all { background: linear-gradient(to right, #059669, #10b981); color: white; font-weight: 700; border: none; border-radius: 6px; padding: 6px 14px; font-size: 13px; cursor: pointer; }
.btn-accept-all:hover { filter: brightness(1.1); }
.btn-accept-all:disabled { background: var(--card-bg, #1e293b); color: var(--text-muted, #64748b); cursor: not-allowed; }
</style>
