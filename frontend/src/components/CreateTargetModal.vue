<script setup lang="ts">
import { ref } from "vue"
defineProps<{ isOpen: boolean }>()
const emit = defineEmits<{ (e: "close"): void; (e: "submit", p: { companyName: string; jobTitle: string; jobText: string }): void }>()
const companyName = ref("")
const jobTitle = ref("")
const jobText = ref("")
function handleSubmit() {
  if (!companyName.value || !jobTitle.value || !jobText.value) { alert("Please fill in all fields"); return }
  emit("submit", { companyName: companyName.value, jobTitle: jobTitle.value, jobText: jobText.value })
  companyName.value = ""; jobTitle.value = ""; jobText.value = ""
}
</script>
<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-card">
      <div class="modal-header"><h3>New Target</h3><button @click="emit('close')" class="btn-close">X</button></div>
      <div class="modal-body">
        <label>Company</label><input v-model="companyName" placeholder="Tencent / ByteDance" />
        <label>Position</label><input v-model="jobTitle" placeholder="Backend Intern" />
        <label>JD Text</label><textarea v-model="jobText" rows="6" placeholder="Paste the full job description..." style="font-family:monospace"></textarea>
      </div>
      <div class="modal-footer"><button class="btn-cancel" @click="emit('close')">Cancel</button><button class="btn-submit" @click="handleSubmit">Analyze</button></div>
    </div>
  </div>
</template>
<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 16px; }
.modal-card { background: #0f172a; border: 1px solid #334155; border-radius: 12px; width: 100%; max-width: 560px; padding: 24px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.modal-header h3 { font-size: 18px; font-weight: 700; color: #f1f5f9; margin: 0; }
.btn-close { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 18px; }
.modal-body { display: flex; flex-direction: column; gap: 12px; }
.modal-body label { font-size: 12px; font-weight: 600; color: #94a3b8; }
.modal-body input, .modal-body textarea { width: 100%; background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 8px 12px; color: #f1f5f9; font-size: 14px; outline: none; }
.modal-body input:focus, .modal-body textarea:focus { border-color: #38bdf8; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.btn-cancel { padding: 8px 16px; background: #1e293b; color: #f1f5f9; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }
.btn-submit { padding: 8px 16px; background: #0ea5e9; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 700; }
.btn-cancel:hover { background: #334155; } .btn-submit:hover { background: #38bdf8; }
</style>
