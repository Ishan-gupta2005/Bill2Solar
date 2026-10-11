import { useCallback, useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import Hero, { SAMPLES, type Sample } from './components/Hero'
import Pipeline from './components/Pipeline'
import BillScan from './components/BillScan'
import Results from './components/Results'
import Proposal from './components/Proposal'
import { analyze, apiConfigured, presign, proposal as fetchProposal, uploadToS3, API_URL, type AnalyzeResult, type Proposal as ProposalT } from './lib/api'
import { fetchAsBlob, prepareImage } from './lib/image'
import { DEMO_RESULT, DEMO_PROPOSAL } from './demo/fallback'

type Phase = 'idle' | 'uploading' | 'analyzing' | 'scanned' | 'results'

export default function App() {
  const [phase, setPhase] = useState<Phase>('idle')
  const [imageUrl, setImageUrl] = useState<string>('')
  const [result, setResult] = useState<AnalyzeResult | null>(null)
  const [prop, setProp] = useState<ProposalT | null>(null)
  const [propLoading, setPropLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const [active, setActive] = useState(0)
  const [demoMode, setDemoMode] = useState(false)
  const timers = useRef<number[]>([])

  const clearTimers = () => { timers.current.forEach(t => window.clearTimeout(t)); timers.current = [] }

  const run = useCallback(async (blob: Blob) => {
    setError(''); setResult(null); setProp(null); setDemoMode(false)
    clearTimers()
    const img = await prepareImage(blob)
    setImageUrl(img.url)
    setPhase('uploading'); setActive(0)
    // optimistic pipeline progression while we wait for the real timings
    timers.current.push(window.setTimeout(() => setActive(1), 900))
    timers.current.push(window.setTimeout(() => setActive(2), 2600))

    try {
      if (!apiConfigured) throw new Error('VITE_API_URL is not set')
      if (new URLSearchParams(window.location.search).get('offline')) throw new Error('offline mode requested')
      const { key, url } = await presign(img.blob.type)
      await uploadToS3(url, img.blob)
      setPhase('analyzing')
      const r = await analyze(key)
      clearTimers()
      setResult(r)
      setPhase('scanned')
      timers.current.push(window.setTimeout(() => setPhase('results'), 3400))
      // proposal in parallel with the reveal
      setPropLoading(true)
      fetchProposal(r.id).then(setProp).catch(e => setError(String(e))).finally(() => setPropLoading(false))
    } catch (e) {
      // Demo safety net: never show a dead screen on camera.
      console.warn('API unavailable, using demo result', e)
      clearTimers()
      setDemoMode(true)
      setResult(DEMO_RESULT)
      setPhase('scanned')
      timers.current.push(window.setTimeout(() => setPhase('results'), 3400))
      setPropLoading(true)
      timers.current.push(window.setTimeout(() => { setProp(DEMO_PROPOSAL); setPropLoading(false) }, 5200))
    }
  }, [])

  const onFile = useCallback((f: File | Blob) => { void run(f) }, [run])
  const onSample = useCallback(async (s: Sample) => { void run(await fetchAsBlob(s.file)) }, [run])
  const restart = () => { clearTimers(); setPhase('idle'); setResult(null); setProp(null); setError(''); setImageUrl('') }

  useEffect(() => () => clearTimers(), [])

  // ?demo=bses|msedcl|bescom auto-runs a specimen on load (handy for recording); &offline=1 forces the bundled fallback.
  useEffect(() => {
    const q = new URLSearchParams(window.location.search)
    const demo = q.get('demo')
    if (!demo) return
    const s = SAMPLES.find(x => x.file.includes(demo)) ?? SAMPLES[0]
    const t = window.setTimeout(() => { void onSample(s) }, 600)
    return () => window.clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const busy = phase === 'uploading' || phase === 'analyzing'
  const showScan = phase !== 'idle'
  const showResults = phase === 'results' && result

  return (
    <div className="shell">
      <header className="topbar no-print">
        <div className="brand"><div className="logo">☀</div>Bill2Solar <small>· PM Surya Ghar in one photo</small></div>
        <div style={{ display: 'flex', gap: 8 }}>
          <span className="pill aws"><span className="dot" style={{ background: 'var(--aws)', boxShadow: '0 0 0 4px rgba(255,153,0,.18)' }} />ap-southeast-2 · Rekognition · Bedrock · Lambda · DynamoDB · Amplify</span>
          <span className={`pill ${apiConfigured && !demoMode ? '' : 'warn'}`}><span className="dot" />{demoMode ? 'offline demo' : apiConfigured ? 'live' : 'no API configured'}</span>
        </div>
      </header>

      <AnimatePresence mode="wait">
        {phase === 'idle' && (
          <motion.div key="hero" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.3 }}>
            <Hero onFile={onFile} onSample={onSample} busy={busy} />
          </motion.div>
        )}
      </AnimatePresence>

      {showScan && (
        <motion.div key="scan" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <Pipeline active={active} steps={result?.pipeline} />
          {error && <div className="error no-print">{error}</div>}
          <BillScan imageUrl={imageUrl} result={result} scanning={busy} />
        </motion.div>
      )}

      {showResults && (
        <>
          <Results estimate={result.estimate} extraction={result.extraction} />
          <Proposal proposal={prop} loading={propLoading} extraction={result.extraction} onRestart={restart} />
        </>
      )}

      <footer className="footer no-print">
        <span>Built for WeMakeDevs Environmental Hacks 2026 · Waste &amp; Energy track · deployed on AWS {API_URL ? <code>{API_URL.replace('https://', '')}</code> : null}</span>
        <span>Estimates are indicative. Subsidy per MNRE CFA rules; confirm on pmsuryaghar.gov.in.</span>
      </footer>
    </div>
  )
}
