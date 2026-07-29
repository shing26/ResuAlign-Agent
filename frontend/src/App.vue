<script setup lang="ts">
import { ref, onMounted, watch } from "vue"
import { useTailorStore } from "./stores/tailorStore"
import JobTargetSidebar from "./components/JobTargetSidebar.vue"
import TargetHeader from "./components/TargetHeader.vue"
import DiffCard from "./components/DiffCard.vue"
import LivePreview from "./components/LivePreview.vue"
import SettingsPanel from "./components/SettingsPanel.vue"
import CreateTargetModal from "./components/CreateTargetModal.vue"

const store = useTailorStore()
const isCreateModalOpen = ref(false)
const isSettingsOpen = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const fd = new FormData()
  fd.append("file", file)
  try {
    store.isLoading = true
    const res = await fetch("/api/v1/resume/parse-pdf", { method: "POST", body: fd })
    const data = await res.json()
    store.baseResumeText = data.raw_text
    store.errorMessage = null
  } catch {
    store.errorMessage = "PDF parse failed"
  } finally {
    store.isLoading = false
  }
}

async function handleCreateTarget(p: { companyName: string; jobTitle: string; jobText: string }) {
  isCreateModalOpen.value = false
  await store.createTargetAndAnalyze(p.companyName, p.jobTitle, p.jobText)
}

function handleExportPDF() {
  if (store.finalResumeText) {
    navigator.clipboard.writeText(store.finalResumeText)
    alert("Copied to clipboard!")
  } else {
    alert("No content to export")
  }
}
</script>

<template>
  <div class="app-root">
    <input type="file" ref="fileInputRef" accept=".pdf,.txt" hidden @change="handleFileUpload" />

    <JobTargetSidebar
      :targets="store.targets"
      :active-target-id="store.activeTargetId"
      @select-target="store.setActiveTarget"
      @create-target="isCreateModalOpen = true"
      @upload-resume="fileInputRef?.click()"
      @open-settings="isSettingsOpen = true"
    />

    <main class="workspace">
      <!-- Top bar -->
      <div class="top-bar">
        <span :class="store.baseResumeText ? 'text-emerald-400' : 'text-amber-400'">
          {{ store.baseResumeText ? 'Resume loaded' : 'No resume uploaded' }}
        </span>
        <button @click="isSettingsOpen = true" class="settings-btn">&#9881; Settings</button>
      </div>

      <!-- Loading -->
      <div v-if="store.isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Analyzing...</p>
      </div>

      <!-- Error -->
      <div v-else-if="store.errorMessage" class="error-state">{{ store.errorMessage }}</div>

      <!-- Active target -->
      <template v-else-if="store.activeTarget">
        <TargetHeader
          :company-name="store.activeTarget.companyName"
          :job-title="store.activeTarget.jobTitle"
          :score-before="store.activeTarget.matchScoreBefore"
          :score-after="store.activeTarget.matchScoreAfter"
          :high-confidence-count="store.highConfidenceCount"
          @accept-all-high="store.acceptAllHighConfidence"
          @export-pdf="handleExportPDF"
        />
        <div v-if="store.activeDiffDelta" class="diff-area">
          <DiffCard
            v-for="item in store.activeDiffDelta.diff_items"
            :key="item.id"
            :item="item"
            :is-accepted="store.activeAcceptedIds.has(item.id)"
            @toggle-accept="store.toggleAccept"
          />
        </div>
        <div v-else class="empty-state">Create a target to see suggestions</div>
      </template>

      <!-- No target -->
      <div v-else class="empty-state">Select a target or create one</div>
    </main>

    <LivePreview :content="store.finalResumeText" />

    <!-- Settings Modal -->
    <div v-if="isSettingsOpen" class="settings-overlay" @click.self="isSettingsOpen = false">
      <div class="settings-modal">
        <div class="settings-modal-header">
          <h3>Settings</h3>
          <button @click="isSettingsOpen = false">&#10005;</button>
        </div>
        <SettingsPanel />
      </div>
    </div>

    <CreateTargetModal :is-open="isCreateModalOpen" @close="isCreateModalOpen = false" @submit="handleCreateTarget" />
  </div>
</template>

<style>
.app-root { display: flex; height: 100vh; width: 100vw; overflow: hidden; background: #0b0f19; color: #f1f5f9; }
.workspace { flex: 1; display: flex; flex-direction: column; background: #0f172a; overflow: hidden; }
.top-bar { background: rgba(11,15,25,0.5); border-bottom: 1px solid #1e293b; padding: 8px 16px; display: flex; justify-content: space-between; align-items: center; font-size: 12px; }
.settings-btn { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 12px; }
.settings-btn:hover { color: #38bdf8; }
.loading-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #38bdf8; }
.spinner { width: 40px; height: 40px; border: 4px solid #1e293b; border-top-color: #38bdf8; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.error-state { flex: 1; display: flex; align-items: center; justify-content: center; color: #f87171; padding: 24px; }
.empty-state { flex: 1; display: flex; align-items: center; justify-content: center; color: #64748b; font-size: 14px; }
.diff-area { flex: 1; padding: 24px; overflow-y: auto; }
.settings-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 100; }
.settings-modal { background: #0f172a; border: 1px solid #334155; border-radius: 12px; width: 90%; max-width: 500px; max-height: 80vh; overflow-y: auto; padding: 20px; }
.settings-modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.settings-modal-header h3 { font-size: 18px; font-weight: 700; margin: 0; color: #f1f5f9; }
.settings-modal-header button { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 18px; }
</style>

