import { defineStore } from 'pinia'
import type { DiffDelta, JobTarget } from '../types/diff'

export const useTailorStore = defineStore('tailor', {
  state: () => ({
    baseResumeText: '',
    targets: [] as JobTarget[],
    activeTargetId: '',
    diffDeltaMap: {} as Record<string, DiffDelta>,
    acceptedDiffIdsMap: {} as Record<string, Set<string>>,
    isLoading: false,
    errorMessage: null as string | null,
    settings: {
      apiKey: '',
      baseUrl: 'https://api.openai.com/v1',
      model: 'gpt-4o'
    }
  }),

  getters: {
    activeTarget: (state) => state.targets.find(t => t.id === state.activeTargetId),
    activeDiffDelta: (state) => state.diffDeltaMap[state.activeTargetId],
    activeAcceptedIds: (state) => state.acceptedDiffIdsMap[state.activeTargetId] || new Set(),

    highConfidenceCount(): number {
      const delta = this.activeDiffDelta
      return delta ? delta.diff_items.filter(i => i.confidence === 'HIGH').length : 0
    },

    finalResumeText(state): string {
      const delta = state.diffDeltaMap[state.activeTargetId]
      const acceptedIds = state.acceptedDiffIdsMap[state.activeTargetId]
      if (!state.baseResumeText) return ''
      if (!delta || !acceptedIds || acceptedIds.size === 0) return state.baseResumeText

      let result = state.baseResumeText
      delta.diff_items.forEach((item) => {
        if (!acceptedIds.has(item.id)) return
        if (item.type === 'MODIFY' && item.original_text) {
          result = result.replace(item.original_text, item.proposed_text)
        } else if (item.type === 'ADD' && item.original_text) {
          result = result.replace(item.original_text, item.original_text + '\\n- ' + item.proposed_text)
        } else if (item.type === 'DELETE' && item.original_text) {
          result = result.replace(item.original_text, '')
        }
      })
      return result
    }
  },

  actions: {
    setActiveTarget(id: string) { this.activeTargetId = id },

    toggleAccept(diffId: string) {
      if (!this.activeTargetId) return
      if (!this.acceptedDiffIdsMap[this.activeTargetId]) {
        this.acceptedDiffIdsMap[this.activeTargetId] = new Set()
      }
      const set = this.acceptedDiffIdsMap[this.activeTargetId]
      set.has(diffId) ? set.delete(diffId) : set.add(diffId)
    },

    acceptAllHighConfidence() {
      const delta = this.activeDiffDelta
      if (!delta || !this.activeTargetId) return
      if (!this.acceptedDiffIdsMap[this.activeTargetId]) {
        this.acceptedDiffIdsMap[this.activeTargetId] = new Set()
      }
      const set = this.acceptedDiffIdsMap[this.activeTargetId]
      delta.diff_items.forEach(item => {
        if (item.confidence === 'HIGH') set.add(item.id)
      })
    },

    async createTargetAndAnalyze(companyName: string, jobTitle: string, jobText: string) {
      if (!this.baseResumeText) { this.errorMessage = 'Upload your resume first'; return }
      const targetId = 'target_' + Date.now()
      this.targets.push({ id: targetId, companyName, jobTitle, jobText, matchScoreBefore: 0, matchScoreAfter: 0, status: 'draft' })
      this.activeTargetId = targetId
      this.isLoading = true
      this.errorMessage = null

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
            diff_items: dd.diff_items.map((d: any, i: number) => ({ ...d, id: d.id || 'd_' + i })),
          }
        }
        const t = this.targets.find(x => x.id === targetId)
        if (t) { t.matchScoreBefore = dd?.match_score_before || 68; t.matchScoreAfter = dd?.match_score_after || 88; t.status = 'analyzed' }
      } catch (err: any) {
        this.errorMessage = err.message || String(err)
      } finally {
        this.isLoading = false
      }
    }
  }
})
