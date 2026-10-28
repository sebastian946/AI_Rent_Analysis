import { useEffect, useRef, useState } from 'react'
import SearchForm from './components/SearchForm'
import Results from './components/Results'
import { createAnalysis, waitForAnalysis } from './api'

export default function App() {
  const [busy, setBusy] = useState(false)
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const resultsRef = useRef(null)

  useEffect(() => {
    if (analysis) resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [analysis])

  const handleSubmit = async (search) => {
    setBusy(true)
    setError('')
    setAnalysis(null)
    setStatus('Enviando búsqueda…')
    try {
      const created = await createAnalysis(search)
      const job = await waitForAnalysis(created.id, (j) => setStatus(j.message))
      setStatus(`${job.listings_count} inmuebles analizados.`)
      setAnalysis(job.result)
    } catch (err) {
      setError(err.message || 'Ocurrió un error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">AI Rent Analysis</h1>
        <p className="mt-1 text-slate-600 dark:text-slate-400">
          Cuéntanos qué tienes y qué buscas. Buscamos los inmuebles y un asesor con IA los clasifica por tiers.
        </p>
      </header>

      <main className="grid gap-6">
        <SearchForm onSubmit={handleSubmit} busy={busy} status={status} error={error} />
        {analysis && (
          <div ref={resultsRef}>
            <Results analysis={analysis} />
          </div>
        )}
      </main>
    </div>
  )
}
