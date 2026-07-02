import { describe, it, expect, vi, beforeEach } from 'vitest'
import { getArtists, addArtist, removeArtist, startRound, guessYear, guessBonus } from './api'

const mockFetch = vi.fn()

function jsonResponse(body: unknown, ok = true) {
  return { ok, json: () => Promise.resolve(body) }
}

describe('api client', () => {
  beforeEach(() => {
    mockFetch.mockReset()
    vi.stubGlobal('fetch', mockFetch)
  })

  it('getArtists returns the artist list', async () => {
    mockFetch.mockResolvedValue(jsonResponse({ artists: ['Ado'] }))
    expect(await getArtists()).toEqual({ artists: ['Ado'] })
    expect(mockFetch).toHaveBeenCalledWith('/api/artists', expect.anything())
  })

  it('addArtist sends the name in the request body', async () => {
    mockFetch.mockResolvedValue(jsonResponse({ artists: ['Ado', 'Queen'] }))
    await addArtist('Queen')
    const [path, options] = mockFetch.mock.calls[0]
    expect(path).toBe('/api/artists')
    expect(options.method).toBe('POST')
    expect(JSON.parse(options.body)).toEqual({ name: 'Queen' })
  })

  it('removeArtist URL-encodes the artist name', async () => {
    mockFetch.mockResolvedValue(jsonResponse({ artists: [] }))
    await removeArtist('AC/DC')
    expect(mockFetch.mock.calls[0][0]).toBe('/api/artists/AC%2FDC')
  })

  it('guessYear posts to the round endpoint', async () => {
    mockFetch.mockResolvedValue(jsonResponse({ correct: true, points: 1, year: 2022 }))
    const result = await guessYear('round-1', 2022)
    expect(result.correct).toBe(true)
    const [path, options] = mockFetch.mock.calls[0]
    expect(path).toBe('/api/rounds/round-1/guess')
    expect(JSON.parse(options.body)).toEqual({ year: 2022 })
  })

  it('guessBonus maps guesses to snake_case fields', async () => {
    mockFetch.mockResolvedValue(
      jsonResponse({ artist_correct: true, track_correct: false, points: 1, artist: 'Ado', track: 'Show' }),
    )
    await guessBonus('round-1', 'Ado', 'Wrong')
    const [, options] = mockFetch.mock.calls[0]
    expect(JSON.parse(options.body)).toEqual({ artist_guess: 'Ado', track_guess: 'Wrong' })
  })

  it('startRound returns the round info', async () => {
    mockFetch.mockResolvedValue(jsonResponse({ round_id: 'r1', preview_url: 'http://p' }))
    expect(await startRound()).toEqual({ round_id: 'r1', preview_url: 'http://p' })
  })

  it('throws the backend detail message on error responses', async () => {
    mockFetch.mockResolvedValue(jsonResponse({ detail: 'Ado is already in the list!' }, false))
    await expect(addArtist('Ado')).rejects.toThrow('Ado is already in the list!')
  })

  it('throws a friendly message when the server is unreachable', async () => {
    mockFetch.mockRejectedValue(new TypeError('fetch failed'))
    await expect(getArtists()).rejects.toThrow('Could not reach the game server. Is it running?')
  })
})
