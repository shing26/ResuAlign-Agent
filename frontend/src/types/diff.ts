export type DiffType = 'MODIFY' | 'ADD' | 'DELETE' | 'REORDER'
export type ConfidenceLevel = 'HIGH' | 'MEDIUM' | 'LOW'

export interface DiffItem {
  id: string
  section: string
  type: DiffType
  original_text?: string
  proposed_text: string
  keywords_aligned: string[]
  reason: string
  confidence: ConfidenceLevel
}

export interface DiffDelta {
  target_job_title: string
  company_name?: string
  match_score_before: number
  match_score_after: number
  summary: string
  diff_items: DiffItem[]
}

export interface JobTarget {
  id: string
  companyName: string
  jobTitle: string
  jobText: string
  matchScoreBefore: number
  matchScoreAfter: number
  status: 'draft' | 'analyzed' | 'applied'
}
