<script setup lang="ts">
import { ref } from "vue"
import { useTailorStore } from "./stores/tailorStore"
import JobTargetSidebar from "./components/JobTargetSidebar.vue"
import TargetHeader from "./components/TargetHeader.vue"
import DiffCard from "./components/DiffCard.vue"
import CreateTargetModal from "./components/CreateTargetModal.vue"
const store = useTailorStore()
const isModalOpen = ref(false)
async function handleCreateTarget(p: { companyName: string; jobTitle: string; jobText: string }) {
  isModalOpen.value = false
  await store.createTargetAndAnalyze(p.companyName, p.jobTitle, p.jobText)
}
function handleExportPDF() {
  if (store.finalResumeText) { navigator.clipboard.writeText(store.finalResumeText); alert("Copied to clipboard!") }
  else alert("No content to export")
}
</script>
<template>
  <div class="app-root">
    <JobTargetSidebar :targets="store.targets" :active-target-id="store.activeTargetId" @select-target="store.setActiveTarget" @create-target="isModalOpen = true" />
    <main class="workspace">
      <div v-if="store.isLoading" class="loading-state"><div class="spinner"></div><p>Analyzing...</p></div>
      <div v-else-if="store.errorMessage" class="error-state">{{ store.errorMessage }}</div>
      <template v-else-if="store.activeTarget">
        <TargetHeader :company-name="store.activeTarget.companyName" :job-title="store.activeTarget.jobTitle"
          :score-before="store.activeTarget.matchScoreBefore" :score-after="store.activeTarget.matchScoreAfter"
          :high-confidence-count="store.highConfidenceCount"
          @accept-all-high="store.acceptAllHighConfidence" @export-pdf="handleExportPDF" />
        <div v-if="store.activeDiffDelta" class="diff-area"><DiffCard v-for="item in store.activeDiffDelta.diff_items" :key="item.id"
          :item="item" :is-accepted="store.activeAcceptedIds.has(item.id)" @toggle-accept="store.toggleAccept" /></div>
        <div v-else class="empty-state">Click + to create a target with a real JD</div>
      </template>
      <div v-else class="empty-state">Select a target or create one</div>
    </main>
    <aside class="preview-pane"><div class="preview-title">Live Preview</div><div class="preview-content"><pre>{{ store.finalResumeText || "No content" }}</pre></div></aside>
    <CreateTargetModal :is-open="isModalOpen" @close="isModalOpen = false" @submit="handleCreateTarget" />
  </div>
</template>
<style scoped>
.app-root { display: flex; height: 100vh; width: 100vw; overflow: hidden; background: #0b0f19; color: #f1f5f9; }
.workspace { flex: 1; display: flex; flex-direction: column; background: #0f172a; overflow: hidden; }
.loading-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #38bdf8; }
.spinner { width: 40px; height: 40px; border: 4px solid #1e293b; border-top-color: #38bdf8; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.error-state { flex: 1; display: flex; align-items: center; justify-content: center; color: #f87171; padding: 24px; }
.empty-state { flex: 1; display: flex; align-items: center; justify-content: center; color: #64748b; font-size: 14px; }
.diff-area { flex: 1; padding: 24px; overflow-y: auto; }
.preview-pane { width: 350px; background: #0b0f19; border-left: 1px solid #1e293b; display: flex; flex-direction: column; }
.preview-title { padding: 16px; border-bottom: 1px solid #1e293b; font-size: 14px; font-weight: 600; color: #94a3b8; }
.preview-content { flex: 1; padding: 20px; overflow-y: auto; }
.preview-content pre { font-family: monospace; font-size: 12px; color: #cbd5e1; white-space: pre-wrap; line-height: 1.6; margin: 0; }
</style>
