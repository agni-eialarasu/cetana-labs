<script lang="ts">
  import { base } from '$app/paths';
  import { auth } from '$lib/auth.svelte';
  import AdminNav from '$lib/components/AdminNav.svelte';
  import {
    loadEditableProjects,
    loadEditableUsers,
    createProject,
    updateProject,
    deleteProject,
    ARCHETYPES,
    HEALTH_OPTIONS,
    type EditableProjectRecord,
    type EditableUserRecord,
    type ProjectInputPayload
  } from '$lib/crud.svelte';
  import type { Archetype, DevEnvironment } from '$lib/types';
  import { onMount } from 'svelte';

  let loading = $state(true);
  let loadError = $state<string | null>(null);
  let projects = $state<EditableProjectRecord[]>([]);
  let users = $state<EditableUserRecord[]>([]);

  // Filtering & Search
  let searchQuery = $state('');
  let archetypeFilter = $state<string>('all');
  let healthFilter = $state<string>('all');

  // Modals & form state
  let showCreateModal = $state(false);
  let editingProject = $state<EditableProjectRecord | null>(null);
  let deletingProject = $state<EditableProjectRecord | null>(null);
  let deleteConfirmInput = $state('');

  // Form fields
  let formLabId = $state('');
  let formSlug = $state('');
  let formName = $state('');
  let formDescriptor = $state('');
  let formArchetype = $state<Archetype>('mini-app');
  let formOwnerId = $state(''); // User PB record ID
  let formRepoUrl = $state('');
  let formRefUrl = $state('');
  let formDevEnv = $state<DevEnvironment>('cloud');
  let formStatusSource = $state<'local' | 'remote'>('local');
  let formStatusHealth = $state('');
  let formStatusNote = $state('');

  let submitting = $state(false);
  let formError = $state<string | null>(null);
  let successNotice = $state<string | null>(null);

  // LAB-ID validation regex
  const LAB_ID_REGEX = /^LAB-\d{3}$/;

  function isValidUrl(val: string): boolean {
    if (!val || val.trim() === '') return true;
    try {
      const u = new URL(val.trim());
      return u.protocol === 'http:' || u.protocol === 'https:';
    } catch {
      return false;
    }
  }

  const filteredProjects = $derived(
    projects.filter((p) => {
      if (archetypeFilter !== 'all' && p.archetype !== archetypeFilter) return false;
      if (healthFilter !== 'all' && (p.status_health || '') !== healthFilter) return false;
      if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase().trim();
        const matchLab = p.lab_id.toLowerCase().includes(q);
        const matchName = p.name.toLowerCase().includes(q);
        const matchSlug = p.slug.toLowerCase().includes(q);
        const matchOwner =
          p.owner_name.toLowerCase().includes(q) || (p.owner_github?.toLowerCase().includes(q) ?? false);
        return matchLab || matchName || matchSlug || matchOwner;
      }
      return true;
    })
  );

  async function fetchData() {
    loading = true;
    loadError = null;
    try {
      const [projList, userList] = await Promise.all([loadEditableProjects(), loadEditableUsers()]);
      projects = projList;
      users = userList;
    } catch (err) {
      loadError = err instanceof Error ? err.message : 'Failed to load project records.';
    } finally {
      loading = false;
    }
  }

  function resetForm() {
    formLabId = '';
    formSlug = '';
    formName = '';
    formDescriptor = '';
    formArchetype = 'mini-app';
    formOwnerId = users[0]?.id || '';
    formRepoUrl = '';
    formRefUrl = '';
    formDevEnv = 'cloud';
    formStatusSource = 'local';
    formStatusHealth = '🟢 On Track';
    formStatusNote = '';
    formError = null;
  }

  function openCreateModal() {
    resetForm();
    // Suggest next available sequential LAB ID (e.g. LAB-006)
    const existingNums = projects
      .map((p) => {
        const m = p.lab_id.match(/^LAB-(\d{3})$/);
        return m ? parseInt(m[1], 10) : -1;
      })
      .filter((n) => n >= 0);
    const nextNum = existingNums.length > 0 ? Math.max(...existingNums) + 1 : 0;
    formLabId = `LAB-${String(nextNum).padStart(3, '0')}`;
    showCreateModal = true;
  }

  function openEditModal(p: EditableProjectRecord) {
    resetForm();
    editingProject = p;
    formLabId = p.lab_id;
    formSlug = p.slug;
    formName = p.name;
    formDescriptor = p.descriptor || '';
    formArchetype = p.archetype;
    formOwnerId = p.owner;
    formRepoUrl = p.repo_url || '';
    formRefUrl = p.reference_url || '';
    formDevEnv = p.dev_environment;
    formStatusSource = p.status_source;
    formStatusHealth = p.status_health || '';
    formStatusNote = p.status_note || '';
  }

  function openDeleteModal(p: EditableProjectRecord) {
    deletingProject = p;
    deleteConfirmInput = '';
    formError = null;
  }

  function autoSlugify() {
    if (!formSlug || formSlug === '') {
      formSlug = formName
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
    }
  }

  async function handleCreateSubmit() {
    formError = null;
    successNotice = null;

    const trimmedLabId = formLabId.trim().toUpperCase();
    if (!LAB_ID_REGEX.test(trimmedLabId)) {
      formError = 'Project ID must strictly follow sequential format LAB-XXX (e.g. LAB-006).';
      return;
    }
    if (!formName.trim()) {
      formError = 'Project name is required.';
      return;
    }
    if (!formSlug.trim()) {
      formError = 'Project slug is required.';
      return;
    }
    if (!formOwnerId) {
      formError = 'Project owner must be selected from registered developers.';
      return;
    }
    if (!isValidUrl(formRepoUrl)) {
      formError = 'Repository URL must be a valid HTTP or HTTPS URL (or leave empty).';
      return;
    }
    if (!isValidUrl(formRefUrl)) {
      formError = 'Reference URL must be a valid HTTP or HTTPS URL (or leave empty).';
      return;
    }

    submitting = true;
    try {
      const payload: ProjectInputPayload = {
        lab_id: trimmedLabId,
        slug: formSlug.trim().toLowerCase(),
        name: formName.trim(),
        descriptor: formDescriptor.trim() || null,
        archetype: formArchetype,
        owner: formOwnerId,
        repo_url: formRepoUrl.trim() || null,
        reference_url: formRefUrl.trim() || null,
        dev_environment: formDevEnv,
        status_source: formStatusSource,
        status_health: formStatusHealth || null,
        status_note: formStatusNote.trim() || null
      };

      await createProject(payload);
      showCreateModal = false;
      successNotice = `Successfully created project ${trimmedLabId} (${formName.trim()}).`;
      await fetchData();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create project.';
      if (
        msg.includes('UNIQUE constraint') ||
        msg.includes('already exists') ||
        msg.includes('idx_projects_lab_id')
      ) {
        formError = `Conflict: A project with ID "${trimmedLabId}" already exists. Please choose a unique sequential LAB ID.`;
      } else {
        formError = msg;
      }
    } finally {
      submitting = false;
    }
  }

  async function handleUpdateSubmit() {
    if (!editingProject) return;
    formError = null;
    successNotice = null;

    const trimmedLabId = formLabId.trim().toUpperCase();
    if (!LAB_ID_REGEX.test(trimmedLabId)) {
      formError = 'Project ID must strictly follow format LAB-XXX (e.g. LAB-001).';
      return;
    }
    if (!formName.trim()) {
      formError = 'Project name is required.';
      return;
    }
    if (!formSlug.trim()) {
      formError = 'Project slug is required.';
      return;
    }
    if (!formOwnerId) {
      formError = 'Project owner must be selected.';
      return;
    }
    if (!isValidUrl(formRepoUrl)) {
      formError = 'Repository URL must be a valid HTTP or HTTPS URL.';
      return;
    }
    if (!isValidUrl(formRefUrl)) {
      formError = 'Reference URL must be a valid HTTP or HTTPS URL.';
      return;
    }

    submitting = true;
    try {
      const payload: Partial<ProjectInputPayload> = {
        lab_id: trimmedLabId,
        slug: formSlug.trim().toLowerCase(),
        name: formName.trim(),
        descriptor: formDescriptor.trim() || null,
        archetype: formArchetype,
        owner: formOwnerId,
        repo_url: formRepoUrl.trim() || null,
        reference_url: formRefUrl.trim() || null,
        dev_environment: formDevEnv,
        status_source: formStatusSource,
        status_health: formStatusHealth || null,
        status_note: formStatusNote.trim() || null
      };

      await updateProject(editingProject.id, payload);
      editingProject = null;
      successNotice = `Successfully updated project ${trimmedLabId}.`;
      await fetchData();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to update project.';
      formError = msg;
    } finally {
      submitting = false;
    }
  }

  async function handleDeleteSubmit() {
    if (!deletingProject) return;
    formError = null;
    successNotice = null;

    if (deleteConfirmInput.trim().toUpperCase() !== deletingProject.lab_id.toUpperCase()) {
      formError = `Confirmation code does not match. Please type "${deletingProject.lab_id}" to confirm.`;
      return;
    }

    submitting = true;
    try {
      const deletedId = deletingProject.lab_id;
      const deletedName = deletingProject.name;
      await deleteProject(deletingProject.id);
      deletingProject = null;
      successNotice = `Permanently deleted project ${deletedId} (${deletedName}).`;
      await fetchData();
    } catch (err: unknown) {
      formError = err instanceof Error ? err.message : 'Failed to delete project.';
    } finally {
      submitting = false;
    }
  }

  onMount(() => {
    if (auth.isAdmin) {
      void fetchData();
    } else {
      loading = false;
    }
  });

  $effect(() => {
    if (auth.isAdmin && projects.length === 0 && !loading) {
      void fetchData();
    }
  });
</script>

<svelte:head>
  <title>Manage Projects — Cetana Labs Admin</title>
</svelte:head>

{#if !auth.isAdmin}
  <div class="mx-auto max-w-content px-4 py-12 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-lg rounded-card border border-line bg-panel p-8 text-center shadow-sm">
      <div
        class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-critical-soft text-xl text-critical"
      >
        🔒
      </div>
      <h1 class="text-xl font-bold text-ink">Admin Access Required</h1>
      <p class="mt-2 text-sm text-muted">
        You must be signed in with administrator privileges to manage the project portfolio registry.
      </p>
      <div class="mt-6 flex justify-center gap-3">
        <a
          href="{base}/"
          class="rounded-control border border-line bg-canvas px-4 py-2 text-xs font-semibold text-ink transition-colors hover:border-brand-line hover:text-brand"
        >
          ← Back to Dashboard
        </a>
      </div>
    </div>
  </div>
{:else}
  <div class="mx-auto max-w-content px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
    <AdminNav />

    <!-- Action Bar & Summary -->
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="text-xl font-bold tracking-tight text-ink flex items-center gap-2">
          <span>📁 Projects Register</span>
          <span
            class="rounded-full bg-panel px-2.5 py-0.5 text-xs font-mono font-medium text-muted border border-line"
          >
            {projects.length} initiatives
          </span>
        </h2>
        <p class="text-xs text-muted mt-0.5">
          Live PocketBase records backing the portfolio dashboard. In-app edits are saved directly to the
          database.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          onclick={openCreateModal}
          class="inline-flex items-center gap-1.5 rounded-md bg-brand px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition-all hover:bg-brand/90"
        >
          <span>＋</span>
          <span>New Project</span>
        </button>
      </div>
    </div>

    <!-- Success Notice -->
    {#if successNotice}
      <div
        class="mb-6 flex items-center justify-between rounded-lg border border-brand/30 bg-brand-soft/20 px-4 py-3 text-xs text-brand-ink"
      >
        <div class="flex items-center gap-2">
          <span>✅</span>
          <span>{successNotice}</span>
        </div>
        <button type="button" onclick={() => (successNotice = null)} class="text-muted hover:text-ink"
          >✕</button
        >
      </div>
    {/if}

    <!-- Filters & Search -->
    <div class="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-4">
      <div class="sm:col-span-2">
        <input
          type="search"
          placeholder="Search by ID, name, slug, or owner…"
          bind:value={searchQuery}
          class="w-full rounded-md border border-line bg-panel px-3 py-2 text-xs text-ink placeholder:text-muted focus:border-brand focus:outline-none"
        />
      </div>
      <div>
        <select
          bind:value={archetypeFilter}
          class="w-full rounded-md border border-line bg-panel px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
        >
          <option value="all">All Archetypes</option>
          {#each ARCHETYPES as arch}
            <option value={arch.value}>{arch.icon} {arch.label}</option>
          {/each}
        </select>
      </div>
      <div>
        <select
          bind:value={healthFilter}
          class="w-full rounded-md border border-line bg-panel px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
        >
          <option value="all">All Health States</option>
          {#each HEALTH_OPTIONS as h}
            <option value={h}>{h}</option>
          {/each}
        </select>
      </div>
    </div>

    <!-- Main Table View -->
    {#if loading}
      <div class="flex items-center justify-center py-20 text-muted">
        <span class="text-sm">Loading project portfolio…</span>
      </div>
    {:else if loadError}
      <div class="rounded-lg border border-critical-line bg-critical-soft/20 p-4 text-xs text-critical">
        <p class="font-semibold">Error Loading Projects</p>
        <p class="mt-1">{loadError}</p>
        <button
          type="button"
          onclick={fetchData}
          class="mt-3 rounded border border-line bg-panel px-2.5 py-1 text-xs text-ink hover:bg-canvas"
        >
          Retry
        </button>
      </div>
    {:else if filteredProjects.length === 0}
      <div class="rounded-lg border border-line bg-panel p-12 text-center text-xs text-muted">
        <p class="text-sm font-medium text-ink">No projects match the current filter</p>
        <p class="mt-1">Try adjusting your search query or archetype/health filters.</p>
      </div>
    {:else}
      <div class="overflow-x-auto rounded-lg border border-line bg-panel shadow-sm">
        <table class="w-full text-left text-xs">
          <thead
            class="border-b border-line bg-canvas/60 text-[11px] font-semibold text-muted uppercase tracking-wider"
          >
            <tr>
              <th scope="col" class="py-3 pl-4 pr-3">ID</th>
              <th scope="col" class="px-3 py-3">Project / Slug</th>
              <th scope="col" class="px-3 py-3">Archetype</th>
              <th scope="col" class="px-3 py-3">Owner</th>
              <th scope="col" class="px-3 py-3">Dev Env</th>
              <th scope="col" class="px-3 py-3">Health Status</th>
              <th scope="col" class="py-3 pl-3 pr-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-line text-ink">
            {#each filteredProjects as p (p.id)}
              <tr class="transition-colors hover:bg-canvas/40">
                <td class="py-3.5 pl-4 pr-3 font-mono font-bold text-ink whitespace-nowrap">
                  {p.lab_id}
                </td>
                <td class="px-3 py-3.5">
                  <div class="font-medium text-ink">{p.name}</div>
                  <div class="font-mono text-[11px] text-muted">{p.slug}</div>
                  {#if p.descriptor}
                    <div class="text-[11px] text-muted italic mt-0.5 line-clamp-1">{p.descriptor}</div>
                  {/if}
                </td>
                <td class="px-3 py-3.5 whitespace-nowrap">
                  <span
                    class="inline-flex items-center gap-1 rounded bg-canvas px-2 py-1 text-[11px] border border-line"
                  >
                    <span>{ARCHETYPES.find((a) => a.value === p.archetype)?.icon || '💻'}</span>
                    <span>{ARCHETYPES.find((a) => a.value === p.archetype)?.label || p.archetype}</span>
                  </span>
                </td>
                <td class="px-3 py-3.5 whitespace-nowrap">
                  <div class="font-medium text-ink">{p.owner_name}</div>
                  {#if p.owner_github}
                    <div class="text-[11px] text-muted font-mono">@{p.owner_github}</div>
                  {/if}
                </td>
                <td class="px-3 py-3.5 whitespace-nowrap">
                  <span
                    class="rounded px-2 py-0.5 font-mono text-[11px] uppercase {p.dev_environment === 'cloud'
                      ? 'bg-brand-soft/40 text-brand'
                      : 'bg-canvas text-muted border border-line'}"
                  >
                    {p.dev_environment}
                  </span>
                </td>
                <td class="px-3 py-3.5 whitespace-nowrap">
                  <div class="text-[11px] font-medium">{p.status_health || '—'}</div>
                  {#if p.status_note}
                    <div class="text-[10px] text-muted line-clamp-1 max-w-xs">{p.status_note}</div>
                  {/if}
                </td>
                <td class="py-3.5 pl-3 pr-4 text-right whitespace-nowrap">
                  <div class="flex items-center justify-end gap-1.5">
                    <button
                      type="button"
                      onclick={() => openEditModal(p)}
                      class="rounded border border-line bg-canvas px-2.5 py-1 text-[11px] font-medium text-ink transition-colors hover:border-brand-line hover:text-brand"
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      onclick={() => openDeleteModal(p)}
                      class="rounded border border-critical-line/40 bg-critical-soft/10 px-2 py-1 text-[11px] font-medium text-critical transition-colors hover:bg-critical hover:text-white"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
{/if}

<!-- Create Project Modal -->
{#if showCreateModal}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto"
  >
    <div class="relative w-full max-w-2xl rounded-card border border-line bg-panel p-6 shadow-xl my-8">
      <div class="flex items-center justify-between border-b border-line pb-3">
        <h3 class="text-base font-bold text-ink flex items-center gap-2">
          <span>＋ Create New Project</span>
          <span class="font-mono text-xs text-brand font-medium">RULE_ADMIN</span>
        </h3>
        <button
          type="button"
          onclick={() => (showCreateModal = false)}
          class="text-muted hover:text-ink text-sm"
        >
          ✕
        </button>
      </div>

      {#if formError}
        <div
          class="mt-4 rounded-md border border-critical-line bg-critical-soft/20 p-3 text-xs text-critical"
        >
          {formError}
        </div>
      {/if}

      <form
        onsubmit={(e) => {
          e.preventDefault();
          void handleCreateSubmit();
        }}
        class="mt-4 space-y-4 text-xs"
      >
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- LAB ID -->
          <div>
            <label for="create-lab-id" class="block font-semibold text-ink">Project ID (Sequential)</label>
            <input
              id="create-lab-id"
              type="text"
              bind:value={formLabId}
              placeholder="LAB-006"
              required
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 font-mono text-xs text-ink uppercase focus:border-brand focus:outline-none"
            />
            <p class="mt-0.5 text-[11px] text-muted">
              Strict pattern: <code class="font-mono">^LAB-\d&#123;3&#125;$</code>
            </p>
          </div>

          <!-- Name -->
          <div>
            <label for="create-name" class="block font-semibold text-ink">Project Name</label>
            <input
              id="create-name"
              type="text"
              bind:value={formName}
              onblur={autoSlugify}
              placeholder="e.g. Nexus Beacon"
              required
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Slug -->
          <div>
            <label for="create-slug" class="block font-semibold text-ink">Project Slug</label>
            <input
              id="create-slug"
              type="text"
              bind:value={formSlug}
              placeholder="e.g. nexus-beacon"
              required
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 font-mono text-xs text-ink lowercase focus:border-brand focus:outline-none"
            />
          </div>

          <!-- Archetype -->
          <div>
            <label for="create-archetype" class="block font-semibold text-ink">Archetype</label>
            <select
              id="create-archetype"
              bind:value={formArchetype}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            >
              {#each ARCHETYPES as arch}
                <option value={arch.value}>{arch.icon} {arch.label}</option>
              {/each}
            </select>
          </div>
        </div>

        <!-- Descriptor -->
        <div>
          <label for="create-descriptor" class="block font-semibold text-ink"
            >Descriptor (Subheading / Tagline)</label
          >
          <input
            id="create-descriptor"
            type="text"
            bind:value={formDescriptor}
            placeholder="e.g. Incident Response Radar"
            class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Owner Picker (Relation) -->
          <div>
            <label for="create-owner" class="block font-semibold text-ink"
              >Project Owner (User Relation)</label
            >
            <select
              id="create-owner"
              bind:value={formOwnerId}
              required
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            >
              {#each users as u}
                <option value={u.id}>
                  {u.name}
                  {u.github_handle ? `(@${u.github_handle})` : ''}
                  {u.is_admin ? '🛡️' : ''}
                </option>
              {/each}
            </select>
            <p class="mt-0.5 text-[11px] text-muted">Required foreign-key relation to users collection.</p>
          </div>

          <!-- Dev Environment -->
          <div>
            <label for="create-dev-env" class="block font-semibold text-ink">Dev Environment</label>
            <select
              id="create-dev-env"
              bind:value={formDevEnv}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            >
              <option value="cloud">☁️ Cloud</option>
              <option value="local">💻 Local</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Repo URL -->
          <div>
            <label for="create-repo-url" class="block font-semibold text-ink">GitHub Repository URL</label>
            <input
              id="create-repo-url"
              type="url"
              bind:value={formRepoUrl}
              placeholder="https://github.com/agni-eialarasu/..."
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            />
          </div>

          <!-- Reference URL -->
          <div>
            <label for="create-ref-url" class="block font-semibold text-ink">Reference / Homepage URL</label>
            <input
              id="create-ref-url"
              type="url"
              bind:value={formRefUrl}
              placeholder="https://..."
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Status Health -->
          <div>
            <label for="create-health" class="block font-semibold text-ink">Initial Health Status</label>
            <select
              id="create-health"
              bind:value={formStatusHealth}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            >
              <option value="">No health specified</option>
              {#each HEALTH_OPTIONS as h}
                <option value={h}>{h}</option>
              {/each}
            </select>
          </div>

          <!-- Status Source -->
          <div>
            <label for="create-status-source" class="block font-semibold text-ink">Status Source</label>
            <select
              id="create-status-source"
              bind:value={formStatusSource}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            >
              <option value="local">local (status.md in repo)</option>
              <option value="remote">remote (status.md in external repo)</option>
            </select>
          </div>
        </div>

        <!-- Status Note -->
        <div>
          <label for="create-status-note" class="block font-semibold text-ink">Status Note / Summary</label>
          <input
            id="create-status-note"
            type="text"
            bind:value={formStatusNote}
            placeholder="e.g. Scaffolding complete; awaiting first sprint delivery."
            class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
          />
        </div>

        <div class="flex items-center justify-end gap-3 pt-4 border-t border-line">
          <button
            type="button"
            onclick={() => (showCreateModal = false)}
            disabled={submitting}
            class="rounded border border-line bg-canvas px-4 py-2 text-xs font-semibold text-ink transition-colors hover:bg-panel disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            class="rounded bg-brand px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-brand/90 disabled:opacity-50"
          >
            {submitting ? 'Creating Project…' : 'Create Project'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Edit Project Modal -->
{#if editingProject}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto"
  >
    <div class="relative w-full max-w-2xl rounded-card border border-line bg-panel p-6 shadow-xl my-8">
      <div class="flex items-center justify-between border-b border-line pb-3">
        <h3 class="text-base font-bold text-ink flex items-center gap-2">
          <span>Edit Project: {editingProject.lab_id}</span>
          <span class="font-mono text-xs text-muted">({editingProject.name})</span>
        </h3>
        <button
          type="button"
          onclick={() => (editingProject = null)}
          class="text-muted hover:text-ink text-sm"
        >
          ✕
        </button>
      </div>

      {#if formError}
        <div
          class="mt-4 rounded-md border border-critical-line bg-critical-soft/20 p-3 text-xs text-critical"
        >
          {formError}
        </div>
      {/if}

      <form
        onsubmit={(e) => {
          e.preventDefault();
          void handleUpdateSubmit();
        }}
        class="mt-4 space-y-4 text-xs"
      >
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- LAB ID -->
          <div>
            <label for="edit-lab-id" class="block font-semibold text-ink">Project ID</label>
            <input
              id="edit-lab-id"
              type="text"
              bind:value={formLabId}
              required
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 font-mono text-xs text-ink uppercase focus:border-brand focus:outline-none"
            />
          </div>

          <!-- Name -->
          <div>
            <label for="edit-name" class="block font-semibold text-ink">Project Name</label>
            <input
              id="edit-name"
              type="text"
              bind:value={formName}
              required
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Slug -->
          <div>
            <label for="edit-slug" class="block font-semibold text-ink">Project Slug</label>
            <input
              id="edit-slug"
              type="text"
              bind:value={formSlug}
              required
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 font-mono text-xs text-ink lowercase focus:border-brand focus:outline-none"
            />
          </div>

          <!-- Archetype -->
          <div>
            <label for="edit-archetype" class="block font-semibold text-ink">Archetype</label>
            <select
              id="edit-archetype"
              bind:value={formArchetype}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            >
              {#each ARCHETYPES as arch}
                <option value={arch.value}>{arch.icon} {arch.label}</option>
              {/each}
            </select>
          </div>
        </div>

        <!-- Descriptor -->
        <div>
          <label for="edit-descriptor" class="block font-semibold text-ink">Descriptor</label>
          <input
            id="edit-descriptor"
            type="text"
            bind:value={formDescriptor}
            class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Owner Reassign Picker (R3.1) -->
          <div>
            <label for="edit-owner" class="block font-semibold text-ink">Project Owner (Reassign)</label>
            <select
              id="edit-owner"
              bind:value={formOwnerId}
              required
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            >
              {#each users as u}
                <option value={u.id}>
                  {u.name}
                  {u.github_handle ? `(@${u.github_handle})` : ''}
                  {u.is_admin ? '🛡️' : ''}
                </option>
              {/each}
            </select>
            <p class="mt-0.5 text-[11px] text-muted">
              Reassigning owner updates PocketBase owner foreign key.
            </p>
          </div>

          <!-- Dev Environment -->
          <div>
            <label for="edit-dev-env" class="block font-semibold text-ink">Dev Environment</label>
            <select
              id="edit-dev-env"
              bind:value={formDevEnv}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            >
              <option value="cloud">☁️ Cloud</option>
              <option value="local">💻 Local</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Repo URL -->
          <div>
            <label for="edit-repo-url" class="block font-semibold text-ink">GitHub Repository URL</label>
            <input
              id="edit-repo-url"
              type="url"
              bind:value={formRepoUrl}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            />
          </div>

          <!-- Reference URL -->
          <div>
            <label for="edit-ref-url" class="block font-semibold text-ink">Reference URL</label>
            <input
              id="edit-ref-url"
              type="url"
              bind:value={formRefUrl}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Status Health -->
          <div>
            <label for="edit-health" class="block font-semibold text-ink">Health Status</label>
            <select
              id="edit-health"
              bind:value={formStatusHealth}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            >
              <option value="">No health specified</option>
              {#each HEALTH_OPTIONS as h}
                <option value={h}>{h}</option>
              {/each}
            </select>
          </div>

          <!-- Status Source -->
          <div>
            <label for="edit-status-source" class="block font-semibold text-ink">Status Source</label>
            <select
              id="edit-status-source"
              bind:value={formStatusSource}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            >
              <option value="local">local (status.md in repo)</option>
              <option value="remote">remote (status.md in external repo)</option>
            </select>
          </div>
        </div>

        <!-- Status Note -->
        <div>
          <label for="edit-status-note" class="block font-semibold text-ink">Status Note</label>
          <input
            id="edit-status-note"
            type="text"
            bind:value={formStatusNote}
            class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
          />
        </div>

        <div class="flex items-center justify-end gap-3 pt-4 border-t border-line">
          <button
            type="button"
            onclick={() => (editingProject = null)}
            disabled={submitting}
            class="rounded border border-line bg-canvas px-4 py-2 text-xs font-semibold text-ink transition-colors hover:bg-panel disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            class="rounded bg-brand px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-brand/90 disabled:opacity-50"
          >
            {submitting ? 'Saving Changes…' : 'Save Project Changes'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Delete Confirmation Modal (R3.2) -->
{#if deletingProject}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
    <div class="relative w-full max-w-md rounded-card border border-critical-line bg-panel p-6 shadow-xl">
      <div class="flex items-center gap-3">
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-critical-soft text-lg text-critical"
        >
          ⚠️
        </div>
        <div>
          <h3 class="text-base font-bold text-ink">Permanently Delete Project?</h3>
          <p class="text-xs text-muted">This action is irreversible and deletes the live database record.</p>
        </div>
      </div>

      {#if formError}
        <div class="mt-3 rounded border border-critical-line bg-critical-soft/20 p-2.5 text-xs text-critical">
          {formError}
        </div>
      {/if}

      <div class="mt-4 rounded bg-canvas p-3 border border-line text-xs">
        <div class="font-bold text-ink">{deletingProject.name}</div>
        <div class="font-mono text-muted text-[11px]">{deletingProject.lab_id} · {deletingProject.slug}</div>
        <div class="text-[11px] text-muted mt-1">Owner: {deletingProject.owner_name}</div>
      </div>

      <div class="mt-4">
        <label for="delete-confirm-input" class="block text-xs text-ink font-medium">
          To confirm, type <strong class="font-mono text-critical">{deletingProject.lab_id}</strong> below:
        </label>
        <input
          id="delete-confirm-input"
          type="text"
          bind:value={deleteConfirmInput}
          placeholder={deletingProject.lab_id}
          class="mt-1.5 w-full rounded border border-line bg-canvas px-3 py-2 font-mono text-xs uppercase text-ink focus:border-critical focus:outline-none"
        />
      </div>

      <div class="mt-6 flex items-center justify-end gap-3">
        <button
          type="button"
          onclick={() => (deletingProject = null)}
          disabled={submitting}
          class="rounded border border-line bg-canvas px-4 py-2 text-xs font-semibold text-ink hover:bg-panel disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          type="button"
          onclick={() => void handleDeleteSubmit()}
          disabled={submitting ||
            deleteConfirmInput.trim().toUpperCase() !== deletingProject.lab_id.toUpperCase()}
          class="rounded bg-critical px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-critical/90 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {submitting ? 'Deleting…' : 'I Understand, Delete Project'}
        </button>
      </div>
    </div>
  </div>
{/if}
