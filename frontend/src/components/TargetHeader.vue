<script setup lang="ts">
defineProps<{ companyName: string; jobTitle: string; scoreBefore: number; scoreAfter: number; highConfidenceCount: number }>()
const emit = defineEmits<{ (e: "accept-all-high"): void; (e: "export-pdf"): void }>()
</script>

<template>
  <header class="header-bar">
    <div>
      <h1>{{ companyName }} <span class="title-sep">&#8212;</span> <span class="title-job">{{ jobTitle }}</span></h1>
      <div class="score-row">
        <span>ATS &#21305;&#37197;&#24230;&#39044;&#27979;:</span>
        <span class="score-old">{{ scoreBefore }}</span>
        <span class="score-arr">&#10140;</span>
        <span class="score-new">{{ scoreAfter }} &#20998;</span>
        <span class="score-gain">+{{ scoreAfter - scoreBefore }}&#20998; &#128200;</span>
      </div>
    </div>
    <div class="header-actions">
      <button class="btn-accept-all" :disabled="highConfidenceCount === 0" @click="emit('accept-all-high')">&#9889; &#19968;&#38190;&#37319;&#32435;&#39640;&#20449;&#24515;&#24230;&#25913;&#21160; ({{ highConfidenceCount }})</button>
      <button class="btn-export" @click="emit('export-pdf')">&#128229; &#23548;&#20986;&#23450;&#21046; PDF</button>
    </div>
  </header>
</template>

<style scoped>
.header-bar { background: #0f172a; border-bottom: 1px solid #1e293b; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }
.header-bar h1 { color: #f1f5f9; font-size: 18px; font-weight: 700; margin: 0; }
.title-sep { color: #64748b; }
.title-job { color: #94a3b8; font-weight: 400; }
.score-row { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #94a3b8; margin-top: 4px; }
.score-old { color: #f43f5e; text-decoration: line-through; }
.score-arr { color: #64748b; }
.score-new { color: #34d399; font-weight: 700; font-size: 14px; }
.score-gain { background: rgba(16,185,129,0.1); color: #34d399; padding: 1px 6px; border-radius: 4px; font-weight: 600; }
.header-actions { display: flex; gap: 12px; }
.btn-accept-all { background: linear-gradient(to right, #059669, #10b981); color: white; font-weight: 700; border: none; border-radius: 8px; padding: 8px 16px; font-size: 14px; cursor: pointer; transition: all 0.2s; box-shadow: 0 0 12px rgba(16,185,129,0.3); }
.btn-accept-all:hover { background: linear-gradient(to right, #10b981, #34d399); }
.btn-accept-all:disabled { background: #1e293b; color: #475569; box-shadow: none; cursor: not-allowed; }
.btn-export { background: #1e293b; color: #f1f5f9; border: 1px solid #475569; border-radius: 8px; padding: 8px 16px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-export:hover { background: #334155; }
</style>