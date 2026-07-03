import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/svelte'
import Settings from '../src/lib/Settings.svelte'
import * as api from '../src/lib/api'
import { getAutoAdvance, saveAutoAdvance } from '../src/lib/settings'

vi.mock('../src/lib/api')

const mocked = vi.mocked(api)

describe('Settings screen', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    mocked.getArtists.mockResolvedValue({ artists: ['Ado'] })
  })

  it('persists the auto-advance toggle', async () => {
    render(Settings, { props: { onBack: vi.fn() } })
    const toggle = screen.getByLabelText(/Automatically play the next song/)

    await fireEvent.click(toggle)
    expect(getAutoAdvance()).toBe(true)

    await fireEvent.click(toggle)
    expect(getAutoAdvance()).toBe(false)
  })

  it('only shows the delay slider when auto-advance is on', async () => {
    render(Settings, { props: { onBack: vi.fn() } })
    expect(screen.queryByText(/Delay before the next song/)).toBeNull()

    await fireEvent.click(screen.getByLabelText(/Automatically play the next song/))
    expect(screen.getByText(/Delay before the next song \(5s\)/)).toBeTruthy()
  })

  it('reflects a previously saved toggle state', async () => {
    saveAutoAdvance(true)
    render(Settings, { props: { onBack: vi.fn() } })
    const toggle = screen.getByLabelText(/Automatically play the next song/) as HTMLInputElement
    expect(toggle.checked).toBe(true)
    expect(screen.getByText(/Delay before the next song/)).toBeTruthy()
  })
})
