<script setup lang="ts">
import { useTailorStore } from '@/stores/tailorStore'
import { computed } from 'vue'

const props = defineProps<{
  targets: any[]
  activeTargetId: string
}>()

const emit = defineEmits<{
  (e: 'select-target', id: string): void
  (e: 'create-target'): void
  (e: 'upload-resume'): void
  (e: 'open-settings'): void
}>()

const store = useTailorStore()

// 判断是否已上传主简历
const hasBaseResume = computed(() => !!store.baseResumeText)
</script>

<template>
  <aside class="w-64 bg-[#0b0f19] border-r border-[#1e293b] flex flex-col h-full z-20">
    <!-- 1. Logo 与系统设置 -->
    <div class="p-5 border-b border-[#1e293b] flex justify-between items-center">
      <div class="flex items-center gap-2">
        <span class="text-sky-400 font-black text-xl">⚡</span>
        <h1 class="text-slate-100 font-bold tracking-wider">ResuAlign <span class="text-xs bg-sky-500/20 text-sky-400 px-1.5 py-0.5 rounded">v2.0</span></h1>
      </div>
      <button @click="emit('open-settings')" class="text-slate-400 hover:text-sky-400 transition-colors" title="系统设置">
        ⚙️
      </button>
    </div>

    <!-- 2. 全局前置：PDF 主简历上传区 (Cyber 风格) -->
    <div class="p-4 border-b border-[#1e293b] bg-[#0f172a]/50">
      <div class="text-xs font-semibold text-slate-500 mb-3 tracking-wide uppercase">
        Base Resume (Truth Source)
      </div>
      
      <!-- 未上传状态 -->
      <button 
        v-if="!hasBaseResume"
        @click="emit('upload-resume')"
        class="w-full flex flex-col items-center justify-center gap-2 border-2 border-dashed border-sky-500/30 bg-sky-500/5 hover:bg-sky-500/10 hover:border-sky-400 transition-all rounded-xl p-4 cursor-pointer group"
      >
        <div class="p-2 bg-sky-500/20 rounded-full text-sky-400 group-hover:scale-110 transition-transform">
          📄
        </div>
        <div class="text-center">
          <p class="text-sm font-semibold text-sky-400">上传 PDF 主简历</p>
          <p class="text-xs text-slate-500 mt-1">支持解析并作为真理源</p>
        </div>
      </button>

      <!-- 已上传状态 -->
      <div v-else class="flex items-center justify-between bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3">
        <div class="flex items-center gap-2 overflow-hidden">
          <span class="text-emerald-400 text-lg">✓</span>
          <div class="truncate">
            <p class="text-xs font-semibold text-emerald-400">主简历已就绪</p>
            <p class="text-[10px] text-slate-400 truncate">可进行靶向多路对齐</p>
          </div>
        </div>
        <button @click="emit('upload-resume')" class="text-xs text-slate-400 hover:text-sky-400 underline">
          重新上传
        </button>
      </div>
    </div>

    <!-- 3. 多路岗位对齐看板 -->
    <div class="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
      <div class="flex items-center justify-between mb-1">
        <span class="text-xs font-semibold text-slate-500 tracking-wide uppercase">Target Boards ({{ targets.length }})</span>
      </div>

      <!-- 岗位目标列表 -->
      <button
        v-for="target in targets"
        :key="target.id"
        @click="emit('select-target', target.id)"
        class="text-left w-full p-3 rounded-lg border transition-all relative overflow-hidden"
        :class="[
          activeTargetId === target.id 
            ? 'bg-[#1e293b] border-sky-500 shadow-[0_0_15px_rgba(14,165,233,0.15)]' 
            : 'bg-[#0f172a] border-[#334155] hover:border-slate-400'
        ]"
      >
        <div class="font-bold text-sm text-slate-200 truncate">{{ target.companyName }}</div>
        <div class="text-xs text-slate-400 mt-1 truncate">{{ target.jobTitle }}</div>
        
        <!-- 侧边霓虹指示灯 -->
        <div 
          v-if="activeTargetId === target.id" 
          class="absolute left-0 top-0 bottom-0 w-1 bg-sky-400 shadow-[0_0_8px_rgba(14,165,233,0.8)]"
        ></div>
      </button>
    </div>

    <!-- 4. 新建投递按钮 -->
    <div class="p-4 border-t border-[#1e293b]">
      <button 
        @click="emit('create-target')"
        :disabled="!hasBaseResume"
        class="w-full py-2.5 rounded-lg text-sm font-bold transition-all shadow-lg flex items-center justify-center gap-2"
        :class="hasBaseResume ? 'bg-sky-500 hover:bg-sky-400 text-white' : 'bg-slate-700 text-slate-500 cursor-not-allowed'"
        :title="!hasBaseResume ? '请先上传主简历' : ''"
      >
        <span>+</span> 新建岗位投递
      </button>
    </div>
  </aside>
</template>
