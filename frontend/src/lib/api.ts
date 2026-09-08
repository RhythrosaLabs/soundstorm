const BASE = '/api'

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export async function generateAudio(prompt: string, model: string, duration: number, apiKey: string) {
  return handle<{ audio: string; format: string }>(
    await fetch(`${BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, model, duration, api_key: apiKey }),
    })
  )
}

export async function applyEffects(file: File, effects: Record<string, boolean>) {
  const form = new FormData()
  form.append('file', file)
  form.append('effects', JSON.stringify(effects))
  return handle<{ audio: string; format: string }>(
    await fetch(`${BASE}/effects`, { method: 'POST', body: form })
  )
}

export async function createSamplePack(params: {
  num_sounds: number; prefix: string; randomness: number; max_duration: number
}) {
  return handle<{ sounds: Array<{ name: string; audio: string }> }>(
    await fetch(`${BASE}/sample-pack`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    })
  )
}

export async function createDrumLoop(params: {
  tempo: number; beat_length: number;
  kick_likelihood: number; snare_likelihood: number; hihat_likelihood: number
}) {
  return handle<{ audio: string; format: string }>(
    await fetch(`${BASE}/drum-loop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    })
  )
}

export async function createMidi(params: {
  key: string; song_name: string; chord_progression: string[]
}) {
  return handle<{ midi: string; filename: string }>(
    await fetch(`${BASE}/midi`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    })
  )
}

export async function sendChat(message: string, apiKey: string) {
  return handle<{ response: string }>(
    await fetch(`${BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, api_key: apiKey }),
    })
  )
}

export async function getRandomPrompt(apiKey: string) {
  return handle<{ prompt: string }>(
    await fetch(`${BASE}/random-prompt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: apiKey }),
    })
  )
}
