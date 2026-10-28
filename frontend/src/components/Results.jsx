import { useMemo, useState } from 'react'
import { TIERS, TIER_INFO } from '../tiers'
import ListingCard from './ListingCard'

function Card({ title, children }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      {title && <h3 className="mb-3 text-lg font-semibold">{title}</h3>}
      {children}
    </section>
  )
}

export default function Results({ analysis }) {
  const [activeTier, setActiveTier] = useState('all')

  const counts = useMemo(() => {
    const c = {}
    for (const ev of analysis.evaluations) c[ev.tier] = (c[ev.tier] || 0) + 1
    return c
  }, [analysis])

  const visible = analysis.evaluations.filter((ev) => activeTier === 'all' || ev.tier === activeTier)

  const chip = (value, label) => {
    const active = activeTier === value
    return (
      <button
        key={value}
        type="button"
        onClick={() => setActiveTier(value)}
        className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
          active
            ? 'border-slate-900 bg-slate-900 text-white dark:border-white dark:bg-white dark:text-slate-900'
            : 'border-slate-300 hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800'
        }`}
      >
        {label}
      </button>
    )
  }

  return (
    <div className="grid gap-5">
      <Card>
        <p className="mb-2 text-xl font-bold">{analysis.headline}</p>
        <p className="leading-relaxed text-slate-600 dark:text-slate-400">{analysis.market_overview}</p>
      </Card>

      <Card title="Ranking por tiers">
        <div className="mb-4 flex flex-wrap gap-2">
          {chip('all', `Todos (${analysis.evaluations.length})`)}
          {TIERS.filter((t) => counts[t]).map((t) => chip(t, `${t} · ${TIER_INFO[t].label} (${counts[t]})`))}
        </div>
        {visible.length ? (
          visible.map((ev) => <ListingCard key={ev.rank} evaluation={ev} />)
        ) : (
          <p className="text-sm text-slate-500">No hay inmuebles en este tier.</p>
        )}
      </Card>

      <Card title="Recomendación principal">
        <p className="leading-relaxed">{analysis.top_recommendation}</p>
      </Card>

      <Card title="Consejos del asesor">
        <ul className="list-disc space-y-1 pl-5 leading-relaxed">
          {analysis.advice.map((tip, i) => (
            <li key={i}>{tip}</li>
          ))}
        </ul>
        {analysis.missing_info.length > 0 && (
          <>
            <h4 className="mt-4 mb-1 text-sm font-semibold">Para afinar la búsqueda</h4>
            <ul className="list-disc space-y-1 pl-5 text-sm leading-relaxed">
              {analysis.missing_info.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </>
        )}
      </Card>
    </div>
  )
}
