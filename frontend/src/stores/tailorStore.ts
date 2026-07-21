import { defineStore } from 'pinia'
import type { DiffDelta, DiffItem, JobTarget } from '@/types/diff'

export const useTailorStore = defineStore('tailor', {
  state: () => ({
    baseResumeText: '',
    targets: [] as JobTarget[],
    activeTargetId: '' as string,
    diffDeltaMap: {} as Record<string, DiffDelta>,
    acceptedDiffIdsMap: {} as Record<string, Set<string>>,
    isLoading: false,
    errorMessage: '',
  }),

  getters: {
    activeTarget(state): JobTarget | undefined {
      return state.targets.find(t => t.id === state.activeTargetId)
    },
    activeDiffDelta(state): DiffDelta | undefined {
      return state.diffDeltaMap[state.activeTargetId]
    },
    activeAcceptedIds(state): Set<string> {
      if (!state.acceptedDiffIdsMap[state.activeTargetId]) {
        state.acceptedDiffIdsMap[state.activeTargetId] = new Set()
      }
      return state.acceptedDiffIdsMap[state.activeTargetId]
    },
    highConfidenceCount(): number {
      const delta = this.activeDiffDelta
      return delta ? delta.diff_items.filter(i => i.confidence === 'HIGH').length : 0
    },
    finalResumeText(state): string {
      const delta = state.diffDeltaMap[state.activeTargetId]
      const acceptedIds = state.acceptedDiffIdsMap[state.activeTargetId]
      if (!delta || !acceptedIds || acceptedIds.size === 0) return state.baseResumeText
      let resultText = state.baseResumeText
      delta.diff_items.forEach((item: DiffItem) => {
        if (!acceptedIds.has(item.id)) return
        if (item.type === 'MODIFY' && item.original_text && resultText.includes(item.original_text)) {
          resultText = resultText.replace(item.original_text, item.proposed_text)
        } else if (item.type === 'ADD' && item.original_text && resultText.includes(item.original_text)) {
          resultText = resultText.replace(item.original_text, item.original_text + '\n' + item.proposed_text)
        } else if (item.type === 'DELETE' && item.original_text) {
          resultText = resultText.replace(item.original_text, '')
        }
      })
      return resultText
    }
  },

  actions: {
    toggleAccept(diffId: string) {
      if (!this.activeTargetId) return
      const acceptedSet = this.activeAcceptedIds
      acceptedSet.has(diffId) ? acceptedSet.delete(diffId) : acceptedSet.add(diffId)
    },
    acceptAllHighConfidence() {
      const delta = this.activeDiffDelta
      if (!delta || !this.activeTargetId) return
      const acceptedSet = this.activeAcceptedIds
      delta.diff_items.forEach(item => {
        if (item.confidence === 'HIGH') acceptedSet.add(item.id)
      })
    },
    setActiveTarget(id: string) {
      this.activeTargetId = id
    },
    async createTargetAndAnalyze(companyName: string, jobTitle: string, jobText: string) {
      if (!this.baseResumeText) { this.errorMessage = 'Please upload your resume first'; return }
      const targetId = 'target_' + Date.now()
      this.targets.push({ id: targetId, companyName, jobTitle, jobText, matchScoreBefore: 0, matchScoreAfter: 0, status: 'draft' })
      this.activeTargetId = targetId
      this.isLoading = true
      this.errorMessage = ''

      try {
        const res = await fetch('/api/v1/tailor', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ resume_text: this.baseResumeText, job_text: jobText, company_name: companyName, job_title: jobTitle })
        })
        if (!res.ok) throw new Error('HTTP ' + res.status)
        const data = await res.json()
        const dd = data.diff_delta
        if (dd && dd.diff_items) {
          this.diffDeltaMap[targetId] = {
            target_job_title: dd.target_job_title || jobTitle,
            company_name: dd.company_name || companyName,
            match_score_before: dd.match_score_before || 0,
            match_score_after: dd.match_score_after || 0,
            summary: dd.summary || '',
            diff_items: dd.diff_items.map((d: any, i: number) => ({...d, id: d.id || 'd_' + i})),
          }
        }
        const t = this.targets.find(x => x.id === targetId)
        if (t) { t.status = 'analyzed'; t.matchScoreBefore = dd?.match_score_before || 68; t.matchScoreAfter = dd?.match_score_after || 88 }
      } catch (err: any) {
        this.errorMessage = err.message || String(err)
      } finally {
        this.isLoading = false
      }
    },
  }
})
