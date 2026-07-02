<script lang="ts">
  import { startRound, guessYear, guessBonus } from './api'
  import { getVolume, saveVolume } from './settings'

  const MAX_STRIKES = 3

  type Phase = 'loading' | 'guessing' | 'bonus' | 'reveal' | 'gameover' | 'error'

  let { onBackToMenu }: { onBackToMenu: () => void } = $props()

  let phase: Phase = $state('loading')
  let score = $state(0)
  let strikes = $state(0)
  let roundId = $state('')
  let previewUrl = $state('')
  let yearInput = $state('')
  let artistInput = $state('')
  let trackInput = $state('')
  let messages: string[] = $state([])
  let errorMessage = $state('')
  let volume = $state(getVolume())
  let audio: HTMLAudioElement | undefined = $state()
  let submitting = $state(false)

  $effect(() => {
    if (audio) {
      audio.volume = volume / 100
    }
    saveVolume(volume)
  })

  $effect(() => {
    if (audio && previewUrl) {
      audio.play().catch(() => {
        // autoplay can be blocked before the first user interaction;
        // the player controls still allow starting playback manually
      })
    }
  })

  async function nextSong() {
    phase = 'loading'
    messages = []
    yearInput = ''
    artistInput = ''
    trackInput = ''
    try {
      const round = await startRound()
      roundId = round.round_id
      previewUrl = round.preview_url
      phase = 'guessing'
    } catch (error) {
      errorMessage = (error as Error).message
      phase = 'error'
    }
  }

  async function submitYear(event: SubmitEvent) {
    event.preventDefault()
    if (submitting) return
    const year = parseInt(yearInput, 10)
    if (isNaN(year)) {
      messages = ['Please enter a number!']
      return
    }
    submitting = true
    audio?.pause()
    try {
      const result = await guessYear(roundId, year)
      if (result.correct) {
        score += result.points
        messages = ['🎉 You got it right!', 'Guess the artist and song name for bonus points!']
        phase = 'bonus'
      } else {
        strikes += 1
        messages = [
          `❌ ${result.hint}`,
          `This song was ${result.track} by ${result.artist}! (${result.year})`,
        ]
        phase = 'reveal'
      }
    } catch (error) {
      errorMessage = (error as Error).message
      phase = 'error'
    } finally {
      submitting = false
    }
  }

  async function submitBonus(event: SubmitEvent) {
    event.preventDefault()
    if (submitting) return
    submitting = true
    try {
      const result = await guessBonus(roundId, artistInput, trackInput)
      score += result.points
      messages = [
        result.artist_correct
          ? `✅ You are right! This song is indeed by ${result.artist}!`
          : `❌ Nope! This song is by ${result.artist}!`,
        result.track_correct
          ? `✅ That's right! The song was ${result.track}!`
          : `❌ Nope! The song was ${result.track}!`,
      ]
      phase = 'reveal'
    } catch (error) {
      errorMessage = (error as Error).message
      phase = 'error'
    } finally {
      submitting = false
    }
  }

  function continueGame() {
    if (strikes >= MAX_STRIKES) {
      phase = 'gameover'
    } else {
      nextSong()
    }
  }

  function restart() {
    score = 0
    strikes = 0
    nextSong()
  }

  nextSong()
</script>

<div class="card">
  <div class="status">
    <span>Score: <strong>{score}</strong></span>
    <span class="strikes">
      {#each { length: MAX_STRIKES } as _, i}
        <span class={i < strikes ? 'strike used' : 'strike'}>✕</span>
      {/each}
    </span>
  </div>

  {#if phase === 'loading'}
    <p class="center">🎵 Finding a song...</p>
  {:else if phase === 'error'}
    <p class="message error">{errorMessage}</p>
    <div class="actions">
      <button onclick={nextSong}>Try Again</button>
      <button class="secondary" onclick={onBackToMenu}>Back to Menu</button>
    </div>
  {:else if phase === 'gameover'}
    <h2 class="center">Game Over!</h2>
    <p class="center">Your final score was: <strong class="final-score">{score}</strong></p>
    <div class="actions">
      <button onclick={restart}>Play Again</button>
      <button class="secondary" onclick={onBackToMenu}>Back to Menu</button>
    </div>
  {:else}
    <audio bind:this={audio} src={previewUrl} controls></audio>
    <label class="volume">
      🔊 Volume ({volume}%)
      <input type="range" min="0" max="100" bind:value={volume} />
    </label>

    {#each messages as message}
      <p class="message">{message}</p>
    {/each}

    {#if phase === 'guessing'}
      <form onsubmit={submitYear}>
        <label for="year">What year did this song come out?</label>
        <div class="row">
          <input id="year" type="number" placeholder="e.g. 2016" bind:value={yearInput} />
          <button type="submit" disabled={submitting}>Guess</button>
        </div>
      </form>
    {:else if phase === 'bonus'}
      <form onsubmit={submitBonus}>
        <label for="artist">Artist name</label>
        <input id="artist" type="text" placeholder="Who sings this?" bind:value={artistInput} />
        <label for="track">Song name</label>
        <input id="track" type="text" placeholder="What's it called?" bind:value={trackInput} />
        <div class="actions">
          <button type="submit" disabled={submitting}>Guess for Bonus Points</button>
        </div>
      </form>
    {:else if phase === 'reveal'}
      <div class="actions">
        <button onclick={continueGame}>
          {strikes >= MAX_STRIKES ? 'See Final Score' : 'Next Song ▶'}
        </button>
      </div>
    {/if}
  {/if}
</div>

<button class="secondary quit" onclick={onBackToMenu}>Quit to Menu</button>

<style>
  .status {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .strike {
    color: var(--border);
    font-size: 1.2rem;
    margin-left: 0.3rem;
  }

  .strike.used {
    color: var(--danger);
  }

  audio {
    width: 100%;
    margin-bottom: 0.75rem;
  }

  .volume {
    display: block;
    color: var(--text-dim);
    font-size: 0.9rem;
    margin-bottom: 1rem;
  }

  .message {
    background: var(--bg-input);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    padding: 0.6rem 0.8rem;
    margin: 0.5rem 0;
  }

  .message.error {
    border-left-color: var(--danger);
  }

  form label {
    display: block;
    margin: 0.75rem 0 0.35rem;
    color: var(--text-dim);
  }

  .row {
    display: flex;
    gap: 0.5rem;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
  }

  .center {
    text-align: center;
  }

  .final-score {
    font-size: 1.5rem;
    color: var(--warning);
  }

  .quit {
    margin-top: 1rem;
    width: 100%;
  }
</style>
