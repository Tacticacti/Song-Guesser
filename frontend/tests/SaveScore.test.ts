import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/svelte'
import SaveScore from '../src/lib/SaveScore.svelte'
import * as api from '../src/lib/api'
import { getPlayerName, savePlayerName } from '../src/lib/settings'

vi.mock('../src/lib/api')

const mocked = vi.mocked(api)

describe('SaveScore', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('submits the trimmed name with the score and remembers the name', async () => {
    mocked.submitScore.mockResolvedValue({
      new_best: true,
      best_score: 4,
      leaderboard: [{ name: 'Ed', score: 4 }],
    })
    render(SaveScore, { props: { score: 4 } })

    await fireEvent.input(screen.getByLabelText(/Save your score/), { target: { value: '  Ed  ' } })
    await fireEvent.click(screen.getByText('Save Score'))

    expect(mocked.submitScore).toHaveBeenCalledWith('Ed', 4)
    expect(await screen.findByText(/New high score!/)).toBeTruthy()
    expect(getPlayerName()).toBe('Ed')
  })

  it('shows the existing record when the score is not a new best', async () => {
    mocked.submitScore.mockResolvedValue({
      new_best: false,
      best_score: 9,
      leaderboard: [{ name: 'Ed', score: 9 }],
    })
    render(SaveScore, { props: { score: 4 } })

    await fireEvent.input(screen.getByLabelText(/Save your score/), { target: { value: 'Ed' } })
    await fireEvent.click(screen.getByText('Save Score'))

    expect(await screen.findByText(/your record is still 9/)).toBeTruthy()
    expect(screen.queryByText(/New high score/)).toBeNull()
  })

  it('shows the saved leaderboard after submitting', async () => {
    mocked.submitScore.mockResolvedValue({
      new_best: true,
      best_score: 4,
      leaderboard: [
        { name: 'Champ', score: 9 },
        { name: 'Ed', score: 4 },
      ],
    })
    render(SaveScore, { props: { score: 4 } })

    await fireEvent.input(screen.getByLabelText(/Save your score/), { target: { value: 'Ed' } })
    await fireEvent.click(screen.getByText('Save Score'))

    expect(await screen.findByText('Champ')).toBeTruthy()
    expect(screen.getByText('Ed')).toBeTruthy()
    // the form is gone once the score is saved, so it cannot be submitted twice
    expect(screen.queryByText('Save Score')).toBeNull()
  })

  it('rejects a blank name without calling the API', async () => {
    render(SaveScore, { props: { score: 4 } })

    await fireEvent.input(screen.getByLabelText(/Save your score/), { target: { value: '   ' } })
    await fireEvent.click(screen.getByText('Save Score'))

    expect(await screen.findByText(/Please enter a name!/)).toBeTruthy()
    expect(mocked.submitScore).not.toHaveBeenCalled()
  })

  it('prefills the name used last time', () => {
    savePlayerName('Ed')
    render(SaveScore, { props: { score: 4 } })
    expect((screen.getByLabelText(/Save your score/) as HTMLInputElement).value).toBe('Ed')
  })

  it('keeps the form and shows the error when saving fails', async () => {
    mocked.submitScore.mockRejectedValue(new Error('Could not reach the game server. Is it running?'))
    render(SaveScore, { props: { score: 4 } })

    await fireEvent.input(screen.getByLabelText(/Save your score/), { target: { value: 'Ed' } })
    await fireEvent.click(screen.getByText('Save Score'))

    expect(await screen.findByText(/Could not reach the game server/)).toBeTruthy()
    expect(screen.getByText('Save Score')).toBeTruthy()
  })
})
