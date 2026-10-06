export type EpistemicState =
  | 'open'
  | 'supported'
  | 'known'
  | 'contradicted'

export interface Hypothesis {
  id: string
  claim: string
  state: EpistemicState
  predictions: string[]
  evidence_for: string[]
  evidence_against: string[]
  falsifiers: string[]
  confounders: string[]
  uncertainties: string[]
}

export interface Observation {
  timestamp: string
  variable: string
  value: string | number | boolean
  unit: string | null
  source: string
  notes: string | null
}

export interface Investigation {
  id: string
  question: string
  domain: string
  status: string
  hypotheses: Hypothesis[]
  observations: Observation[]
  variables: string[]
  confounders: string[]
  created_at: string
  updated_at: string
}

interface ApiError {
  detail?: string
}

async function readError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as ApiError
    return body.detail ?? `Request failed with status ${response.status}`
  } catch {
    return `Request failed with status ${response.status}`
  }
}

export async function startInvestigation(
  question: string,
): Promise<Investigation> {
  const investigationId = `INV-${crypto.randomUUID()}`

  const response = await fetch('/api/investigations/from-question', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      investigation_id: investigationId,
      question,
    }),
  })

  if (!response.ok) {
    throw new Error(await readError(response))
  }

  return (await response.json()) as Investigation
}

export async function recordObservation(
  investigationId: string,
  variable: string,
  value: string | number | boolean,
  unit: string | null = null,
): Promise<Investigation> {
  const response = await fetch(
    `/api/investigations/${encodeURIComponent(investigationId)}/observations`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        variable,
        value,
        unit,
      }),
    },
  )

  if (!response.ok) {
    throw new Error(await readError(response))
  }

  return (await response.json()) as Investigation
}

export interface Experiment {
  question: string
  target_hypotheses: string[]
  variable_changed: string
  variables_held_constant: string[]
  observations_required: string[]
  duration_days: number
  predicted_results: Record<string, string>
}

export async function getNextTest(
  investigationId: string,
): Promise<Experiment> {
  const response = await fetch(
    `/api/investigations/${encodeURIComponent(investigationId)}/next-test`,
  )

  if (!response.ok) {
    throw new Error(await readError(response))
  }

  return (await response.json()) as Experiment
}
