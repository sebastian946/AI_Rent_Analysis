import { TIER_INFO } from '../tiers'

function BulletList({ title, items }) {
  return (
    <div>
      <h4 className="mb-1 text-xs font-semibold tracking-wide text-slate-500 uppercase dark:text-slate-400">{title}</h4>
      <ul className="list-disc space-y-0.5 pl-5 text-sm leading-relaxed">
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  )
}

export default function ListingCard({ evaluation: ev }) {
  const tier = TIER_INFO[ev.tier]
  return (
    <article className="grid gap-3 border-t border-slate-200 py-5 first:border-t-0 first:pt-0 dark:border-slate-800">
      <div className="flex flex-wrap items-center gap-3">
        <div
          title={tier.label}
          className={`grid h-11 w-11 shrink-0 place-items-center rounded-xl text-lg font-extrabold text-white ${tier.bg}`}
        >
          {ev.tier}
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-semibold">
            <a href={ev.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
              #{ev.rank} {ev.title}
            </a>
          </p>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {ev.price} · {ev.location}
          </p>
        </div>
        <span
          className={`rounded-md px-2 py-1 text-xs font-semibold ${
            ev.fits_budget ? 'bg-tier-a/15 text-tier-a' : 'bg-tier-d/15 text-tier-d'
          }`}
        >
          {ev.fits_budget ? 'Dentro del presupuesto' : 'Fuera del presupuesto'}
        </span>
        <span className="text-sm font-bold tabular-nums">{ev.score}/100</span>
      </div>

      <p className="text-sm leading-relaxed">{ev.summary}</p>

      <div className="grid gap-3 sm:grid-cols-2">
        <BulletList title="A favor" items={ev.pros} />
        <BulletList title="En contra" items={ev.cons} />
      </div>

      <p className="rounded-md border-l-4 border-blue-500 bg-slate-50 px-3 py-2 text-sm leading-relaxed dark:bg-slate-950">
        <span className="font-semibold">Asesor:</span> {ev.advisor_note}
      </p>
    </article>
  )
}
