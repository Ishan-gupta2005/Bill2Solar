import type { PipelineStep } from '../lib/api'

const STEPS: { key: PipelineStep['step']; short: string; service: string; waiting: string }[] = [
  { key: 's3', short: 'S3', service: 'Amazon S3', waiting: 'uploading bill photo' },
  { key: 'rekognition', short: 'REK', service: 'Amazon Rekognition', waiting: 'DetectText: reading every line' },
  { key: 'bedrock', short: 'BDR', service: 'Amazon Bedrock', waiting: 'Converse: extracting units, load, DISCOM' },
  { key: 'dynamodb', short: 'DDB', service: 'Amazon DynamoDB', waiting: 'saving your estimate' },
]

type Props = { active: number; steps?: PipelineStep[] }

/** `active` is the index currently running while we wait; once `steps` arrive the real timings win. */
export default function Pipeline({ active, steps }: Props) {
  return (
    <div className="pipeline no-print">
      {STEPS.map((s, i) => {
        const real = steps?.find(x => x.step === s.key)
        let cls = ''
        if (real) cls = real.ok ? 'done' : 'degraded'
        else if (i === active) cls = 'running'
        else if (i < active) cls = 'done'
        return (
          <div key={s.key} className={`stepcard ${cls}`}>
            <div className="ic">{s.short}</div>
            <div className="t">
              <b>{s.service}</b>
              <span title={real?.detail}>{real ? (real.model ? `${real.detail} · ${real.model.split('.').pop()}` : real.detail) : (i <= active ? s.waiting : 'queued')}</span>
            </div>
            <div className="ms">{real ? `${real.ms} ms` : i === active ? '…' : ''}</div>
          </div>
        )
      })}
    </div>
  )
}
