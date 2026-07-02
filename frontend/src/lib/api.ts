export interface ArtistList {
  artists: string[]
}

export interface RoundStart {
  round_id: string
  preview_url: string
}

export interface GuessResult {
  correct: boolean
  points: number
  year: number
  hint?: string
  artist?: string
  track?: string
}

export interface BonusResult {
  artist_correct: boolean
  track_correct: boolean
  points: number
  artist: string
  track: string
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(path, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    throw new Error('Could not reach the game server. Is it running?')
  }
  let body: unknown
  try {
    body = await response.json()
  } catch {
    // the server (or proxy) returned something that is not JSON
    throw new Error(`The game server returned an unexpected error (${response.status})`)
  }
  if (!response.ok) {
    // FastAPI validation errors put an object array in detail; only show plain strings
    const detail = (body as { detail?: unknown }).detail
    throw new Error(typeof detail === 'string' ? detail : 'Something went wrong!')
  }
  return body as T
}

export function getArtists(): Promise<ArtistList> {
  return request('/api/artists')
}

export function addArtist(name: string): Promise<ArtistList> {
  return request('/api/artists', { method: 'POST', body: JSON.stringify({ name }) })
}

export function removeArtist(name: string): Promise<ArtistList> {
  return request(`/api/artists/${encodeURIComponent(name)}`, { method: 'DELETE' })
}

export function startRound(): Promise<RoundStart> {
  return request('/api/rounds', { method: 'POST' })
}

export function guessYear(roundId: string, year: number): Promise<GuessResult> {
  return request(`/api/rounds/${roundId}/guess`, { method: 'POST', body: JSON.stringify({ year }) })
}

export function guessBonus(roundId: string, artistGuess: string, trackGuess: string): Promise<BonusResult> {
  return request(`/api/rounds/${roundId}/bonus`, {
    method: 'POST',
    body: JSON.stringify({ artist_guess: artistGuess, track_guess: trackGuess }),
  })
}
