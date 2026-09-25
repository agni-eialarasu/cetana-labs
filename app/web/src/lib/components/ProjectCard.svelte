<script lang="ts">
  import type { Project } from '$lib/types';
  import HealthPill from './HealthPill.svelte';

  let { project }: { project: Project } = $props();

  const cleanWin = (w: string) => w.replace(/\*\*([^*]+)\*\*/g, '$1');
</script>

<article
  class="flex flex-col gap-4 rounded-card border bg-panel p-5 shadow-sm transition-transform hover:-translate-y-0.5
    {project.has_blocker ? 'border-critical/50' : 'border-line hover:border-line-strong'}"
>
  <!-- Top: owner pill (left) + health (right). Project ID is internal (title attr). -->
  <header class="flex items-center justify-between gap-2">
    <span
      class="inline-flex max-w-[62%] items-center gap-1.5 rounded-full border border-line bg-subtle px-2.5 py-1 text-xs font-semibold {project.owner_name ===
      '— Unassigned'
        ? 'text-muted'
        : 'text-ink'}"
      title={project.id}
    >
      <span aria-hidden="true">👤</span>
      <span class="truncate">{project.owner_name}</span>
    </span>
    <HealthPill health={project.health} severity={project.severity} />
  </header>

  <div class="flex flex-col gap-1">
    <h2 class="text-lg font-semibold leading-tight tracking-tight text-ink">{project.name}</h2>
    <div class="text-xs text-muted">
      {project.archetype_icon}
      {project.archetype_label}
    </div>
  </div>

  {#if project.pitch}
    <p class="text-sm leading-relaxed text-ink-secondary">{project.pitch}</p>
  {/if}

  {#if project.has_blocker}
    <div class="rounded-control border border-critical/40 bg-critical-soft p-3">
      <div class="text-[11px] font-bold uppercase tracking-wide text-critical">🚨 Active blocker</div>
      <div class="mt-1 text-sm font-medium text-ink">{project.blockers}</div>
    </div>
  {/if}

  {#if project.is_onboarding_pending}
    <div class="rounded-control border border-dashed border-warn/40 bg-warn-soft p-3 text-sm text-warn-ink">
      <strong>Onboarding pending</strong>
      <p class="mt-1 text-ink-secondary">
        Initial baseline <code class="tabular">STATUS.md</code> not yet committed to this repository.
      </p>
    </div>
  {:else}
    {#if project.wins.length}
      <div>
        <div class="mb-1.5 text-[11px] font-bold uppercase tracking-wide text-muted">Latest deliveries</div>
        <ul class="flex flex-col gap-1.5">
          {#each project.wins.slice(0, 3) as win}
            <li
              class="relative pl-4 text-sm text-ink before:absolute before:left-0 before:text-brand before:content-['•']"
            >
              {cleanWin(win)}
            </li>
          {/each}
        </ul>
      </div>
    {/if}
    {#if project.focus}
      <div>
        <div class="mb-1 text-[11px] font-bold uppercase tracking-wide text-muted">Current focus</div>
        <p class="text-sm text-ink-secondary">{project.focus}</p>
      </div>
    {/if}
  {/if}

  {#if project.repo_url || project.reference_url}
    <footer class="mt-auto border-t border-line pt-3">
      <a
        href={project.repo_url ?? project.reference_url}
        target="_blank"
        rel="noopener noreferrer"
        class="text-xs font-semibold text-brand hover:text-brand-hover"
      >
        View codebase ↗
      </a>
    </footer>
  {/if}
</article>
