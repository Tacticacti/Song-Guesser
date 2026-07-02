<script lang="ts">
  import { getArtists, addArtist, removeArtist } from './api'
  import { getVolume, saveVolume } from './settings'

  let { onBack }: { onBack: () => void } = $props()

  let artists: string[] = $state([])
  let newArtist = $state('')
  let message = $state('')
  let volume = $state(getVolume())

  $effect(() => {
    saveVolume(volume)
  })

  async function loadArtists() {
    try {
      artists = (await getArtists()).artists
    } catch (error) {
      message = (error as Error).message
    }
  }

  async function handleAdd(event: SubmitEvent) {
    event.preventDefault()
    try {
      artists = (await addArtist(newArtist)).artists
      message = `Added ${newArtist.trim()}!`
      newArtist = ''
    } catch (error) {
      message = (error as Error).message
    }
  }

  async function handleRemove(artist: string) {
    try {
      artists = (await removeArtist(artist)).artists
      message = `Removed ${artist}!`
    } catch (error) {
      message = (error as Error).message
    }
  }

  loadArtists()
</script>

<div class="card">
  <h2>Settings</h2>

  <label class="volume">
    🔊 Volume ({volume}%)
    <input type="range" min="0" max="100" bind:value={volume} />
  </label>

  <h3>Artist List</h3>
  {#if message}
    <p class="message">{message}</p>
  {/if}
  <ul>
    {#each artists as artist}
      <li>
        <span>{artist}</span>
        <button class="secondary remove" onclick={() => handleRemove(artist)} title="Remove {artist}">✕</button>
      </li>
    {/each}
  </ul>

  <form onsubmit={handleAdd}>
    <div class="row">
      <input type="text" placeholder="Add an artist..." bind:value={newArtist} />
      <button type="submit">Add</button>
    </div>
  </form>

  <button class="secondary back" onclick={onBack}>← Go Back</button>
</div>

<style>
  .volume {
    display: block;
    color: var(--text-dim);
    margin-bottom: 1.5rem;
  }

  h3 {
    color: #fff;
    margin: 0 0 0.5rem;
  }

  .message {
    background: var(--bg-input);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    padding: 0.5rem 0.8rem;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0 0 1rem;
  }

  li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.45rem 0.25rem;
    border-bottom: 1px solid var(--border);
  }

  .remove {
    padding: 0.2rem 0.6rem;
    color: var(--danger);
  }

  .row {
    display: flex;
    gap: 0.5rem;
  }

  .back {
    margin-top: 1.25rem;
    width: 100%;
  }
</style>
