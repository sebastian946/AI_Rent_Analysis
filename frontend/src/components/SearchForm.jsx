import { useState } from 'react'

const INITIAL = {
  service_type: 'arriendo',
  property_type: 'apartamento',
  price: '',
  square_meters: '40',
  vehicles: '0',
  department: '',
  ubication: '',
  locality: '',
  query: '',
}

const inputClass =
  'w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm shadow-xs outline-none ' +
  'focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 ' +
  'dark:border-slate-700 dark:bg-slate-900 dark:focus:border-blue-400'

function Field({ label, children, className = '' }) {
  return (
    <label className={`flex flex-col gap-1.5 text-sm text-slate-600 dark:text-slate-400 ${className}`}>
      <span className="font-medium">{label}</span>
      {children}
    </label>
  )
}

export default function SearchForm({ onSubmit, busy, status, error }) {
  const [form, setForm] = useState(INITIAL)

  const update = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }))

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      service_type: form.service_type,
      property_type: form.property_type,
      price: Number(form.price),
      square_meters: Number(form.square_meters),
      vehicles: Number(form.vehicles),
      department: form.department,
      ubication: form.ubication,
      locality: form.locality || null,
      query: form.query || null,
    })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="grid grid-cols-1 gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:grid-cols-2 lg:grid-cols-3 dark:border-slate-800 dark:bg-slate-900"
    >
      <Field label="Operación">
        <select name="service_type" value={form.service_type} onChange={update} className={inputClass}>
          <option value="arriendo">Arriendo</option>
          <option value="venta">Venta</option>
        </select>
      </Field>
      <Field label="Tipo de inmueble">
        <select name="property_type" value={form.property_type} onChange={update} className={inputClass}>
          <option value="apartamento">Apartamento</option>
          <option value="casa">Casa</option>
          <option value="apartaestudio">Apartaestudio</option>
        </select>
      </Field>
      <Field label="Presupuesto máximo (COP)">
        <input name="price" type="number" min="1" step="1" placeholder="2500000" required value={form.price} onChange={update} className={inputClass} />
      </Field>
      <Field label="Metros cuadrados mínimos">
        <input name="square_meters" type="number" min="1" required value={form.square_meters} onChange={update} className={inputClass} />
      </Field>
      <Field label="Vehículos">
        <input name="vehicles" type="number" min="0" required value={form.vehicles} onChange={update} className={inputClass} />
      </Field>
      <Field label="Departamento">
        <input name="department" placeholder="Antioquia" required value={form.department} onChange={update} className={inputClass} />
      </Field>
      <Field label="Ciudad o municipio">
        <input name="ubication" placeholder="Medellín" required value={form.ubication} onChange={update} className={inputClass} />
      </Field>
      <Field label="Localidad o barrio (opcional)">
        <input name="locality" placeholder="Laureles" value={form.locality} onChange={update} className={inputClass} />
      </Field>
      <Field label="Algo más que debamos saber (opcional)" className="sm:col-span-2 lg:col-span-3">
        <textarea name="query" rows={3} placeholder="Mascotas, cerca al metro, piso alto..." value={form.query} onChange={update} className={`${inputClass} resize-y`} />
      </Field>

      <div className="flex flex-wrap items-center gap-3 sm:col-span-2 lg:col-span-3">
        <button
          type="submit"
          disabled={busy}
          className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-wait disabled:opacity-60"
        >
          {busy ? 'Analizando…' : 'Analizar'}
        </button>
        {busy && (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-blue-600 dark:border-slate-700" />
        )}
        {error ? (
          <span className="text-sm text-tier-d">{error}</span>
        ) : (
          status && <span className="text-sm text-slate-500 dark:text-slate-400">{status}</span>
        )}
      </div>
    </form>
  )
}
