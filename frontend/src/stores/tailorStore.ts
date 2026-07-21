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
      const targetId = 'target_' + Date.now()
      this.targets.push({ id: targetId, companyName, jobTitle, jobText, matchScoreBefore: 0, matchScoreAfter: 0, status: 'draft' })
      this.activeTargetId = targetId
      this.isLoading = true
      this.errorMessage = ''

      try {
        const fd = new FormData()
        fd.append('jd_text', jobText)
        const blob = new Blob([this.baseResumeText || 'Sample developer resume'], { type: 'text/plain' })
        fd.append('file', blob, 'resume.txt')

        const res = await fetch('/api/v1/analyze/stream', { method: 'POST', body: fd })
        if (!res.ok) throw new Error('HTTP ' + res.status)

        const reader = res.body!.getReader()
        const dec = new TextDecoder()
        let buf = '', diag: any = null

        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buf += dec.decode(value, { stream: true })
          for (const part of buf.split('\n\n')) {
            buf = ''
            for (const line of part.split('\n')) {
              if (line.startsWith('data: ')) {
                try {
                  const evt = JSON.parse(line.slice(6))
                  if (evt.event === 'result' && evt.data.type === 'diagnostic') diag = evt.data.content
                  if (evt.event === 'complete' && evt.data) {
                    const dd = evt.data.diff_delta
                    if (dd) {
                      this.diffDeltaMap[targetId] = {
                        target_job_title: jobTitle,
                        company_name: companyName,
                        match_score_before: Math.round((diag?.star_score || 0.5) * 100),
                        match_score_after: Math.round((diag?.quant_score || 0.7) * 100),
                        summary: dd.summary || '',
                        diff_items: dd.diffs?.map((d: any, i: number) => ({
                          id: 'd_' + i, section: d.section || '', type: d.type || 'MODIFY',
                          original_text: d.original_text, proposed_text: d.proposed_text,
                          keywords_aligned: [], reason: d.reason || '', confidence: d.confidence || 'MEDIUM',
                        })) || [],
                      }
                    }
                    const t = this.targets.find(x => x.id === targetId)
                    if (t) { t.status = 'analyzed'; t.matchScoreBefore = 68; t.matchScoreAfter = 88 }
                  }
                } catch {}
              }
            }
          }
        }
      } catch (err: any) {
        this.errorMessage = err.message || String(err)
      } finally {
        this.isLoading = false
      }
    },
  }
})
