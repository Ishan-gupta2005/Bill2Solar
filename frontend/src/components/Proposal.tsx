import { useState } from 'react'
import type { Proposal as ProposalT, Extraction } from '../lib/api'

type Props = { proposal: ProposalT | null; loading: boolean; extraction: Extraction; onRestart: () => void }

export default function Proposal({ proposal, loading, extraction, onRestart }: Props) {
  const [lang, setLang] = useState<'hindi' | 'english'>('hindi')
  const text = proposal ? proposal[lang] : ''
  return (
    <section>
      <div className="section-title">
        <h2>Your one-page proposal</h2>
        <span>{proposal ? (proposal.source === 'bedrock' ? `written by Amazon Bedrock · ${proposal.model?.split('.').slice(-1)[0] ?? ''} · ${proposal.ms} ms` : 'template text (Bedrock unavailable)') : 'Amazon Bedrock is writing…'}</span>
      </div>
      <div className="panelbox">
        <div className="tabs no-print">
          <button className={lang === 'hindi' ? 'on' : ''} onClick={() => setLang('hindi')}>हिंदी</button>
          <button className={lang === 'english' ? 'on' : ''} onClick={() => setLang('english')}>English</button>
        </div>
        <div className={`prose ${lang}`}>
          {loading && !proposal ? (
            <>
              <span className="skeleton" style={{ width: '92%' }} /><span className="skeleton" style={{ width: '98%' }} /><span className="skeleton" style={{ width: '74%' }} />
              <span className="skeleton" style={{ width: '90%', marginTop: 22 }} /><span className="skeleton" style={{ width: '96%' }} /><span className="skeleton" style={{ width: '60%' }} />
            </>
          ) : text}
        </div>
        <div className="actions no-print">
          <button className="btn primary" onClick={() => window.print()}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
            Save proposal as PDF
          </button>
          <a className="btn" href="https://pmsuryaghar.gov.in" target="_blank" rel="noreferrer">Apply on PM Surya Ghar ↗</a>
          {extraction.discom_portal && <a className="btn ghost" href={extraction.discom_portal} target="_blank" rel="noreferrer">{extraction.discom_code ?? 'DISCOM'} net-meter portal ↗</a>}
          <button className="btn ghost" onClick={onRestart}>Scan another bill</button>
        </div>
      </div>
    </section>
  )
}
