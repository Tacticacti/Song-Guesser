<script lang="ts">
  import Menu from './lib/Menu.svelte'
  import Game from './lib/Game.svelte'
  import Settings from './lib/Settings.svelte'

  type Screen = 'menu' | 'game' | 'settings'

  let screen: Screen = $state('menu')
</script>

<main>
  <h1>🎵 Song Guesser</h1>
  <p class="tagline">Hear a song, guess the year it came out!</p>

  {#if screen === 'menu'}
    <Menu onStart={() => (screen = 'game')} onSettings={() => (screen = 'settings')} />
  {:else if screen === 'game'}
    <Game onBackToMenu={() => (screen = 'menu')} />
  {:else}
    <Settings onBack={() => (screen = 'menu')} />
  {/if}
</main>

<style>
  .tagline {
    text-align: center;
    color: var(--text-dim);
    margin: 0;
  }
</style>
