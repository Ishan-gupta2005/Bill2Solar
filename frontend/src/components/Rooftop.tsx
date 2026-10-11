import { motion } from 'framer-motion'

type Props = { panels: number; kw: number; sqft: number }

/** Top-down stylised rooftop with panels landing row by row. */
export default function Rooftop({ panels, kw, sqft }: Props) {
  const n = Math.max(1, Math.min(panels, 24))
  const cols = Math.min(6, Math.ceil(Math.sqrt(n * 1.5)))
  const rows = Math.ceil(n / cols)
  const W = 420, H = 300
  const roof = { x: 40, y: 50, w: 340, h: 210 }
  const pw = 44, ph = 26, gap = 7
  const gridW = cols * pw + (cols - 1) * gap
  const gridH = rows * ph + (rows - 1) * gap
  const ox = roof.x + (roof.w - gridW) / 2
  const oy = roof.y + (roof.h - gridH) / 2 + 8

  return (
    <div className="roof">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${panels} solar panels on the roof`}>
        <defs>
          <linearGradient id="roofg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#3a4452" />
            <stop offset="1" stopColor="#262e3a" />
          </linearGradient>
          <linearGradient id="cell" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#1d3a8a" />
            <stop offset="1" stopColor="#0b1e4d" />
          </linearGradient>
          <radialGradient id="sun" cx="0.5" cy="0.5" r="0.5">
            <stop offset="0" stopColor="#ffd34d" />
            <stop offset="0.6" stopColor="#f5b700" />
            <stop offset="1" stopColor="#f5b700" stopOpacity="0" />
          </radialGradient>
        </defs>
        {/* ground */}
        <rect x="0" y="0" width={W} height={H} rx="16" fill="#101620" />
        <rect x="12" y="12" width={W - 24} height={H - 24} rx="12" fill="#17391f" opacity="0.55" />
        {/* sun */}
        <motion.circle cx={W - 46} cy="44" r="26" fill="url(#sun)" initial={{ scale: 0.6, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.8 }} />
        {/* parapet + roof slab */}
        <rect x={roof.x - 8} y={roof.y - 8} width={roof.w + 16} height={roof.h + 16} rx="10" fill="#4b5563" />
        <rect x={roof.x} y={roof.y} width={roof.w} height={roof.h} rx="6" fill="url(#roofg)" />
        {/* water tank + stair head, the two things on every Indian roof */}
        <circle cx={roof.x + 34} cy={roof.y + 36} r="18" fill="#111827" stroke="#6b7280" strokeWidth="2" />
        <circle cx={roof.x + 34} cy={roof.y + 36} r="9" fill="#1f2937" />
        <rect x={roof.x + roof.w - 70} y={roof.y + roof.h - 56} width="54" height="40" rx="4" fill="#111827" stroke="#6b7280" strokeWidth="2" />
        {/* panels */}
        {Array.from({ length: n }).map((_, i) => {
          const r = Math.floor(i / cols), c = i % cols
          const x = ox + c * (pw + gap), y = oy + r * (ph + gap)
          return (
            <motion.g key={i} initial={{ opacity: 0, y: -40, scale: 0.6 }} animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ delay: 0.5 + i * 0.09, type: 'spring', bounce: 0.3, duration: 0.6 }}>
              <rect x={x} y={y} width={pw} height={ph} rx="2.5" fill="url(#cell)" stroke="#8fb3ff" strokeWidth="1.2" />
              {[1, 2, 3].map(k => <line key={k} x1={x + (pw / 4) * k} y1={y} x2={x + (pw / 4) * k} y2={y + ph} stroke="#2f55b8" strokeWidth="0.8" />)}
              <line x1={x} y1={y + ph / 2} x2={x + pw} y2={y + ph / 2} stroke="#2f55b8" strokeWidth="0.8" />
              <rect x={x + 3} y={y + 3} width={pw * 0.35} height={ph * 0.25} rx="1" fill="#fff" opacity="0.14" />
            </motion.g>
          )
        })}
        <motion.text x={roof.x} y={H - 14} fill="#94a3b8" fontSize="12" fontFamily="Inter, sans-serif" fontWeight="600"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 + n * 0.09 }}>
          {panels} × 540 W panels · {kw} kW · ≈ {sqft} sq ft shadow-free roof
        </motion.text>
      </svg>
    </div>
  )
}
