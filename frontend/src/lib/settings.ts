const VOLUME_KEY = 'song-guesser-volume'
const AUTO_ADVANCE_KEY = 'song-guesser-auto-advance'
const AUTO_ADVANCE_DELAY_KEY = 'song-guesser-auto-advance-delay'
const PLAYER_NAME_KEY = 'song-guesser-player-name'

const DEFAULT_AUTO_ADVANCE_DELAY = 5
export const MIN_AUTO_ADVANCE_DELAY = 1
export const MAX_AUTO_ADVANCE_DELAY = 30

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

export function getAutoAdvance(): boolean {
  return localStorage.getItem(AUTO_ADVANCE_KEY) === 'true'
}

export function saveAutoAdvance(enabled: boolean): void {
  localStorage.setItem(AUTO_ADVANCE_KEY, String(enabled))
}

export function getAutoAdvanceDelay(): number {
  const stored = localStorage.getItem(AUTO_ADVANCE_DELAY_KEY)
  const parsed = stored === null ? NaN : parseInt(stored, 10)
  if (isNaN(parsed)) {
    return DEFAULT_AUTO_ADVANCE_DELAY
  }
  return Math.max(MIN_AUTO_ADVANCE_DELAY, Math.min(MAX_AUTO_ADVANCE_DELAY, parsed))
}

export function saveAutoAdvanceDelay(seconds: number): void {
  if (isNaN(seconds)) {
    return
  }
  localStorage.setItem(AUTO_ADVANCE_DELAY_KEY, String(seconds))
}

export function getPlayerName(): string {
  return localStorage.getItem(PLAYER_NAME_KEY) ?? ''
}

export function savePlayerName(name: string): void {
  localStorage.setItem(PLAYER_NAME_KEY, name)
}
