import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/svelte'
import Game from './Game.svelte'
import * as api from './api'

vi.mock('./api')

const mocked = vi.mocked(api)

async function submitYear(year: string) {
  const input = await screen.findByLabelText(/What year/)
  await fireEvent.input(input, { target: { value: year } })
  await fireEvent.click(screen.getByText('Guess'))
}

describe('Game', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    mocked.startRound.mockResolvedValue({ round_id: 'r1', preview_url: 'http://preview' })
  })

  it('starts a round and asks for the year', async () => {
    render(Game, { props: { onBackToMenu: vi.fn() } })
    expect(await screen.findByLabelText(/What year/)).toBeTruthy()
    expect(mocked.startRound).toHaveBeenCalledOnce()
  })

  it('shows hint and answer after a wrong guess', async () => {
    mocked.guessYear.mockResolvedValue({
      correct: false, points: 0, hint: 'Way off!', year: 2022, artist: 'Ado', track: 'Show',
    })
    render(Game, { props: { onBackToMenu: vi.fn() } })
    await submitYear('1990')

    expect(await screen.findByText(/Way off!/)).toBeTruthy()
    expect(screen.getByText(/This song was Show by Ado! \(2022\)/)).toBeTruthy()
    expect(screen.getByText(/Next Song/)).toBeTruthy()
    expect(mocked.guessYear).toHaveBeenCalledWith('r1', 1990)
  })

  it('enters the bonus phase after a correct guess and adds bonus points', async () => {
    mocked.guessYear.mockResolvedValue({ correct: true, points: 1, year: 2022 })
    mocked.guessBonus.mockResolvedValue({
      artist_correct: true, track_correct: false, points: 1, artist: 'Ado', track: 'Show',
    })
    render(Game, { props: { onBackToMenu: vi.fn() } })
    await submitYear('2022')

    expect(await screen.findByText(/You got it right!/)).toBeTruthy()
    await fireEvent.input(await screen.findByLabelText(/Artist name/), { target: { value: 'Ado' } })
    await fireEvent.input(screen.getByLabelText(/Song name/), { target: { value: 'Wrong' } })
    await fireEvent.click(screen.getByText(/Guess for Bonus Points/))

    expect(await screen.findByText(/This song is indeed by Ado/)).toBeTruthy()
    expect(screen.getByText(/Nope! The song was Show/)).toBeTruthy()
    // 1 point for the year + 1 bonus point for the artist
    expect(screen.getByText('2')).toBeTruthy()
    expect(mocked.guessBonus).toHaveBeenCalledWith('r1', 'Ado', 'Wrong')
  })

  it('rejects a non-numeric year without calling the API', async () => {
    render(Game, { props: { onBackToMenu: vi.fn() } })
    await submitYear('abc')

    expect(await screen.findByText(/Please enter a number!/)).toBeTruthy()
    expect(mocked.guessYear).not.toHaveBeenCalled()
  })

  it('ends the game after three wrong guesses', async () => {
    mocked.guessYear.mockResolvedValue({
      correct: false, points: 0, hint: 'Way off!', year: 2022, artist: 'Ado', track: 'Show',
    })
    render(Game, { props: { onBackToMenu: vi.fn() } })

    for (let strike = 1; strike <= 3; strike++) {
      await submitYear('1990')
      if (strike < 3) {
        await fireEvent.click(await screen.findByText(/Next Song/))
      }
    }

    await fireEvent.click(await screen.findByText(/See Final Score/))
    expect(await screen.findByText(/Game Over!/)).toBeTruthy()
    expect(screen.getByText(/Play Again/)).toBeTruthy()
  })

  it('ignores a double-click on the Guess button', async () => {
    let resolveGuess!: (value: api.GuessResult) => void
    mocked.guessYear.mockReturnValue(new Promise((resolve) => (resolveGuess = resolve)))
    render(Game, { props: { onBackToMenu: vi.fn() } })

    const input = await screen.findByLabelText(/What year/)
    await fireEvent.input(input, { target: { value: '1990' } })
    const guessButton = screen.getByText('Guess')
    await fireEvent.click(guessButton)
    await fireEvent.click(guessButton) // second click while the first request is in flight

    resolveGuess({ correct: false, points: 0, hint: 'Way off!', year: 2022, artist: 'Ado', track: 'Show' })
    expect(await screen.findByText(/Way off!/)).toBeTruthy()
    expect(mocked.guessYear).toHaveBeenCalledTimes(1)
  })

  it('shows an error screen when the server is unreachable', async () => {
    mocked.startRound.mockRejectedValue(new Error('Could not reach the game server. Is it running?'))
    render(Game, { props: { onBackToMenu: vi.fn() } })

    expect(await screen.findByText(/Could not reach the game server/)).toBeTruthy()
    expect(screen.getByText(/Try Again/)).toBeTruthy()
  })
})
