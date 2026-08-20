type Deployment = {
  commit: string
  branch: string
  image_tag: string
  container_id: string
  url: string
}

const container = document.querySelector<HTMLDivElement>('#status')!

async function fetchStatus(): Promise<Deployment | null> {
  const res = await fetch('/api/status')
  if (!res.ok) throw new Error(`server said ${res.status}`)
  return res.json()
}

function render(deployment: Deployment | null): void {
  console.log('live right now:', deployment)
}

fetchStatus().then(render)
