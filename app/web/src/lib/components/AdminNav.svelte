<script lang="ts">
  import { onMount } from 'svelte';
  import { checkDataDivergence, type DivergenceStatus } from '$lib/crud.svelte';

  let divergence = $state<DivergenceStatus>({
    isDiverged: false,
    projectDiff: 0,
    userDiff: 0,
    details: []
  });
  let showDetails = $state(false);
  let checking = $state(false);

  async function refreshDivergence() {
    checking = true;
    try {
      divergence = await checkDataDivergence();
    } finally {
      checking = false;
    }
  }

  onMount(() => {
    void refreshDivergence();
  });
</script>

<!-- D-CRUD-1 / R7.2 Honesty Divergence Banner (rendered only when DB is diverged from data/*.json) -->
{#if divergence.isDiverged}
  <div class="mb-4 rounded-lg border border-warn-line bg-warn-soft/20 p-3.5 text-xs text-ink transition-all">
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-start gap-2.5">
        <span class="text-base leading-none">⚠️</span>
        <div>
          <div class="font-semibold text-warn flex items-center gap-2">
            <span>Live Database Diverged from Committed Snapshot (data/*.json)</span>
            <span class="rounded bg-warn/20 px-1.5 py-0.5 text-2xs uppercase font-mono tracking-wider">
              Unreconciled
            </span>
          </div>
          <p class="mt-1 text-muted">
            Live in-app changes exist in PocketBase that differ from the committed <code
              class="rounded bg-panel px-1 py-0.5 font-mono">data/</code
            > snapshot. The master README registry is out of date until reconciled.
          </p>
          <div class="mt-2 flex items-center gap-2 text-ink">
            <span>Resolution:</span>
            <code class="rounded bg-panel border border-line px-2 py-0.5 font-mono text-brand font-medium">
              just export-live-data
            </code>
            <span class="text-muted">then run</span>
            <code class="rounded bg-panel border border-line px-2 py-0.5 font-mono text-brand font-medium">
              just validate-local
            </code>
            <span class="text-muted">and commit via PR.</span>
          </div>

          {#if showDetails && divergence.details.length > 0}
            <ul
              class="mt-3 space-y-1 rounded bg-panel/70 p-2.5 border border-line text-2xs font-mono text-muted"
            >
              {#each divergence.details as item}
                <li class="flex items-center gap-1.5">
                  <span class="text-warn">•</span>
                  <span>{item}</span>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      </div>

      <div class="flex items-center gap-2 shrink-0">
        {#if divergence.details.length > 0}
          <button
            type="button"
            onclick={() => (showDetails = !showDetails)}
            class="rounded border border-line bg-panel px-2.5 py-1 text-xs font-medium text-ink transition-colors hover:bg-canvas"
          >
            {showDetails ? 'Hide Details' : `Details (${divergence.details.length})`}
          </button>
        {/if}
        <button
          type="button"
          onclick={refreshDivergence}
          disabled={checking}
          class="rounded border border-line bg-panel px-2.5 py-1 text-xs font-medium text-ink transition-colors hover:bg-canvas disabled:opacity-50"
        >
          {checking ? 'Checking…' : '↻ Re-check'}
        </button>
      </div>
    </div>
  </div>
{/if}
