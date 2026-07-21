<script setup lang="ts">
import type { DiffItem } from "../types/diff"
defineProps<{ item: DiffItem; isAccepted: boolean }>()
const emit = defineEmits<{ (e: "toggle-accept", id: string): void }>()
</script>

<template>
  <div class="diff-card" :class="{ accepted: isAccepted, 'conf-low': item.confidence === 'LOW' }">
    <div class="diff-header">
      <div class="diff-tags">
        <span class="tag-type">{{ item.type }}</span>
        <span class="tag-conf" :class="'conf-' + item.confidence.toLowerCase()">{{ item.confidence === 'HIGH' ? '&#39640;&#20449;&#24515;&#24230;' : item.confidence === 'MEDIUM' ? '&#20013;&#20449;&#24515;&#24230;' : '&#9888;&#20449;&#24515;&#24230;' }}</span>
      </div>
      <span class="diff-section">{{ item.section }}</span>
    </div>
    <div class="diff-body">
      <div v-if="item.original_text" class="diff-original"><span class="diff-mark">-</span><del>{{ item.original_text }}</del></div>
      <div class="diff-proposed"><span class="diff-mark">+</span><span>{{ item.proposed_text }}</span></div>
    </div>
    <div v-if="item.keywords_aligned.length" class="diff-keywords">
      <span class="kw-label">&#127919; &#24050;&#23545;&#40784;&#20851;&#38190;&#35789;:</span>
      <span v-for="kw in item.keywords_aligned" :key="kw" class="kw-tag">{{ kw }}</span>
    </div>
    <div class="diff-reason" :class="{ 'reason-low': item.confidence === 'LOW' }">&#128161; <strong>&#20248;&#21270;&#36923;&#36753;:</strong> {{ item.reason }}</div>
    <div class="diff-actions">
      <button class="btn-accept" :class="{ accepted: isAccepted }" @click="emit('toggle-accept', item.id)">{{ isAccepted ? '&#10003; &#24050;&#37319;&#32435;' : '&#37319;&#32435;&#27492;&#20462;&#25913;' }}</button>
    </div>
  </div>
</template>

<style scoped>
.diff-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 16px; margin-bottom: 16px; transition: all 0.2s; }
.diff-card.accepted { border-color: #10b981; background: rgba(16,185,129,0.05); box-shadow: 0 0 12px rgba(16,185,129,0.1); }
.diff-card.conf-low { border-color: rgba(245,158,11,0.5); }
.diff-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.diff-tags { display: flex; gap: 8px; align-items: center; }
.tag-type { background: #334155; color: #f1f5f9; font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 4px; }
.tag-conf { font-size: 10px; font-weight: 700; padding: 1px 8px; border-radius: 4px; }
.tag-conf.conf-high { background: rgba(16,185,129,0.15); color: #34d399; }
.tag-conf.conf-medium { background: rgba(56,189,248,0.15); color: #38bdf8; }
.tag-conf.conf-low { background: rgba(245,158,11,0.15); color: #fbbf24; }
.diff-section { color: #64748b; font-size: 11px; font-weight: 600; }
.diff-body { background: #0f172a; border-radius: 8px; padding: 12px; font-family: monospace; font-size: 12px; line-height: 1.6; margin-bottom: 12px; }
.diff-original { background: rgba(244,63,94,0.15); color: #fda4af; padding: 6px; border-radius: 4px; display: flex; gap: 8px; margin-bottom: 4px; }
.diff-proposed { background: rgba(16,185,129,0.15); color: #6ee7b7; padding: 6px; border-radius: 4px; display: flex; gap: 8px; }
.diff-mark { font-weight: 700; user-select: none; }
.diff-original .diff-mark { color: #f43f5e; }
.diff-proposed .diff-mark { color: #10b981; }
.diff-keywords { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.kw-label { font-size: 12px; color: #94a3b8; }
.kw-tag { background: rgba(56,189,248,0.1); color: #38bdf8; border: 1px solid rgba(56,189,248,0.2); font-size: 10px; padding: 1px 6px; border-radius: 4px; }
.diff-reason { background: rgba(15,23,42,0.5); padding: 10px; border-radius: 6px; font-size: 12px; color: #cbd5e1; margin-bottom: 12px; }
.diff-reason.reason-low { border-left: 4px solid #f59e0b; color: #fcd34d; }
.diff-actions { display: flex; justify-content: flex-end; }
.btn-accept { padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 600; border: none; cursor: pointer; transition: all 0.2s; background: #334155; color: #f1f5f9; }
.btn-accept:hover { background: #475569; }
.btn-accept.accepted { background: #10b981; color: white; }
</style>