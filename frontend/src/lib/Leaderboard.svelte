<script lang="ts">
  import { getLeaderboard, type LeaderboardEntry } from './api'
  import { getPlayerName } from './settings'
  import ScoreList from './ScoreList.svelte'

  let { onBack }: { onBack: () => void } = $props()

  let entries: LeaderboardEntry[] | null = $state(null)
  let error = $state('')

  async function load() {
    error = ''
    entries = null
    try {
      entries = (await getLeaderboard()).leaderboard
    } catch (loadError) {
      error = (loadError as Error).message
    }
  }

  load()
</script>

<div class="card">
  <h2>🏆 Leaderboard</h2>

  {#if error}
    <p class="error">{error}</p>
    <button onclick={load}>Try Again</button>
  {:else if entries === null}
    <p class="dim">Loading scores...</p>
  {:else if entries.length === 0}
    <p class="dim">No scores yet — be the first!</p>
  {:else}
    <ScoreList {entries} highlight={getPlayerName()} />
  {/if}
</div>

<button class="secondary back" onclick={onBack}>Back to Menu</button>

<style>
  h2 {
    text-align: center;
  }

  .dim {
    color: var(--text-dim);
    text-align: center;
  }

  .error {
    color: var(--danger);
    text-align: center;
  }

  .back {
    margin-top: 1rem;
    width: 100%;
  }
</style>
