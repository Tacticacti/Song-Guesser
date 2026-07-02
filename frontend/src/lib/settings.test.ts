import { describe, it, expect, beforeEach } from 'vitest'
import { getVolume, saveVolume } from './settings'

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
