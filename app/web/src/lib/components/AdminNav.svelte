<script lang="ts">
  import { base } from '$app/paths';
  import { page } from '$app/state';
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

  const pathname = $derived(page.url.pathname);

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

<div class="mb-8">
  <!-- Section Header & Navigation Tabs -->
  <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-line pb-4">
    <div>
      <div class="flex items-center gap-2">
        <span
          class="inline-flex items-center rounded-full bg-brand-soft px-2.5 py-0.5 text-xs font-semibold text-brand"
        >
          🛡️ Admin Control Plane
        </span>
      </div>
      <h1 class="mt-1 text-2xl font-bold tracking-tight text-ink">System Administration</h1>
      <p class="text-xs text-muted">
        Manage project portfolio registers, developer accounts, RBAC tiers, and application configuration.
      </p>
    </div>

    <!-- Admin Tabs -->
    <nav
      class="flex items-center gap-1.5 rounded-lg border border-line bg-panel p-1 text-xs font-medium"
      aria-label="Admin Sections"
    >
      <a
        href="{base}/admin/projects"
        class="flex items-center gap-1.5 rounded-md px-3 py-1.5 transition-colors {pathname.includes(
          '/admin/projects'
        )
          ? 'bg-canvas text-ink font-semibold shadow-sm border border-line'
          : 'text-muted hover:text-ink hover:bg-canvas/50'}"
      >
        <span>📁</span>
        <span>Projects</span>
      </a>
      <a
        href="{base}/admin/developers"
        class="flex items-center gap-1.5 rounded-md px-3 py-1.5 transition-colors {pathname.includes(
          '/admin/developers'
        )
          ? 'bg-canvas text-ink font-semibold shadow-sm border border-line'
          : 'text-muted hover:text-ink hover:bg-canvas/50'}"
      >
        <span>👥</span>
        <span>Developers</span>
      </a>
      <a
        href="{base}/admin/settings"
        class="flex items-center gap-1.5 rounded-md px-3 py-1.5 transition-colors {pathname.includes(
          '/admin/settings'
        )
          ? 'bg-canvas text-ink font-semibold shadow-sm border border-line'
          : 'text-muted hover:text-ink hover:bg-canvas/50'}"
      >
        <span>⚙️</span>
        <span>Settings</span>
      </a>
    </nav>
  </div>

  <!-- D-CRUD-1 / R7.2 Honesty Divergence Banner -->
  {#if divergence.isDiverged}
    <div class="mt-4 rounded-lg border border-warn-line bg-warn-soft/20 p-4 text-xs text-ink transition-all">
      <div class="flex items-start justify-between gap-3">
        <div class="flex items-start gap-2.5">
          <span class="text-base leading-none">⚠️</span>
          <div>
            <div class="font-semibold text-warn flex items-center gap-2">
              <span>Live Database Diverged from Committed Snapshot (data/*.json)</span>
              <span class="rounded bg-warn/20 px-1.5 py-0.5 text-[10px] uppercase font-mono tracking-wider">
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
                class="mt-3 space-y-1 rounded bg-panel/70 p-2.5 border border-line text-[11px] font-mono text-muted"
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
</div>
