import { describe, it, expect, beforeEach } from 'vitest'
import {
  getVolume,
  saveVolume,
  getAutoAdvance,
  saveAutoAdvance,
  getAutoAdvanceDelay,
  saveAutoAdvanceDelay,
} from './settings'

describe('volume settings', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('defaults to 100 when nothing is saved', () => {
    expect(getVolume()).toBe(100)
  })

  it('round-trips a saved volume', () => {
    saveVolume(55)
    expect(getVolume()).toBe(55)
  })

  it('clamps stored values above 100', () => {
    localStorage.setItem('song-guesser-volume', '500')
    expect(getVolume()).toBe(100)
  })

  it('clamps stored values below 0', () => {
    localStorage.setItem('song-guesser-volume', '-20')
    expect(getVolume()).toBe(0)
  })

  it('falls back to 100 for garbage values', () => {
    localStorage.setItem('song-guesser-volume', 'loud')
    expect(getVolume()).toBe(100)
  })
})

describe('auto-advance settings', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('is off by default', () => {
    expect(getAutoAdvance()).toBe(false)
  })

  it('round-trips the toggle', () => {
    saveAutoAdvance(true)
    expect(getAutoAdvance()).toBe(true)
    saveAutoAdvance(false)
    expect(getAutoAdvance()).toBe(false)
  })

  it('delay defaults to 5 seconds', () => {
    expect(getAutoAdvanceDelay()).toBe(5)
  })

  it('round-trips the delay', () => {
    saveAutoAdvanceDelay(12)
    expect(getAutoAdvanceDelay()).toBe(12)
  })

  it('clamps the delay to the allowed range', () => {
    localStorage.setItem('song-guesser-auto-advance-delay', '999')
    expect(getAutoAdvanceDelay()).toBe(30)
    localStorage.setItem('song-guesser-auto-advance-delay', '0')
    expect(getAutoAdvanceDelay()).toBe(1)
  })

  it('falls back to the default for garbage values', () => {
    localStorage.setItem('song-guesser-auto-advance-delay', 'soon')
    expect(getAutoAdvanceDelay()).toBe(5)
  })

  it('ignores attempts to save NaN as the delay', () => {
    saveAutoAdvanceDelay(10)
    saveAutoAdvanceDelay(NaN)
    expect(getAutoAdvanceDelay()).toBe(10)
  })
})
