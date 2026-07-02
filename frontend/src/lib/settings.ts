const VOLUME_KEY = 'song-guesser-volume'

export function getVolume(): number {
  const stored = localStorage.getItem(VOLUME_KEY)
  const parsed = stored === null ? NaN : parseInt(stored, 10)
  if (isNaN(parsed)) {
    return 100
  }
  return Math.max(0, Math.min(100, parsed))
}

export function saveVolume(volume: number): void {
  localStorage.setItem(VOLUME_KEY, String(volume))
}
