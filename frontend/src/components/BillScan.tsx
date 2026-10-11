import { motion, AnimatePresence } from 'framer-motion'
import type { AnalyzeResult, Box } from '../lib/api'
import { inr, num } from '../lib/useCountUp'

type Props = { imageUrl: string; result: AnalyzeResult | null; scanning: boolean }

const FIELD_LABEL: Record<string, string> = { units: 'Units consumed', amount: 'Amount payable', load: 'Sanctioned load', discom: 'DISCOM' }
const FIELD_ORDER = ['discom', 'units', 'load', 'amount']

function pct(b: Box) {
  return { left: `${b.left * 100}%`, top: `${b.top * 100}%`, width: `${b.width * 100}%`, height: `${b.height * 100}%` }
}

export default function BillScan({ imageUrl, result, scanning }: Props) {
  const lines = result?.ocr.lines ?? []
  const fields = result?.field_boxes ?? {}
  const x = result?.extraction
  return (
    <div className="scan">
      <div className="billwrap">
        <img src={imageUrl} alt="Your electricity bill" />
        {scanning && <div className="scanline" />}
        <AnimatePresence>
          {lines.map((l, i) => (
            <motion.div key={`l${l.id}`} className="ocrbox" style={pct(l.box)}
              initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: Math.min(i * 0.025, 1.2), duration: 0.25 }} />
          ))}
          {FIELD_ORDER.filter(k => fields[k as keyof typeof fields]).map((k, i) => {
            const b = fields[k as keyof typeof fields]!
            const pad = 0.006
            const box = { left: b.left - pad, top: b.top - pad, width: b.width + pad * 2, height: b.height + pad * 2 }
            return (
              <motion.div key={`f${k}`} className={`fieldbox ${k}`} style={pct(box)}
                initial={{ opacity: 0, scale: 1.25 }} animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.3 + i * 0.45, duration: 0.4, type: 'spring', bounce: 0.35 }}>
                <span className="tag">{FIELD_LABEL[k]}</span>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>

      <div>
        <div className="readout">
          <Readout cls="discom" label="Distribution company" value={x?.discom ?? '—'} sub={x ? [x.city, x.state].filter(Boolean).join(', ') : ''} delay={1.3} ready={!!x} />
          <Readout cls="units" label="Units this month" value={x ? `${num(x.units_consumed)} kWh` : '—'} sub={x?.billing_period ?? ''} delay={1.75} ready={!!x} />
          <Readout cls="load" label="Sanctioned load" value={x?.sanctioned_load_kw ? `${num(x.sanctioned_load_kw, 1)} kW` : '—'} sub={x?.meter_type ?? ''} delay={2.2} ready={!!x} />
          <Readout cls="amount" label="Amount payable" value={x?.bill_amount_rs ? inr(x.bill_amount_rs) : '—'} sub={x?.bill_amount_rs && x.units_consumed ? `≈ ₹${(x.bill_amount_rs / x.units_consumed).toFixed(2)} per unit` : ''} delay={2.65} ready={!!x} />
        </div>
        {x && (
          <motion.p className="note" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 3 }}>
            {x.source === 'bedrock'
              ? <>Extracted by Amazon Bedrock with {Math.round((x.confidence ?? 0) * 100)}% confidence, cross-checked against {lines.length} Rekognition text lines.</>
              : x.source === 'heuristic'
                ? <>Bedrock was unavailable, so a rules-based parser read the Rekognition text instead.</>
                : <>{x.note ?? 'Showing a representative estimate.'}</>}
          </motion.p>
        )}
      </div>
    </div>
  )
}

function Readout({ cls, label, value, sub, delay, ready }: { cls: string; label: string; value: string; sub: string; delay: number; ready: boolean }) {
  return (
    <motion.div className={`kv ${cls}`} initial={{ opacity: 0.35, y: 6 }} animate={ready ? { opacity: 1, y: 0 } : { opacity: 0.35 }} transition={{ delay: ready ? delay : 0, duration: 0.4 }}>
      <span>{label}</span>
      <b>{value}</b>{sub && <small>{sub}</small>}
    </motion.div>
  )
}
