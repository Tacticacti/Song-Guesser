<script lang="ts">
  import { submitScore, type ScoreResult } from './api'
  import { getPlayerName, savePlayerName } from './settings'
  import ScoreList from './ScoreList.svelte'

  let { score }: { score: number } = $props()

  // start from the name used last time so returning players keep their entry
  let name = $state(getPlayerName())
  let result: ScoreResult | null = $state(null)
  let error = $state('')
  let submitting = $state(false)

  async function save(event: SubmitEvent) {
    event.preventDefault()
    if (submitting) return
    error = ''
    const trimmed = name.trim()
    if (!trimmed) {
      error = 'Please enter a name!'
      return
    }
    submitting = true
    try {
      result = await submitScore(trimmed, score)
      savePlayerName(trimmed)
    } catch (submitError) {
      error = (submitError as Error).message
    } finally {
      submitting = false
    }
  }
</script>

{#if result === null}
  <form onsubmit={save}>
    <label for="player-name">Save your score to the leaderboard</label>
    <div class="row">
      <input id="player-name" type="text" maxlength="20" placeholder="Your name" bind:value={name} />
      <button type="submit" disabled={submitting}>Save Score</button>
    </div>
  </form>
  {#if error}
    <p class="save-error">{error}</p>
  {/if}
{:else}
  <p class="result" class:best={result.new_best}>
    {result.new_best
      ? '🏆 New high score!'
      : `Saved — but your record is still ${result.best_score}.`}
  </p>
  <ScoreList entries={result.leaderboard} highlight={name.trim()} />
{/if}

<style>
  form label {
    display: block;
    margin: 1rem 0 0.35rem;
    color: var(--text-dim);
    text-align: center;
  }

  .row {
    display: flex;
    gap: 0.5rem;
  }

  .row button {
    white-space: nowrap;
  }

  .save-error,
  .result {
    text-align: center;
    margin: 0.75rem 0 0;
  }

  .save-error {
    color: var(--danger);
  }

  .result.best {
    color: var(--warning);
    font-size: 1.1rem;
  }
</style>
