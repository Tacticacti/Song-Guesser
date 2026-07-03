import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/svelte'
import Menu from '../src/lib/Menu.svelte'

describe('Menu', () => {
  it('starts the game when Start is clicked', async () => {
    const onStart = vi.fn()
    render(Menu, { props: { onStart, onSettings: vi.fn(), onLeaderboard: vi.fn() } })
    await fireEvent.click(screen.getByText(/Start Normal Mode/))
    expect(onStart).toHaveBeenCalledOnce()
  })

  it('opens settings when Settings is clicked', async () => {
    const onSettings = vi.fn()
    render(Menu, { props: { onStart: vi.fn(), onSettings, onLeaderboard: vi.fn() } })
    await fireEvent.click(screen.getByText(/Settings/))
    expect(onSettings).toHaveBeenCalledOnce()
  })

  it('opens the leaderboard when Leaderboard is clicked', async () => {
    const onLeaderboard = vi.fn()
    render(Menu, { props: { onStart: vi.fn(), onSettings: vi.fn(), onLeaderboard } })
    await fireEvent.click(screen.getByText(/Leaderboard/))
    expect(onLeaderboard).toHaveBeenCalledOnce()
  })

  it('shows More Modes as disabled', () => {
    render(Menu, { props: { onStart: vi.fn(), onSettings: vi.fn(), onLeaderboard: vi.fn() } })
    expect((screen.getByText(/More Modes/) as HTMLButtonElement).disabled).toBe(true)
  })
})
