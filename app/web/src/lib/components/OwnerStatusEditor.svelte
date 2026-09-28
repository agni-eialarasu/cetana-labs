<script lang="ts">
  // Owner-only status editor (RFC-LAB-000-008 M4, R3). Renders ONLY when the signed-in
  // user owns this project (UX affordance). The security boundary is the PocketBase
  // owner updateRule (R5) — a non-owner write is rule-denied regardless of this control.
  import type { Project } from '$lib/types';
  import { untrack } from 'svelte';
  import { pb } from '$lib/pb';
  import { auth } from '$lib/auth.svelte';

  let { project }: { project: Project } = $props();

  // Ownership (UX only): linked seeded user id === the project's owner seed id.
  const isOwner = $derived(!!auth.user && auth.user.id === project.owner_id && !!project.pb_id);

  const HEALTH_OPTIONS = [
    '🟢 On Track',
    '🟡 At Risk',
    '🔴 Blocked',
    '⏸️ Paused',
    '✅ Completed',
    '⏳ Onboarding Pending'
  ];

  let editing = $state(false);
  let saving = $state(false);
  let error = $state<string | null>(null);
  // Local edit buffer (draft while editing).
  let health = $state('');
  let note = $state('');
  // Last-saved values shown when not editing. Intentionally seeded ONCE from the prop:
  // after a successful save we set these from the record refetch (R3.4), and the parent
  // reloads fresh data on navigation — so this component owns the displayed value between
  // saves. (Initial-only capture is deliberate here.)
  let savedHealth = $state(untrack(() => project.status_health ?? ''));
  let savedNote = $state(untrack(() => project.status_note ?? ''));

  function startEdit() {
    health = savedHealth;
    note = savedNote;
    error = null;
    editing = true;
  }

  async function save() {
    if (!project.pb_id) return;
    saving = true;
    error = null;
    try {
      await pb.collection('projects').update(project.pb_id, {
        status_health: health,
        status_note: note,
        status_updated_at: new Date().toISOString()
      });
      // Reflect by reading the record back (R3.4) rather than trusting local state.
      const fresh = await pb.collection('projects').getOne(project.pb_id);
      savedHealth = (fresh.status_health as string) ?? '';
      savedNote = (fresh.status_note as string) ?? '';
      editing = false;
    } catch (err) {
      // A non-owner write would land here (rule-denied) — surface it, don't crash.
      error = err instanceof Error ? err.message : 'Save failed.';
    } finally {
      saving = false;
    }
  }
</script>

{#if isOwner}
  <div class="rounded-control border border-brand/30 bg-brand-soft/30 p-3">
    <div class="mb-1.5 flex items-center justify-between">
      <span class="text-[11px] font-bold uppercase tracking-wide text-brand-ink">✏️ Your status (owner)</span>
      {#if !editing}
        <button
          type="button"
          class="text-xs font-semibold text-brand hover:text-brand-hover"
          onclick={startEdit}
        >
          Edit
        </button>
      {/if}
    </div>

    {#if editing}
      <div class="flex flex-col gap-2">
        <label class="flex flex-col gap-1 text-xs text-muted">
          Health
          <select
            bind:value={health}
            class="rounded-[6px] border border-line bg-panel px-2 py-1.5 text-sm text-ink"
          >
            <option value="">— none —</option>
            {#each HEALTH_OPTIONS as opt}
              <option value={opt}>{opt}</option>
            {/each}
          </select>
        </label>
        <label class="flex flex-col gap-1 text-xs text-muted">
          Note
          <input
            type="text"
            bind:value={note}
            placeholder="Short status note"
            class="rounded-[6px] border border-line bg-panel px-2 py-1.5 text-sm text-ink"
          />
        </label>
        {#if error}
          <p class="text-xs text-critical">{error}</p>
        {/if}
        <div class="flex gap-2">
          <button
            type="button"
            class="rounded-control bg-brand-soft px-2.5 py-1.5 text-xs font-semibold text-brand-ink hover:brightness-110 disabled:opacity-60"
            onclick={save}
            disabled={saving}
          >
            {saving ? 'Saving…' : 'Save'}
          </button>
          <button
            type="button"
            class="rounded-control border border-line bg-panel px-2.5 py-1.5 text-xs font-semibold text-muted hover:text-ink"
            onclick={() => (editing = false)}
            disabled={saving}
          >
            Cancel
          </button>
        </div>
      </div>
    {:else}
      <div class="text-sm text-ink">
        {savedHealth || '— not set —'}
        {#if savedNote}
          <span class="text-ink-secondary"> · {savedNote}</span>
        {/if}
      </div>
    {/if}
  </div>
{/if}
