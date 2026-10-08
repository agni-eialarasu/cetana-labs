<script lang="ts">
  import { base } from '$app/paths';
  import { auth } from '$lib/auth.svelte';
  import AdminNav from '$lib/components/AdminNav.svelte';
  import {
    loadEditableUsers,
    createUser,
    updateUser,
    ROLES,
    type EditableUserRecord,
    type UserInputPayload
  } from '$lib/crud.svelte';
  import type { Role } from '$lib/types';
  import { onMount } from 'svelte';

  let loading = $state(true);
  let loadError = $state<string | null>(null);
  let users = $state<EditableUserRecord[]>([]);

  // Search & Filters
  let searchQuery = $state('');
  let roleFilter = $state<string>('all');
  let statusFilter = $state<string>('all');

  // Modals & Form State
  let showCreateModal = $state(false);
  let editingUser = $state<EditableUserRecord | null>(null);
  let showHardDeleteInfo = $state(false);

  // Form inputs
  let formName = $state('');
  let formSeedId = $state('');
  let formEmail = $state('');
  let formGithub = $state('');
  let formRole = $state<Role>('contributor');
  let formOrg = $state('');
  let formActive = $state(true);
  let formIsAdmin = $state(false);

  let submitting = $state(false);
  let formError = $state<string | null>(null);
  let successNotice = $state<string | null>(null);

  const SEED_ID_REGEX = /^usr-[a-z0-9-]+$/;

  const filteredUsers = $derived(
    users.filter((u) => {
      if (roleFilter !== 'all' && u.role !== roleFilter) return false;
      if (statusFilter === 'active' && !u.active) return false;
      if (statusFilter === 'inactive' && u.active) return false;
      if (statusFilter === 'admin' && !u.is_admin) return false;
      if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase().trim();
        const matchName = u.name.toLowerCase().includes(q);
        const matchHandle = (u.github_handle || '').toLowerCase().includes(q);
        const matchSeed = (u.seed_id || '').toLowerCase().includes(q);
        const matchOrg = (u.org || '').toLowerCase().includes(q);
        return matchName || matchHandle || matchSeed || matchOrg;
      }
      return true;
    })
  );

  async function fetchUsers() {
    loading = true;
    loadError = null;
    try {
      users = await loadEditableUsers();
    } catch (err) {
      loadError = err instanceof Error ? err.message : 'Failed to load developer records.';
    } finally {
      loading = false;
    }
  }

  function resetForm() {
    formName = '';
    formSeedId = '';
    formEmail = '';
    formGithub = '';
    formRole = 'contributor';
    formOrg = '';
    formActive = true;
    formIsAdmin = false;
    formError = null;
  }

  function openCreateModal() {
    resetForm();
    showCreateModal = true;
  }

  function openEditModal(u: EditableUserRecord) {
    resetForm();
    editingUser = u;
    formName = u.name;
    formSeedId = u.seed_id || '';
    formEmail = u.email || '';
    formGithub = u.github_handle || '';
    formRole = u.role;
    formOrg = u.org || '';
    formActive = u.active;
    formIsAdmin = u.is_admin;
  }

  function autoGenerateSeedId() {
    if (!formSeedId || formSeedId === '') {
      const slug = formName
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
      if (slug) {
        formSeedId = `usr-${slug}`;
      }
    }
  }

  async function handleCreateSubmit() {
    formError = null;
    successNotice = null;

    if (!formName.trim()) {
      formError = 'Full name is required.';
      return;
    }
    const seed = formSeedId.trim();
    if (seed && !SEED_ID_REGEX.test(seed)) {
      formError = 'Seed ID must follow pattern ^usr-[a-z0-9-]+$ (e.g. usr-john-doe).';
      return;
    }

    submitting = true;
    try {
      const payload: UserInputPayload = {
        name: formName.trim(),
        seed_id: seed || null,
        email: formEmail.trim() || null,
        github_handle: formGithub.trim().replace(/^@/, '') || null,
        role: formRole,
        org: formOrg.trim() || null,
        active: formActive,
        is_admin: formIsAdmin
      };

      await createUser(payload);
      showCreateModal = false;
      successNotice = `Successfully created developer account for ${formName.trim()}.`;
      await fetchUsers();
    } catch (err: unknown) {
      formError = err instanceof Error ? err.message : 'Failed to create developer.';
    } finally {
      submitting = false;
    }
  }

  async function handleUpdateSubmit() {
    if (!editingUser) return;
    formError = null;
    successNotice = null;

    if (!formName.trim()) {
      formError = 'Name is required.';
      return;
    }

    // R5.2 Guard: If user owns projects and admin attempts to deactivate
    if (!formActive && editingUser.active && editingUser.owned_projects.length > 0) {
      formError = `Cannot deactivate developer who owns active projects. This user owns: ${editingUser.owned_projects.join(', ')}. Please reassign project ownership before deactivating.`;
      return;
    }

    submitting = true;
    try {
      const payload: Partial<UserInputPayload> = {
        name: formName.trim(),
        seed_id: formSeedId.trim() || null,
        github_handle: formGithub.trim().replace(/^@/, '') || null,
        role: formRole,
        org: formOrg.trim() || null,
        active: formActive,
        is_admin: formIsAdmin
      };

      await updateUser(editingUser.id, payload);
      editingUser = null;
      successNotice = `Updated details for ${formName.trim()}.`;
      await fetchUsers();
    } catch (err: unknown) {
      formError = err instanceof Error ? err.message : 'Failed to update developer.';
    } finally {
      submitting = false;
    }
  }

  onMount(() => {
    if (auth.isAdmin) {
      void fetchUsers();
    } else {
      loading = false;
    }
  });

  $effect(() => {
    if (auth.isAdmin && users.length === 0 && !loading) {
      void fetchUsers();
    }
  });
</script>

<svelte:head>
  <title>Manage Developers — Cetana Labs Admin</title>
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
        You must be signed in with administrator privileges to manage developers and RBAC tiers.
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
  <div class="mx-auto max-w-content px-4 py-4 sm:px-6 lg:px-8 lg:py-5">
    <AdminNav />

    <!-- Action Bar & Summary -->
    <div class="mb-3.5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-line pb-3">
      <div>
        <h2 class="text-xl font-bold tracking-tight text-ink flex items-center gap-2">
          <span>👥 Developers & Access Control</span>
          <span
            class="rounded-full bg-panel px-2.5 py-0.5 text-xs font-mono font-medium text-muted border border-line"
          >
            {users.length} users
          </span>
        </h2>
        <p class="text-xs text-muted mt-0.5">
          Manage developer profiles, GitHub handle linking, active status, and administrator privileges
          (BK-030).
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          onclick={() => (showHardDeleteInfo = true)}
          class="inline-flex items-center gap-1.5 rounded-md border border-line bg-panel px-3 py-1.5 text-xs font-medium text-muted hover:text-ink hover:bg-canvas transition-colors"
        >
          <span>ℹ️</span>
          <span>Deletion Policy</span>
        </button>
        <button
          type="button"
          onclick={openCreateModal}
          class="inline-flex items-center gap-1.5 rounded-md bg-brand px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition-all hover:bg-brand/90"
        >
          <span>＋</span>
          <span>New Developer</span>
        </button>
      </div>
    </div>

    <!-- Success Notice -->
    {#if successNotice}
      <div
        class="mb-3.5 flex items-center justify-between rounded-lg border border-brand/30 bg-brand-soft/20 px-3.5 py-2 text-xs text-brand-ink"
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

    <!-- Search & Filters -->
    <div class="mb-3.5 grid grid-cols-1 gap-2.5 sm:grid-cols-4">
      <div class="sm:col-span-2">
        <input
          type="search"
          placeholder="Search by name, @handle, ID, or organization…"
          bind:value={searchQuery}
          class="w-full rounded-md border border-line bg-panel px-3 py-1.5 text-xs text-ink placeholder:text-muted focus:border-brand focus:outline-none"
        />
      </div>
      <div>
        <select
          bind:value={roleFilter}
          class="w-full rounded-md border border-line bg-panel px-3 py-1.5 text-xs text-ink focus:border-brand focus:outline-none"
        >
          <option value="all">All Roles</option>
          {#each ROLES as r}
            <option value={r}>{r}</option>
          {/each}
        </select>
      </div>
      <div>
        <select
          bind:value={statusFilter}
          class="w-full rounded-md border border-line bg-panel px-3 py-1.5 text-xs text-ink focus:border-brand focus:outline-none"
        >
          <option value="all">All Statuses</option>
          <option value="active">Active Only</option>
          <option value="inactive">Inactive Only</option>
          <option value="admin">Administrators (🛡️)</option>
        </select>
      </div>
    </div>

    <!-- Main Users Table -->
    {#if loading}
      <div class="flex items-center justify-center py-12 text-muted">
        <span class="text-sm">Loading developer roster…</span>
      </div>
    {:else if loadError}
      <div class="rounded-lg border border-critical-line bg-critical-soft/20 p-4 text-xs text-critical">
        <p class="font-semibold">Error Loading Users</p>
        <p class="mt-1">{loadError}</p>
        <button
          type="button"
          onclick={fetchUsers}
          class="mt-3 rounded border border-line bg-panel px-2.5 py-1 text-xs text-ink hover:bg-canvas"
        >
          Retry
        </button>
      </div>
    {:else if filteredUsers.length === 0}
      <div class="rounded-lg border border-line bg-panel p-8 text-center text-xs text-muted">
        <p class="text-sm font-medium text-ink">No developers match your filters</p>
        <p class="mt-1">Try clearing your search term or selecting "All Roles".</p>
      </div>
    {:else}
      <div class="overflow-x-auto rounded-lg border border-line bg-panel shadow-sm">
        <table class="w-full text-left text-xs">
          <thead
            class="border-b border-line bg-canvas/60 text-xs font-semibold text-muted uppercase tracking-wider"
          >
            <tr>
              <th scope="col" class="py-2.5 pl-3.5 pr-2.5">Developer</th>
              <th scope="col" class="px-2.5 py-2.5">GitHub Handle</th>
              <th scope="col" class="px-2.5 py-2.5">Role & Org</th>
              <th scope="col" class="px-2.5 py-2.5">Owned Projects</th>
              <th scope="col" class="px-2.5 py-2.5">Privileges</th>
              <th scope="col" class="px-2.5 py-2.5">Status</th>
              <th scope="col" class="py-2.5 pl-2.5 pr-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-line text-ink">
            {#each filteredUsers as u (u.id)}
              <tr class="transition-colors hover:bg-canvas/40">
                <td class="py-2.5 pl-3.5 pr-2.5">
                  <div class="font-semibold text-ink">{u.name}</div>
                  <div class="font-mono text-2xs text-muted">{u.seed_id || u.id}</div>
                </td>
                <td class="px-2.5 py-2.5 whitespace-nowrap">
                  {#if u.github_handle}
                    <a
                      href="https://github.com/{u.github_handle}"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="font-mono text-brand hover:underline"
                    >
                      @{u.github_handle}
                    </a>
                  {:else}
                    <span class="text-muted font-mono text-2xs">Unlinked</span>
                  {/if}
                </td>
                <td class="px-2.5 py-2.5">
                  <div class="font-medium capitalize text-ink">{u.role}</div>
                  {#if u.org}
                    <div class="text-2xs text-muted">{u.org}</div>
                  {/if}
                </td>
                <td class="px-2.5 py-2.5">
                  {#if u.owned_projects.length > 0}
                    <div class="flex flex-wrap gap-1">
                      {#each u.owned_projects as pid}
                        <span
                          class="rounded bg-canvas border border-line px-1.5 py-0.5 font-mono text-2xs text-ink font-semibold"
                        >
                          {pid}
                        </span>
                      {/each}
                    </div>
                  {:else}
                    <span class="text-muted text-2xs">None</span>
                  {/if}
                </td>
                <td class="px-2.5 py-2.5 whitespace-nowrap">
                  {#if u.is_admin}
                    <span
                      class="inline-flex items-center gap-1 rounded bg-brand-soft/60 px-2 py-0.5 text-xs font-semibold text-brand-ink"
                    >
                      <span>🛡️</span>
                      <span>Admin</span>
                    </span>
                  {:else}
                    <span class="text-muted text-xs">Standard</span>
                  {/if}
                </td>
                <td class="px-2.5 py-2.5 whitespace-nowrap">
                  {#if u.active}
                    <span
                      class="inline-flex items-center gap-1.5 rounded-full bg-panel px-2.5 py-0.5 text-xs font-medium text-ink border border-line"
                    >
                      <span class="h-1.5 w-1.5 rounded-full bg-brand"></span>
                      <span>Active</span>
                    </span>
                  {:else}
                    <span
                      class="inline-flex items-center gap-1.5 rounded-full bg-panel px-2.5 py-0.5 text-xs font-medium text-muted border border-line"
                    >
                      <span class="h-1.5 w-1.5 rounded-full bg-muted"></span>
                      <span>Inactive</span>
                    </span>
                  {/if}
                </td>
                <td class="py-2.5 pl-2.5 pr-3.5 text-right whitespace-nowrap">
                  <button
                    type="button"
                    onclick={() => openEditModal(u)}
                    class="rounded border border-line bg-canvas px-2.5 py-1 text-xs font-medium text-ink transition-colors hover:border-brand-line hover:text-brand"
                  >
                    Edit / Access
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
{/if}

<!-- Create Developer Modal (R5.3) -->
{#if showCreateModal}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto"
  >
    <div class="relative w-full max-w-lg rounded-card border border-line bg-panel p-6 shadow-xl my-8">
      <div class="flex items-center justify-between border-b border-line pb-3">
        <h3 class="text-base font-bold text-ink flex items-center gap-2">
          <span>＋ Add Developer Account</span>
        </h3>
        <button
          type="button"
          onclick={() => (showCreateModal = false)}
          class="text-muted hover:text-ink text-sm"
        >
          ✕
        </button>
      </div>

      <!-- Information notice about OAuth vs direct creation -->
      <div class="mt-4 rounded border border-line bg-canvas/70 p-3 text-xs text-muted">
        <p class="font-semibold text-ink">💡 Authentication Note</p>
        <p class="mt-0.5">
          The standard developer path is self-sign-in via GitHub OAuth. You can also pre-provision developer
          records here with a seed ID and initial privileges.
        </p>
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
        <div>
          <label for="create-user-name" class="block font-semibold text-ink">Full Name</label>
          <input
            id="create-user-name"
            type="text"
            bind:value={formName}
            onblur={autoGenerateSeedId}
            placeholder="e.g. John Doe"
            required
            class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="create-user-seed" class="block font-semibold text-ink">Seed ID</label>
            <input
              id="create-user-seed"
              type="text"
              bind:value={formSeedId}
              placeholder="usr-john-doe"
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 font-mono text-xs text-ink focus:border-brand focus:outline-none"
            />
            <p class="mt-0.5 text-2xs text-muted">Format: <code class="font-mono">usr-name</code></p>
          </div>

          <div>
            <label for="create-user-github" class="block font-semibold text-ink">GitHub Handle</label>
            <input
              id="create-user-github"
              type="text"
              bind:value={formGithub}
              placeholder="johndoe"
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 font-mono text-xs text-ink focus:border-brand focus:outline-none"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="create-user-role" class="block font-semibold text-ink">Project Role</label>
            <select
              id="create-user-role"
              bind:value={formRole}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            >
              {#each ROLES as r}
                <option value={r}>{r}</option>
              {/each}
            </select>
          </div>

          <div>
            <label for="create-user-org" class="block font-semibold text-ink">Organization</label>
            <input
              id="create-user-org"
              type="text"
              bind:value={formOrg}
              placeholder="e.g. eAgni Technologies"
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            />
          </div>
        </div>

        <div>
          <label for="create-user-email" class="block font-semibold text-ink">Email Address (Optional)</label>
          <input
            id="create-user-email"
            type="email"
            bind:value={formEmail}
            placeholder="leave empty for local auto-fallback"
            class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
          />
        </div>

        <!-- Toggles -->
        <div class="pt-2 border-t border-line space-y-3">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              bind:checked={formIsAdmin}
              class="h-4 w-4 rounded border-line text-brand focus:ring-brand"
            />
            <div>
              <span class="font-semibold text-ink">🛡️ Grant Administrator Privileges (is_admin)</span>
              <p class="text-xs text-muted">
                Authorizes write access to Settings, Projects register, and Developer accounts.
              </p>
            </div>
          </label>

          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              bind:checked={formActive}
              class="h-4 w-4 rounded border-line text-brand focus:ring-brand"
            />
            <span class="font-semibold text-ink">Account Active</span>
          </label>
        </div>

        <div class="flex items-center justify-end gap-3 pt-4 border-t border-line">
          <button
            type="button"
            onclick={() => (showCreateModal = false)}
            disabled={submitting}
            class="rounded border border-line bg-canvas px-4 py-2 text-xs font-semibold text-ink hover:bg-panel disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            class="rounded bg-brand px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-brand/90 disabled:opacity-50"
          >
            {submitting ? 'Creating…' : 'Create Developer'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Edit Developer Modal (R4.2 / R5.2) -->
{#if editingUser}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto"
  >
    <div class="relative w-full max-w-lg rounded-card border border-line bg-panel p-6 shadow-xl my-8">
      <div class="flex items-center justify-between border-b border-line pb-3">
        <h3 class="text-base font-bold text-ink flex items-center gap-2">
          <span>Edit Developer: {editingUser.name}</span>
          {#if editingUser.is_admin}
            <span class="text-xs text-brand font-mono font-medium">🛡️ Admin</span>
          {/if}
        </h3>
        <button type="button" onclick={() => (editingUser = null)} class="text-muted hover:text-ink text-sm">
          ✕
        </button>
      </div>

      <!-- Warning if user owns projects (R5.2) -->
      {#if editingUser.owned_projects.length > 0}
        <div class="mt-4 rounded border border-line bg-canvas p-3 text-xs">
          <span class="font-semibold text-ink">Associated Project Ownership:</span>
          <p class="text-muted mt-0.5">
            This developer owns: <strong class="font-mono text-ink"
              >{editingUser.owned_projects.join(', ')}</strong
            >. Soft deactivation will be blocked until ownership is reassigned.
          </p>
        </div>
      {/if}

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
        <div>
          <label for="edit-user-name" class="block font-semibold text-ink">Full Name</label>
          <input
            id="edit-user-name"
            type="text"
            bind:value={formName}
            required
            class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="edit-user-seed" class="block font-semibold text-ink">Seed ID</label>
            <input
              id="edit-user-seed"
              type="text"
              bind:value={formSeedId}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 font-mono text-xs text-ink focus:border-brand focus:outline-none"
            />
          </div>

          <div>
            <label for="edit-user-github" class="block font-semibold text-ink">GitHub Handle</label>
            <input
              id="edit-user-github"
              type="text"
              bind:value={formGithub}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 font-mono text-xs text-ink focus:border-brand focus:outline-none"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="edit-user-role" class="block font-semibold text-ink">Project Role</label>
            <select
              id="edit-user-role"
              bind:value={formRole}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            >
              {#each ROLES as r}
                <option value={r}>{r}</option>
              {/each}
            </select>
          </div>

          <div>
            <label for="edit-user-org" class="block font-semibold text-ink">Organization</label>
            <input
              id="edit-user-org"
              type="text"
              bind:value={formOrg}
              class="mt-1 w-full rounded border border-line bg-canvas px-3 py-2 text-xs text-ink focus:border-brand focus:outline-none"
            />
          </div>
        </div>

        <!-- Toggles -->
        <div class="pt-2 border-t border-line space-y-3">
          <!-- is_admin toggle (A1 R2.6) -->
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              bind:checked={formIsAdmin}
              class="h-4 w-4 rounded border-line text-brand focus:ring-brand"
            />
            <div>
              <span class="font-semibold text-ink">🛡️ Administrator Privileges (is_admin)</span>
              <p class="text-xs text-muted">Grant or revoke administrator access across the system.</p>
            </div>
          </label>

          <!-- active toggle (soft delete / active state) -->
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              bind:checked={formActive}
              class="h-4 w-4 rounded border-line text-brand focus:ring-brand"
            />
            <div>
              <span class="font-semibold text-ink">Active Status</span>
              <p class="text-xs text-muted">
                Uncheck to soft-deactivate this account without deleting audit records.
              </p>
            </div>
          </label>
        </div>

        <div class="flex items-center justify-end gap-3 pt-4 border-t border-line">
          <button
            type="button"
            onclick={() => (editingUser = null)}
            disabled={submitting}
            class="rounded border border-line bg-canvas px-4 py-2 text-xs font-semibold text-ink hover:bg-panel disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            class="rounded bg-brand px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-brand/90 disabled:opacity-50"
          >
            {submitting ? 'Saving…' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Deletion Policy Explainer Modal (R5.1) -->
{#if showHardDeleteInfo}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
    <div class="relative w-full max-w-md rounded-card border border-line bg-panel p-6 shadow-xl">
      <div class="flex items-center gap-3">
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-soft text-lg text-brand"
        >
          🛡️
        </div>
        <div>
          <h3 class="text-base font-bold text-ink">Developer Deletion Policy</h3>
          <p class="text-xs text-muted">D-CRUD-2 Referential Integrity & Auth Security</p>
        </div>
      </div>

      <div class="mt-4 space-y-2 text-xs text-muted">
        <p>
          Hard-deletion of developer records is disabled in-app (<code class="font-mono text-ink"
            >users.deleteRule = None</code
          >) by design:
        </p>
        <ul class="list-disc pl-4 space-y-1 mt-2">
          <li>
            Prevents orphaning required project owner relations (<code class="font-mono text-ink"
              >cascade=False</code
            >).
          </li>
          <li>Preserves audit history and attribution across historical milestones.</li>
          <li>Protects OAuth identities against account hijacking or duplicate re-seeding.</li>
        </ul>
        <p class="mt-3 text-ink font-medium">
          To revoke a developer's access, edit their account and toggle <strong>Active: Inactive</strong>.
        </p>
      </div>

      <div class="mt-6 flex justify-end">
        <button
          type="button"
          onclick={() => (showHardDeleteInfo = false)}
          class="rounded bg-brand px-4 py-2 text-xs font-semibold text-white hover:bg-brand/90"
        >
          Got it
        </button>
      </div>
    </div>
  </div>
{/if}
