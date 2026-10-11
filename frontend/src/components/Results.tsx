import { motion } from 'framer-motion'
import type { Estimate, Extraction } from '../lib/api'
import { useCountUp, inr, num } from '../lib/useCountUp'
import Rooftop from './Rooftop'

type Props = { estimate: Estimate; extraction: Extraction }

export default function Results({ estimate: e, extraction: x }: Props) {
  const kw = useCountUp(e.recommended_kw, 1200, 100)
  const subsidy = useCountUp(e.subsidy_rs, 1400, 300)
  const net = useCountUp(e.net_cost_rs, 1400, 500)
  const saving = useCountUp(e.monthly_savings_rs, 1400, 700)
  const payback = useCountUp(e.payback_years, 1400, 900)
  const co2 = useCountUp(e.co2_tonnes_per_year, 1400, 1100)
  const trees = useCountUp(e.trees_equivalent, 1400, 1200)
  const life = useCountUp(e.lifetime_savings_rs, 1600, 1300)

  return (
    <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <div className="section-title">
        <h2>Your rooftop solar plan</h2>
        <span>sized to cover {e.coverage_percent}% of {num(e.monthly_units)} units a month · {x.discom ?? 'your DISCOM'}</span>
      </div>

      <div className="cards">
        <div className="card hero-card">
          <div className="badge">Recommended</div>
          <div className="lbl">System size</div>
          <div className="val">{kw.toFixed(1)}<small>kW</small></div>
          <div className="sub">{e.panel_count} panels · generates ≈ {num(e.monthly_generation_units)} units / month</div>
        </div>
        <div className="card green">
          <div className="lbl">PM Surya Ghar subsidy</div>
          <div className="val">{inr(subsidy)}</div>
          <div className="sub">paid directly to your bank account</div>
        </div>
        <div className="card">
          <div className="lbl">Your net cost</div>
          <div className="val"><span className="strike">{inr(e.gross_cost_rs)}</span>{inr(net)}</div>
          <div className="sub">after subsidy · ₹{num(e.assumptions.installed_cost_rs_per_kw as number)} per kW installed</div>
        </div>

        <div className="card">
          <div className="lbl">Monthly saving</div>
          <div className="val">{inr(saving)}</div>
          <div className="sub">at ₹{e.effective_tariff_rs_per_unit} per unit · {inr(e.annual_savings_rs)} a year</div>
        </div>
        <div className="card">
          <div className="lbl">Payback</div>
          <div className="val">{payback.toFixed(1)}<small>years</small></div>
          <div className="sub">then ~20 more years of free power</div>
        </div>
        <div className="card green">
          <div className="lbl">CO₂ avoided every year</div>
          <div className="val">{co2.toFixed(2)}<small>tonnes</small></div>
          <div className="sub">= {Math.round(trees)} trees working full time</div>
        </div>
        <div className="card">
          <div className="lbl">25-year net benefit</div>
          <div className="val">{inr(life)}</div>
          <div className="sub">after paying for the system</div>
        </div>
      </div>

      <div className="twocol">
        <div className="panelbox">
          <h3>How it sits on your roof</h3>
          <p className="hint">Indicative layout. A vendor will survey shadows from tanks, parapets and neighbours.</p>
          <Rooftop panels={e.panel_count} kw={e.recommended_kw} sqft={e.roof_sqft_needed} />
        </div>
        <div className="panelbox">
          <h3>How we got here</h3>
          <p className="hint">Every number is auditable. Change any assumption and the plan moves with it.</p>
          <table className="mono" style={{ width: '100%', fontSize: 13, borderCollapse: 'collapse' }}>
            <tbody>
              {[
                ['Yield', `${e.assumptions.units_per_kw_per_day} units / kW / day`],
                ['Roof needed', `${e.assumptions.roof_sqft_per_kw} sq ft per kW`],
                ['Installed cost', `₹${num(e.assumptions.installed_cost_rs_per_kw as number)} per kW`],
                ['Subsidy rule', '₹30k/kW to 2 kW, ₹18k for 3rd kW, cap ₹78k'],
                ['Export credit', `₹${e.assumptions.export_rate_rs_per_unit} per surplus unit`],
                ['Grid CO₂', `${e.assumptions.grid_co2_kg_per_kwh} kg per unit (CEA)`],
                ['Panel', `${e.assumptions.panel_watt} W mono-PERC, 0.6%/yr degradation`],
              ].map(([k, v]) => (
                <tr key={k} style={{ borderTop: '1px solid var(--line)' }}>
                  <td style={{ padding: '8px 0', color: 'var(--muted)', fontFamily: 'var(--font)' }}>{k}</td>
                  <td style={{ padding: '8px 0', textAlign: 'right' }}>{v}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.section>
  )
}
