<script setup lang="ts">
import type { JobTarget } from "../types/diff"
defineProps<{ targets: JobTarget[]; activeTargetId: string }>()
const emit = defineEmits<{ (e: "select-target", id: string): void; (e: "create-target"): void; (e: "upload-resume"): void; (e: "open-settings"): void }>()
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo-row">
        <span class="logo-icon">&#9889;</span>
        <h2>ResuAlign <span class="version-badge">v1.0</span></h2>
      </div>
      <button class="btn-new-target" @click="emit('create-target')">+ &#26032;&#24314;&#23703;&#20301;&#25237;&#36882;</button>
    </div>
    <div class="targets-list">
      <div class="targets-count">&#25237;&#36882;&#30446;&#26631;&#30475;&#26495; ({{ targets.length }})</div>
      <div v-for="t in targets" :key="t.id" class="target-card" :class="{ active: t.id === activeTargetId }" @click="emit('select-target', t.id)">
        <div class="target-company">{{ t.companyName }}</div>
        <div class="target-title">{{ t.jobTitle }}</div>
        <div class="target-footer">
          <div class="score-pill"><span class="score-old">{{ t.matchScoreBefore }}</span> <span class="score-arrow">&#10140;</span> <span class="score-new">{{ t.matchScoreAfter }}&#20998;</span></div>
          <span class="status-dot" :class="t.status"></span>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar { width: 270px; background: #0b0f19; border-right: 1px solid #1e293b; height: 100vh; display: flex; flex-direction: column; padding: 16px; }
.sidebar-header { margin-bottom: 24px; }
.logo-row { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.logo-icon { font-size: 20px; }
.logo-row h2 { color: #f1f5f9; font-weight: 700; font-size: 16px; margin: 0; }
.version-badge { font-size: 11px; background: rgba(56,189,248,0.1); color: #38bdf8; padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(56,189,248,0.2); }
.btn-new-target { width: 100%; padding: 8px 12px; background: linear-gradient(to right, #2563eb, #1d4ed8); color: white; font-weight: 600; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; display: flex; align-items: center; justify-content: center; gap: 4px; transition: all 0.2s; }
.btn-sidebar { width: 100%; padding: 6px 12px; background: #0f172a; color: #94a3b8; border: 1px solid #334155; border-radius: 6px; cursor: pointer; font-size: 12px; margin-top: 6px; transition: all 0.2s; }
.btn-sidebar:hover { background: #1e293b; color: #f1f5f9; }
.btn-new-target:hover { background: linear-gradient(to right, #3b82f6, #2563eb); }
.targets-list { flex: 1; overflow-y: auto; }
.targets-count { color: #64748b; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 12px; }
.target-card { padding: 12px; border-radius: 8px; border: 1px solid rgba(51,65,85,0.5); cursor: pointer; margin-bottom: 8px; transition: all 0.2s; background: rgba(30,41,59,0.2); }
.target-card:hover { background: #1e293b; border-color: #475569; }
.target-card.active { background: #1e293b; border-color: #38bdf8; box-shadow: 0 0 12px rgba(56,189,248,0.15); }
.target-company { font-weight: 600; color: #f1f5f9; font-size: 14px; }
.target-title { color: #94a3b8; font-size: 12px; margin-top: 2px; }
.target-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.score-pill { background: #0f172a; padding: 1px 8px; border-radius: 50px; font-size: 11px; color: #94a3b8; display: flex; align-items: center; gap: 4px; }
.score-old { text-decoration: line-through; color: #f43f5e; }
.score-arrow { color: #64748b; }
.score-new { color: #34d399; font-weight: 700; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.draft { background: #64748b; }
.status-dot.analyzed { background: #10b981; box-shadow: 0 0 6px #10b981; }
.status-dot.applied { background: #38bdf8; }
</style>