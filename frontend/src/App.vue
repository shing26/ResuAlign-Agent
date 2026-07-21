<script setup lang="ts">
import { onMounted } from "vue"
import { useTailorStore } from "./stores/tailorStore"
import JobTargetSidebar from "./components/JobTargetSidebar.vue"
import TargetHeader from "./components/TargetHeader.vue"
import DiffCard from "./components/DiffCard.vue"

const store = useTailorStore()

onMounted(() => {
  if (store.targets.length === 0) {
    store.targets.push({
      id: "target_1", companyName: "腾讯", jobTitle: "基础架构实习生",
      jobText: "要求熟练掌握 Redis 分布式锁与高并发治理...",
      matchScoreBefore: 68, matchScoreAfter: 88, status: "analyzed" as const,
    })
    store.activeTargetId = "target_1"
  }
})
</script>

<template>
  <div class="app-root">
    <JobTargetSidebar :targets="store.targets" :active-target-id="store.activeTargetId" @select-target="(id: string) => store.activeTargetId = id" @create-target="() => {}" />
    <main class="workspace">
      <div v-if="store.isLoading" class="loading-state">
        <div class="spinner-custom"></div>
        <p>Agents &#27491;&#22312;&#31934;&#20934;&#23545;&#40784; JD &#20013;...</p>
      </div>
      <template v-else-if="store.activeTarget">
        <TargetHeader :company-name="store.activeTarget.companyName" :job-title="store.activeTarget.jobTitle" :score-before="store.activeTarget.matchScoreBefore" :score-after="store.activeTarget.matchScoreAfter" :high-confidence-count="store.highConfidenceCount" @accept-all-high="store.acceptAllHighConfidence" @export-pdf="() => {}" />
        <div v-if="store.activeDiffDelta" class="diff-area">
          <DiffCard v-for="item in store.activeDiffDelta.diff_items" :key="item.id" :item="item" :is-accepted="store.activeAcceptedIds.has(item.id)" @toggle-accept="(id: string) => store.toggleAccept(id)" />
        </div>
      </template>
    </main>
    <aside class="preview-pane">
      <div class="preview-title">&#128196; &#23450;&#21046;&#31616;&#21382;&#23454;&#26102;&#39044;&#35272;</div>
      <div class="preview-content"><pre>{{ store.finalResumeText }}</pre></div>
    </aside>
  </div>
</template>

<style scoped>
.app-root { display: flex; height: 100vh; width: 100vw; overflow: hidden; background: #0b0f19; color: #f1f5f9; }
.workspace { flex: 1; display: flex; flex-direction: column; background: #0f172a; overflow: hidden; }
.loading-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #38bdf8; }
.spinner-custom { width: 40px; height: 40px; border: 4px solid #1e293b; border-top-color: #38bdf8; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.diff-area { flex: 1; padding: 24px; overflow-y: auto; }
.preview-pane { width: 350px; background: #0b0f19; border-left: 1px solid #1e293b; display: flex; flex-direction: column; }
.preview-title { padding: 16px; border-bottom: 1px solid #1e293b; font-size: 14px; font-weight: 600; color: #94a3b8; }
.preview-content { flex: 1; padding: 20px; overflow-y: auto; }
.preview-content pre { font-family: monospace; font-size: 12px; color: #cbd5e1; white-space: pre-wrap; line-height: 1.6; margin: 0; }
</style>