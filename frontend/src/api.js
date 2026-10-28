const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

async function request(path, options) {
  const res = await fetch(path, options)
  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    const detail = Array.isArray(body.detail)
      ? body.detail.map((d) => `${d.loc.at(-1)}: ${d.msg}`).join('; ')
      : body.detail || res.statusText
    throw new Error(detail)
  }
  return body
}

export function createAnalysis(search) {
  return request('/api/analyses', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(search),
  })
}

export function getAnalysis(id) {
  return request(`/api/analyses/${id}`)
}

/** Hace polling del trabajo hasta que termine. Llama onProgress con cada estado. */
export async function waitForAnalysis(id, onProgress, intervalMs = 2500) {
  for (;;) {
    const job = await getAnalysis(id)
    onProgress?.(job)
    if (job.status === 'done') return job
    if (job.status === 'error') throw new Error(job.error || job.message)
    await sleep(intervalMs)
  }
}
