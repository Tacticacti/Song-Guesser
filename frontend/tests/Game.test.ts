import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/svelte'
import Game from '../src/lib/Game.svelte'
import * as api from '../src/lib/api'
import { getVolume, saveVolume, saveAutoAdvance, saveAutoAdvanceDelay } from '../src/lib/settings'

vi.mock('../src/lib/api')

const mocked = vi.mocked(api)
const pauseMock = window.HTMLMediaElement.prototype.pause as ReturnType<typeof vi.fn>

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

  it('applies the saved volume when a song starts', async () => {
    saveVolume(40)
    const { container } = render(Game, { props: { onBackToMenu: vi.fn() } })
    await screen.findByLabelText(/What year/)

    const audio = container.querySelector('audio')!
    expect(audio.volume).toBeCloseTo(0.4)
  })

  it('persists volume changes made on the native player control', async () => {
    const { container } = render(Game, { props: { onBackToMenu: vi.fn() } })
    await screen.findByLabelText(/What year/)

    const audio = container.querySelector('audio')!
    audio.volume = 0.3
    await fireEvent(audio, new Event('volumechange'))

    expect(getVolume()).toBe(30)
  })

  it('keeps the music playing through the bonus round after a correct guess', async () => {
    mocked.guessYear.mockResolvedValue({ correct: true, points: 1, year: 2022 })
    mocked.guessBonus.mockResolvedValue({
      artist_correct: true, track_correct: true, points: 2, artist: 'Ado', track: 'Show',
    })
    render(Game, { props: { onBackToMenu: vi.fn() } })
    await submitYear('2022')

    expect(await screen.findByText(/You got it right!/)).toBeTruthy()
    expect(pauseMock).not.toHaveBeenCalled()

    // still playing while the bonus result is revealed
    await fireEvent.input(await screen.findByLabelText(/Artist name/), { target: { value: 'Ado' } })
    await fireEvent.input(screen.getByLabelText(/Song name/), { target: { value: 'Show' } })
    await fireEvent.click(screen.getByText(/Guess for Bonus Points/))
    expect(await screen.findByText(/This song is indeed by Ado/)).toBeTruthy()
    expect(pauseMock).not.toHaveBeenCalled()
  })

  it('stops the music after a wrong guess', async () => {
    mocked.guessYear.mockResolvedValue({
      correct: false, points: 0, hint: 'Way off!', year: 2022, artist: 'Ado', track: 'Show',
    })
    render(Game, { props: { onBackToMenu: vi.fn() } })
    await submitYear('1990')

    await screen.findByText(/Way off!/)
    expect(pauseMock).toHaveBeenCalled()
  })

  it('stops the music when leaving the game screen', async () => {
    const { unmount } = render(Game, { props: { onBackToMenu: vi.fn() } })
    await screen.findByLabelText(/What year/)

    expect(pauseMock).not.toHaveBeenCalled()
    unmount()
    expect(pauseMock).toHaveBeenCalled()
  })

  it('stops the music when a guess fails with a server error', async () => {
    mocked.guessYear.mockRejectedValue(new Error('Could not reach the game server. Is it running?'))
    render(Game, { props: { onBackToMenu: vi.fn() } })
    await submitYear('1990')

    await screen.findByText(/Could not reach the game server/)
    expect(pauseMock).toHaveBeenCalled()
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

describe('Game auto-advance', () => {
  const wrongGuess = {
    correct: false, points: 0, hint: 'Way off!', year: 2022, artist: 'Ado', track: 'Show',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    vi.useFakeTimers()
    mocked.startRound.mockResolvedValue({ round_id: 'r1', preview_url: 'http://preview' })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  async function revealAfterWrongGuess() {
    mocked.guessYear.mockResolvedValue(wrongGuess)
    const rendered = render(Game, { props: { onBackToMenu: vi.fn() } })
    await vi.advanceTimersByTimeAsync(0) // resolve startRound
    const input = screen.getByLabelText(/What year/)
    await fireEvent.input(input, { target: { value: '1990' } })
    await fireEvent.click(screen.getByText('Guess'))
    await vi.advanceTimersByTimeAsync(0) // resolve guessYear
    expect(screen.getByText(/Way off!/)).toBeTruthy()
    return rendered
  }

  it('automatically starts the next song after the configured delay', async () => {
    saveAutoAdvance(true)
    saveAutoAdvanceDelay(3)
    await revealAfterWrongGuess()

    expect(screen.getByRole('status').textContent).toContain('Next song in 3s')
    expect(mocked.startRound).toHaveBeenCalledTimes(1)

    await vi.advanceTimersByTimeAsync(2000)
    expect(screen.getByRole('status').textContent).toContain('Next song in 1s')
    expect(mocked.startRound).toHaveBeenCalledTimes(1)

    await vi.advanceTimersByTimeAsync(1000)
    expect(mocked.startRound).toHaveBeenCalledTimes(2)
  })

  it('does not auto-advance when the toggle is off', async () => {
    await revealAfterWrongGuess()

    expect(screen.queryByRole('status')).toBeNull()
    await vi.advanceTimersByTimeAsync(60000)
    expect(mocked.startRound).toHaveBeenCalledTimes(1)
  })

  it('clicking Next Song early cancels the timer so the song does not skip twice', async () => {
    saveAutoAdvance(true)
    saveAutoAdvanceDelay(3)
    await revealAfterWrongGuess()

    await fireEvent.click(screen.getByText(/Next Song/))
    await vi.advanceTimersByTimeAsync(0)
    expect(mocked.startRound).toHaveBeenCalledTimes(2)

    await vi.advanceTimersByTimeAsync(60000)
    expect(mocked.startRound).toHaveBeenCalledTimes(2)
  })

  it('quitting the game cancels a pending auto-advance', async () => {
    saveAutoAdvance(true)
    saveAutoAdvanceDelay(3)
    const { unmount } = await revealAfterWrongGuess()

    unmount()
    await vi.advanceTimersByTimeAsync(60000)
    expect(mocked.startRound).toHaveBeenCalledTimes(1)
  })

  it('auto-advances to the game over screen on the final strike', async () => {
    saveAutoAdvance(true)
    saveAutoAdvanceDelay(2)
    mocked.guessYear.mockResolvedValue(wrongGuess)
    render(Game, { props: { onBackToMenu: vi.fn() } })

    for (let strike = 1; strike <= 3; strike++) {
      await vi.advanceTimersByTimeAsync(0)
      const input = screen.getByLabelText(/What year/)
      await fireEvent.input(input, { target: { value: '1990' } })
      await fireEvent.click(screen.getByText('Guess'))
      await vi.advanceTimersByTimeAsync(0)
      if (strike === 3) {
        // the final countdown leads to the score screen, and says so
        expect(screen.getByRole('status').textContent).toContain('Final score in 2s')
      }
      await vi.advanceTimersByTimeAsync(2000) // countdown elapses
    }

    expect(screen.getByText(/Game Over!/)).toBeTruthy()
    expect(mocked.startRound).toHaveBeenCalledTimes(3)
  })
})
