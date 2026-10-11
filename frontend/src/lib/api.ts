export type Box = { left: number; top: number; width: number; height: number }
export type OcrLine = { id: number; text: string; confidence: number; box: Box }
export type PipelineStep = {
  step: 's3' | 'rekognition' | 'bedrock' | 'dynamodb' | string
  service: string
  api?: string
  model?: string
  detail: string
  ms: number
  ok: boolean
  fallback?: string
}
export type Extraction = {
  discom?: string | null
  discom_code?: string
  discom_portal?: string
  state?: string | null
  city?: string | null
  billing_period?: string | null
  units_consumed: number
  sanctioned_load_kw?: number | null
  bill_amount_rs?: number | null
  tariff_category?: string | null
  meter_type?: string | null
  confidence: number
  source: 'bedrock' | 'heuristic' | 'fallback'
  note?: string
}
export type Estimate = {
  monthly_units: number
  effective_tariff_rs_per_unit: number
  recommended_kw: number
  panel_count: number
  roof_sqft_needed: number
  monthly_generation_units: number
  gross_cost_rs: number
  subsidy_rs: number
  net_cost_rs: number
  annual_savings_rs: number
  monthly_savings_rs: number
  payback_years: number
  lifetime_savings_rs: number
  co2_tonnes_per_year: number
  trees_equivalent: number
  coverage_percent: number
  assumptions: Record<string, string | number>
}
export type AnalyzeResult = {
  id: string
  key: string
  created_at?: number
  extraction: Extraction
  estimate: Estimate
  field_boxes: Partial<Record<'units' | 'amount' | 'load' | 'discom', Box>>
  ocr: { lines: OcrLine[] }
  pipeline: PipelineStep[]
}
export type Proposal = {
  english: string
  hindi: string
  source: 'bedrock' | 'template'
  model?: string
  ms: number
  error?: string
}

export const API_URL: string = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') ?? ''
export const apiConfigured = API_URL.length > 0

export class ApiError extends Error {
  status: number
  code?: string
  constructor(status: number, message: string, code?: string) {
    super(message)
    this.status = status
    this.code = code
  }
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) {
    let code: string | undefined
    let message = `${path} failed with ${r.status}`
    try {
      const j = (await r.json()) as { error?: string; message?: string }
      code = j.error
      message = j.message ?? message
    } catch { /* non-JSON body */ }
    throw new ApiError(r.status, message, code)
  }
  return (await r.json()) as T
}

export async function presign(contentType: string): Promise<{ key: string; url: string }> {
  return post('/presign', { contentType })
}

export async function uploadToS3(url: string, blob: Blob): Promise<void> {
  const r = await fetch(url, { method: 'PUT', headers: { 'content-type': blob.type }, body: blob })
  if (!r.ok) throw new Error(`S3 upload failed: ${r.status}`)
}

export async function analyze(key: string, roofSqft?: number): Promise<AnalyzeResult> {
  return post('/analyze', { key, roofSqft })
}

export async function proposal(id: string): Promise<Proposal> {
  const r = await post<{ id: string; proposal: Proposal }>('/proposal', { id })
  return r.proposal
}

export async function health(): Promise<Record<string, unknown>> {
  const r = await fetch(`${API_URL}/health`)
  return r.json()
}
