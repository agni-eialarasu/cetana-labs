<script lang="ts">
  import type { Project } from '$lib/types';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import KpiCard from '$lib/components/KpiCard.svelte';
  import ProjectCard from '$lib/components/ProjectCard.svelte';

  let { data }: { data: { projects: Project[] } } = $props();
  const projects = $derived(data.projects);

  type Filter = 'active' | 'all' | 'onboarding-pending' | 'completed' | 'control-plane';
  type Sort = 'priority' | 'recent' | 'id';

  let filter = $state<Filter>('active');
  let sort = $state<Sort>('priority');
  let query = $state('');

  // KPI counts (derived from the static page data)
  const total = $derived(projects.length);
  const activeCount = $derived(projects.filter((p) => p.tags.includes('active')).length);
  const blockerCount = $derived(projects.filter((p) => p.has_blocker).length);
  const onboardingCount = $derived(projects.filter((p) => p.tags.includes('onboarding-pending')).length);
  const completedCount = $derived(projects.filter((p) => p.tags.includes('completed')).length);

  const tabs = $derived<{ id: Filter; label: string; count: number }[]>([
    { id: 'active', label: 'Active Products', count: activeCount },
    { id: 'all', label: 'All Projects', count: total },
    { id: 'onboarding-pending', label: 'Onboarding Pending', count: onboardingCount },
    { id: 'completed', label: 'Completed', count: completedCount },
    { id: 'control-plane', label: 'Control Hub', count: 1 }
  ]);

  const visible = $derived.by(() => {
    const q = query.toLowerCase().trim();
    let list = projects.filter((p) => {
      const matchesFilter = filter === 'all' || p.tags.includes(filter);
      const haystack = `${p.id} ${p.name} ${p.owner_name} ${p.archetype_label}`.toLowerCase();
      return matchesFilter && (!q || haystack.includes(q));
    });
    list = [...list].sort((a, b) => {
      if (sort === 'priority')
        return a.priority_score - b.priority_score || b.last_updated.localeCompare(a.last_updated);
      if (sort === 'recent') return b.last_updated.localeCompare(a.last_updated);
      return a.id.localeCompare(b.id);
    });
    return list;
  });
</script>

<svelte:head><title>Cetana Labs — Engineering Portfolio</title></svelte:head>

<div class="mx-auto max-w-content px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
  <!-- Header -->
  <header class="mb-8 flex flex-col gap-4 border-b border-line pb-6">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-ink">Cetana Labs</h1>
        <p class="mt-1 text-sm text-muted">Executive engineering portfolio &amp; automated status</p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <ThemeToggle />
        <a
          href="https://github.com/agni-eialarasu/cetana-labs"
          target="_blank"
          rel="noopener noreferrer"
          class="rounded-control border border-line bg-panel px-3.5 py-2 text-sm font-semibold text-ink hover:border-brand-line"
        >
          GitHub ↗
        </a>
      </div>
    </div>

    <!-- KPI bar -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
      <KpiCard
        label="Active Products"
        value={activeCount}
        sub="Client & product initiatives"
        tone="live"
        onclick={() => (filter = 'active')}
      />
      <KpiCard
        label="Hard Blockers"
        value={blockerCount}
        sub={blockerCount ? '⚠️ Requires intervention' : 'All systems clear'}
        tone={blockerCount ? 'critical' : 'live'}
        onclick={() => (filter = 'all')}
      />
      <KpiCard
        label="Onboarding"
        value={onboardingCount}
        sub="Awaiting baseline"
        tone="warn"
        onclick={() => (filter = 'onboarding-pending')}
      />
      <KpiCard
        label="Completed"
        value={completedCount}
        sub="Operationalized"
        tone="muted"
        onclick={() => (filter = 'completed')}
      />
      <KpiCard
        label="Total Registered"
        value={total}
        sub="Full registry"
        tone="brand"
        onclick={() => (filter = 'all')}
      />
    </div>
  </header>

  <!-- Controls -->
  <div class="mb-6 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
    <div class="flex flex-wrap gap-2">
      {#each tabs as tab (tab.id)}
        <button
          type="button"
          class="rounded-control border px-3.5 py-2 text-sm font-semibold transition-colors
            {filter === tab.id
            ? 'border-brand bg-brand-soft text-brand-ink'
            : 'border-line bg-panel text-muted hover:text-ink'}"
          onclick={() => (filter = tab.id)}
        >
          {tab.label} ({tab.count})
        </button>
      {/each}
    </div>
    <div class="flex flex-wrap items-center gap-3">
      <label class="flex items-center gap-2 rounded-control border border-line bg-panel px-3 py-1.5">
        <span class="text-[11px] font-semibold uppercase tracking-wide text-muted">Sort</span>
        <select bind:value={sort} class="bg-transparent text-sm font-semibold text-ink outline-none">
          <option value="priority">Executive Priority</option>
          <option value="recent">Recently Updated</option>
          <option value="id">Project ID</option>
        </select>
      </label>
      <input
        type="search"
        bind:value={query}
        placeholder="Search title, lead, ID…"
        class="min-w-[220px] rounded-control border border-line bg-panel px-3.5 py-2 text-sm text-ink outline-none focus:border-brand"
      />
    </div>
  </div>

  <!-- Cards -->
  {#if visible.length}
    <div class="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
      {#each visible as project (project.id)}
        <ProjectCard {project} />
      {/each}
    </div>
  {:else}
    <p class="rounded-card border border-line bg-panel p-8 text-center text-muted">
      No projects match the current filter.
    </p>
  {/if}

  <footer class="mt-12 border-t border-line pt-5 text-center text-xs text-muted">
    Cetana Labs Control Hub • Synchronized from authoritative STATUS.md records
  </footer>
</div>
