<script lang="ts">
  import type { LeaderboardEntry } from './api'

  let { entries, highlight = '' }: { entries: LeaderboardEntry[]; highlight?: string } = $props()

  const medals = ['🥇', '🥈', '🥉']
</script>

<ol class="scores">
  {#each entries as entry, index}
    <li class:highlight={entry.name.toLowerCase() === highlight.toLowerCase() && highlight !== ''}>
      <span class="rank">{medals[index] ?? `${index + 1}.`}</span>
      <span class="name">{entry.name}</span>
      <span class="score">{entry.score}</span>
    </li>
  {/each}
</ol>

<style>
  .scores {
    list-style: none;
    margin: 1rem 0 0;
    padding: 0;
  }

  .scores li {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.5rem 0.8rem;
    margin-bottom: 0.4rem;
  }

  .scores li.highlight {
    border-color: var(--accent);
  }

  .rank {
    width: 2rem;
    text-align: center;
  }

  .name {
    flex: 1;
    overflow-wrap: anywhere;
  }

  .score {
    font-weight: bold;
    color: var(--warning);
  }
</style>
