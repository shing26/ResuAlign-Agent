<script setup lang="ts">
import { ref, onMounted } from "vue"

const terminalText = ref("")
const fullText = "> INITIALIZING AGENT PROTOCOLS...\n> ESTABLISHING SECURE CONNECTION...\n> ALL SYSTEMS NOMINAL. READY FOR INPUT."

onMounted(() => {
  let i = 0
  const tw = setInterval(() => {
    terminalText.value += fullText.charAt(i)
    i++
    if (i >= fullText.length) clearInterval(tw)
  }, 50)
})
</script>

<template>
  <section class="relative min-h-screen w-full bg-[#050505] text-cyan-400 overflow-hidden font-mono flex items-center justify-center p-8">
    <div class="absolute inset-0 z-0 opacity-20 pointer-events-none bg-[linear-gradient(rgba(0,255,255,0.3)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,255,0.3)_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,#000_20%,transparent_100%)]"></div>

    <header class="absolute top-0 left-0 w-full p-6 flex justify-between items-start z-20">
      <div class="flex flex-col gap-1">
        <span class="text-xs tracking-widest text-cyan-500/60">SYS_ID: OP-CLAW-09</span>
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]"></div>
          <span class="text-sm font-bold text-emerald-400">ONLINE</span>
        </div>
      </div>
      <nav class="flex gap-6 text-sm uppercase tracking-widest">
        <a href="#" class="hover:text-fuchsia-500 transition-colors">Dashboard</a>
        <a href="#" class="hover:text-fuchsia-500 transition-colors">Modules</a>
        <a href="#" class="text-fuchsia-500 border-b border-fuchsia-500 pb-1">Gateway</a>
      </nav>
    </header>

    <div class="relative z-10 w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-8">
      <div class="lg:col-span-7 flex flex-col justify-center">
        <h1 class="text-6xl lg:text-8xl font-black uppercase tracking-tighter leading-none mb-4 text-transparent bg-clip-text bg-gradient-to-br from-cyan-400 to-blue-700 drop-shadow-[0_0_20px_rgba(0,255,255,0.3)]">System<br/>Overdrive.</h1>
        <p class="text-slate-400 max-w-xl text-lg mb-10 leading-relaxed border-l-2 border-cyan-500/50 pl-4">Bypass traditional frameworks. Deploy highly isolated, multi-agent gateways engineered for maximum throughput.</p>
        <div class="flex gap-4">
          <button class="relative px-8 py-3 bg-cyan-500/10 border border-cyan-400 text-cyan-300 font-bold uppercase tracking-widest hover:bg-cyan-400 hover:text-black transition-all shadow-[0_0_15px_rgba(0,255,255,0.2)] hover:shadow-[0_0_30px_rgba(0,255,255,0.6)]">
            Initialize
            <span class="absolute top-0 right-0 w-2 h-2 bg-cyan-400"></span>
            <span class="absolute bottom-0 left-0 w-2 h-2 bg-cyan-400"></span>
          </button>
          <button class="px-8 py-3 border border-slate-700 text-slate-400 font-bold uppercase tracking-widest hover:border-fuchsia-500 hover:text-fuchsia-400 transition-colors">View Logs</button>
        </div>
      </div>
      <div class="lg:col-span-5 relative">
        <div class="absolute -inset-1 bg-gradient-to-b from-cyan-500 to-fuchsia-500 opacity-20 blur"></div>
        <div class="relative bg-black/80 border border-cyan-500/30 backdrop-blur-xl h-full min-h-[400px] p-6 flex flex-col shadow-2xl shadow-cyan-900/20">
          <div class="flex justify-between items-center border-b border-slate-800 pb-3 mb-4">
            <span class="text-xs text-slate-500 uppercase">Gateway.exe</span>
            <div class="flex gap-2">
              <div class="w-3 h-3 bg-rose-500 rounded-full"></div>
              <div class="w-3 h-3 bg-amber-500 rounded-full"></div>
              <div class="w-3 h-3 bg-emerald-500 rounded-full"></div>
            </div>
          </div>
          <div class="flex-1 flex flex-col gap-2 overflow-hidden">
            <pre class="text-cyan-400 text-sm whitespace-pre-wrap leading-relaxed">{{ terminalText }}<span class="animate-pulse">_</span></pre>
          </div>
          <div class="h-24 mt-auto border border-slate-800 bg-slate-900/30 relative overflow-hidden flex items-end p-2 gap-1">
            <div v-for="i in 12" :key="i" class="w-full bg-cyan-500/40 hover:bg-fuchsia-500 transition-colors" :style="'height: ' + Math.random() * 100 + '%'"></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
