<script lang="ts">
  let {
    onStart,
    onSettings,
    onLeaderboard,
  }: { onStart: () => void; onSettings: () => void; onLeaderboard: () => void } = $props()
</script>

<div class="card menu">
  <button onclick={onStart}>▶ Start Normal Mode</button>
  <button class="secondary" disabled title="Coming soon!">More Modes (WIP)</button>
  <button class="secondary" onclick={onLeaderboard}>🏆 Leaderboard</button>
  <button class="secondary" onclick={onSettings}>⚙ Settings</button>
</div>

<style>
  .menu {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .menu button {
    padding: 0.9rem;
    font-size: 1.05rem;
  }
</style>
