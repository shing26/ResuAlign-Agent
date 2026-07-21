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
    }
  }
})
