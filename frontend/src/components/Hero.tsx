import { useState } from 'react'

export type Sample = { file: string; title: string; sub: string }
export const SAMPLES: Sample[] = [
  { file: '/samples/bill_bses_delhi.jpg', title: 'BSES Rajdhani, Delhi', sub: '312 units · 3 kW load' },
  { file: '/samples/bill_msedcl_pune.jpg', title: 'MSEDCL, Pune', sub: '650 units · 5 kW load' },
  { file: '/samples/bill_bescom_bengaluru.jpg', title: 'BESCOM, Bengaluru', sub: '190 units · 2 kW load' },
]

type Props = {
  onFile: (f: File | Blob, name: string) => void
  onSample: (s: Sample) => void
  busy: boolean
}

export default function Hero({ onFile, onSample, busy }: Props) {
  const [over, setOver] = useState(false)
  return (
    <section className="hero">
      <div>
        <h1>
          Your electricity bill is already a <em>solar quote.</em>
        </h1>
        <p className="lead">
          Photograph any Indian electricity bill. In seconds you get the right rooftop size, your PM Surya Ghar subsidy,
          the real net cost, and the month you break even. Read by Amazon Rekognition, understood by Amazon Bedrock.
        </p>
        <div className="facts">
          <div><b>₹78,000</b>max central subsidy</div>
          <div><b>1 crore</b>homes targeted by 2027</div>
          <div><b>~3 yrs</b>typical payback</div>
        </div>
      </div>

      <div>
        <label
          className={`drop ${over ? 'over' : ''}`}
          onDragOver={e => { e.preventDefault(); setOver(true) }}
          onDragLeave={() => setOver(false)}
          onDrop={e => {
            e.preventDefault(); setOver(false)
            const f = e.dataTransfer.files?.[0]
            if (f) onFile(f, f.name)
          }}
        >
          <input type="file" accept="image/*" capture="environment" disabled={busy}
            onChange={e => { const f = e.target.files?.[0]; if (f) onFile(f, f.name) }} />
          <div className="icon">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
              <circle cx="12" cy="13" r="4" />
            </svg>
          </div>
          <h3>Snap or drop your bill</h3>
          <p>JPG or PNG. We never store your name or address.</p>
        </label>

        <div className="samples">
          <div className="label">or try a specimen bill</div>
          <div className="row">
            {SAMPLES.map(s => (
              <button key={s.file} className="sample" disabled={busy} onClick={() => onSample(s)}>
                <img src={s.file} alt={s.title} loading="lazy" />
                <b>{s.title}</b>
                <span>{s.sub}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
