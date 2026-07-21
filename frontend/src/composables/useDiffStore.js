import { reactive, computed } from 'vue'

const state = reactive({
  diffs: [],
  accepted: new Set(),
  baseResume: '',
})

export function useDiffStore() {
  function acceptDiff(index) {
    state.accepted.add(index)
    state.accepted = new Set(state.accepted)
  }

  function rejectDiff(index) {
    state.accepted.delete(index)
    state.accepted = new Set(state.accepted)
  }

  function acceptAllHigh() {
    state.diffs.forEach((d, i) => {
      if (d.confidence === 'high') state.accepted.add(i)
    })
    state.accepted = new Set(state.accepted)
  }

  function setDiffs(diffs, baseResume) {
    state.diffs = diffs || []
    state.baseResume = baseResume || ''
    state.accepted = new Set()
  }

  const finalResume = computed(() => {
    let result = state.baseResume
    const acceptedDiffs = state.diffs
      .map((d, i) => ({ ...d, _index: i }))
      .filter(d => state.accepted.has(d._index))

    for (const diff of acceptedDiffs) {
      if (diff.type === 'modify' && diff.original_text) {
        result = result.replace(diff.original_text, diff.proposed_text)
      } else if (diff.type === 'add') {
        result += '\n' + diff.proposed_text
      } else if (diff.type === 'delete' && diff.original_text) {
        result = result.replace(diff.original_text, '')
      }
    }
    return result
  })

  function reset() {
    state.diffs = []
    state.accepted = new Set()
    state.baseResume = ''
  }

  return { state, acceptDiff, rejectDiff, acceptAllHigh, setDiffs, finalResume, reset }
}
