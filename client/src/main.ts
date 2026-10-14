type Deployment = {
  commit: string
  branch: string
  image_tag: string
  container_id: string
  url: string
  status: 'live' | 'superseded' | 'failed'
  detail: string
  at: string
}

type Status = {
  current: Deployment | null
  history: Deployment[]
}

const POLL_MS = 5000

const currentEl = document.querySelector<HTMLDivElement>('#status')!
const historyEl = document.querySelector<HTMLDivElement>('#history')!

async function fetchStatus(): Promise<Status> {
  const res = await fetch('/api/status')
  if (!res.ok) throw new Error(`server said ${res.status}`)
  return res.json()
}

// detail carries server-side exception text, so nothing goes in as raw html
function escape(value: string): string {
  const node = document.createElement('div')
  node.textContent = value
  return node.innerHTML
}

function card(deployment: Deployment): string {
  const detail = deployment.detail
    ? `<p class="detail">${escape(deployment.detail)}</p>`
    : ''
  const link =
    deployment.status === 'live'
      ? `<a href="${escape(deployment.url)}">${escape(deployment.url)}</a>`
      : ''

  return `
    <div class="card ${escape(deployment.status)}">
      <div class="head">
        <code>${escape(deployment.commit)}</code>
        <span class="badge">${escape(deployment.status)}</span>
      </div>
      <p class="meta">${escape(deployment.branch)} · ${escape(deployment.at)}</p>
      ${detail}
      ${link}
    </div>`
}

function render(status: Status): void {
  currentEl.className = status.current ? '' : 'empty'
  currentEl.innerHTML = status.current
    ? card(status.current)
    : 'nothing deployed yet'

  historyEl.className = status.history.length ? '' : 'empty'
  historyEl.innerHTML = status.history.length
    ? status.history.map(card).join('')
    : 'no previous deploys'
}

function fail(error: unknown): void {
  currentEl.className = 'empty'
  currentEl.textContent = `can't reach the server (${String(error)})`
}

async function tick(): Promise<void> {
  try {
    render(await fetchStatus())
  } catch (error) {
    fail(error)
  }
}

tick()
setInterval(tick, POLL_MS)
