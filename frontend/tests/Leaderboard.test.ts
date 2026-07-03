import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/svelte'
import Leaderboard from '../src/lib/Leaderboard.svelte'
import * as api from '../src/lib/api'

vi.mock('../src/lib/api')

const mocked = vi.mocked(api)

describe('Leaderboard screen', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('lists the scores in order with medals for the top three', async () => {
    mocked.getLeaderboard.mockResolvedValue({
      leaderboard: [
        { name: 'Champ', score: 9 },
        { name: 'Runner', score: 7 },
        { name: 'Third', score: 5 },
        { name: 'Fourth', score: 2 },
      ],
    })
    render(Leaderboard, { props: { onBack: vi.fn() } })

    expect(await screen.findByText('Champ')).toBeTruthy()
    expect(screen.getByText('🥇')).toBeTruthy()
    expect(screen.getByText('🥈')).toBeTruthy()
    expect(screen.getByText('🥉')).toBeTruthy()
    expect(screen.getByText('4.')).toBeTruthy()
  })

  it('invites the first score when the board is empty', async () => {
    mocked.getLeaderboard.mockResolvedValue({ leaderboard: [] })
    render(Leaderboard, { props: { onBack: vi.fn() } })

    expect(await screen.findByText(/No scores yet/)).toBeTruthy()
  })

  it('shows an error with a retry button when loading fails', async () => {
    mocked.getLeaderboard
      .mockRejectedValueOnce(new Error('Could not reach the game server. Is it running?'))
      .mockResolvedValueOnce({ leaderboard: [{ name: 'Ed', score: 3 }] })
    render(Leaderboard, { props: { onBack: vi.fn() } })

    expect(await screen.findByText(/Could not reach the game server/)).toBeTruthy()
    await fireEvent.click(screen.getByText(/Try Again/))
    expect(await screen.findByText('Ed')).toBeTruthy()
  })

  it('goes back to the menu', async () => {
    mocked.getLeaderboard.mockResolvedValue({ leaderboard: [] })
    const onBack = vi.fn()
    render(Leaderboard, { props: { onBack } })

    await fireEvent.click(screen.getByText(/Back to Menu/))
    expect(onBack).toHaveBeenCalledOnce()
  })
})
