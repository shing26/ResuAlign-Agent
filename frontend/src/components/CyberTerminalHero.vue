<script setup lang="ts">
import { ref, onMounted } from "vue"

const terminalText = ref("")
const fullText = "> ResuAlign-Agent STANDBY\n> Awaiting target selection...\n> Upload a resume and create a target to begin."

onMounted(() => {
  let i = 0
  const tw = setInterval(() => {
    terminalText.value += fullText.charAt(i)
    i++
    if (i >= fullText.length) clearInterval(tw)
  }, 30)
})
</script>

<template>
  <div class="empty-terminal">
    <div class="grid-bg"></div>
    <div class="terminal-card">
      <div class="terminal-bar"><span class="text-xs text-slate-500 uppercase">ResuAlign v2.0 — Gateway.exe</span></div>
      <pre class="terminal-output">{{ terminalText }}<span class="cursor">_</span></pre>
    </div>
    <p class="hint-text">Select a target from the sidebar or create one to start</p>
  </div>
</template>

<style scoped>
.empty-terminal { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; overflow: hidden; background: #0A0D14; padding: 24px; }
.grid-bg { position: absolute; inset: 0; opacity: 0.08; background-image: linear-gradient(rgba(0,240,255,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(0,240,255,0.3) 1px, transparent 1px); background-size: 40px 40px; pointer-events: none; }
.terminal-card { position: relative; background: rgba(15,23,42,0.8); border: 1px solid rgba(0,240,255,0.15); border-radius: 8px; width: 100%; max-width: 480px; padding: 0; overflow: hidden; box-shadow: 0 0 30px rgba(0,240,255,0.05); }
.terminal-bar { padding: 10px 16px; border-bottom: 1px solid rgba(0,240,255,0.1); }
.terminal-output { font-family: monospace; font-size: 13px; color: #00F0FF; padding: 20px; line-height: 1.8; min-height: 80px; white-space: pre-wrap; margin: 0; }
.cursor { animation: blink 1s step-end infinite; }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0; } }
.hint-text { font-size: 13px; color: #64748b; margin-top: 24px; letter-spacing: 0.5px; }
</style>