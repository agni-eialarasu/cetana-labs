<script lang="ts">
  import { base } from '$app/paths';
  import { auth } from '$lib/auth.svelte';
  import { loadEditableSettings, updateSetting, loadSettings } from '$lib/settings.svelte';
  import AdminNav from '$lib/components/AdminNav.svelte';
  import { onMount } from 'svelte';

  interface SettingField {
    id: string;
    key: string;
    label: string;
    description: string;
    type: 'string' | 'url' | 'number' | 'boolean';
    original: string;
    draft: string;
    error: string | null;
  }

  const FIELD_METADATA: Record<string, { label: string; description: string }> = {
    app_name: {
      label: 'Application Name',
      description: 'Main application heading and browser title.'
    },
    app_description: {
      label: 'Application Description',
      description: 'Subheading and descriptor rendered in the header masthead.'
    },
    logo_icon_url: {
      label: 'Logo Icon URL',
      description: 'Square/icon branding mark. Leave empty for text-only branding fallback.'
    },
    logo_small_url: {
      label: 'Logo Small URL',
      description: 'Horizontal logo rendered in the header navigation. Leave empty for text-only fallback.'
    },
    logo_medium_url: {
      label: 'Logo Medium URL',
      description: 'Medium prominent branding asset. Leave empty for text-only fallback.'
    }
  };

  const KEY_ORDER = ['app_name', 'app_description', 'logo_icon_url', 'logo_small_url', 'logo_medium_url'];

  function isValidUrl(val: string): boolean {
    if (!val || val.trim() === '') return true;
    try {
      const u = new URL(val.trim());
      return u.protocol === 'http:' || u.protocol === 'https:';
    } catch {
      return false;
    }
  }

  let loading = $state(true);
  let loadError = $state<string | null>(null);
  let fields = $state<SettingField[]>([]);
  let saving = $state(false);
  let saveError = $state<string | null>(null);
  let saveSuccess = $state<string | null>(null);

  const hasChanges = $derived(fields.some((f) => f.draft !== f.original));

  const hasValidationErrors = $derived(fields.some((f) => f.error !== null));

  function validateField(f: SettingField) {
    if (f.type === 'url') {
      if (!isValidUrl(f.draft)) {
        f.error = 'Must be a valid HTTP or HTTPS URL (or leave empty).';
        return;
      }
    }
    f.error = null;
  }

  async function fetchSettings() {
    loading = true;
    loadError = null;
    try {
      const records = await loadEditableSettings();
      // Sort according to KEY_ORDER, placing any unexpected keys at the end
      const sorted = [...records].sort((a, b) => {
        const idxA = KEY_ORDER.indexOf(a.key);
        const idxB = KEY_ORDER.indexOf(b.key);
        if (idxA !== -1 && idxB !== -1) return idxA - idxB;
        if (idxA !== -1) return -1;
        if (idxB !== -1) return 1;
        return a.key.localeCompare(b.key);
      });

      fields = sorted.map((r) => {
        const meta = FIELD_METADATA[r.key] ?? {
          label: r.key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
          description: `Group: ${r.group ?? 'general'}`
        };
        return {
          id: r.id,
          key: r.key,
          label: meta.label,
          description: meta.description,
          type: r.type,
          original: r.value ?? '',
          draft: r.value ?? '',
          error: null
        };
      });
    } catch (err) {
      loadError = err instanceof Error ? err.message : 'Failed to load application settings.';
    } finally {
      loading = false;
    }
  }

  function handleReset() {
    for (const f of fields) {
      f.draft = f.original;
      f.error = null;
    }
    saveError = null;
    saveSuccess = null;
  }

  async function handleSave() {
    saveError = null;
    saveSuccess = null;

    // Validate all fields first
    for (const f of fields) {
      validateField(f);
    }
    if (fields.some((f) => f.error !== null)) {
      saveError = 'Please fix URL validation errors before saving.';
      return;
    }

    const changed = fields.filter((f) => f.draft !== f.original);
    if (changed.length === 0) return;

    saving = true;
    try {
      for (const f of changed) {
        await updateSetting(f.id, f.draft.trim());
      }
      // Re-populate shared settings accessor so header/footer and all views update live (R2.4)
      await loadSettings();

      // Commit changes to original baseline
      for (const f of changed) {
        f.original = f.draft.trim();
        f.draft = f.original;
      }

      saveSuccess = `Successfully updated ${changed.length} setting${changed.length === 1 ? '' : 's'}. Live branding refreshed.`;
    } catch (err) {
      // Server rule denial (RULE_ADMIN) or network error
      saveError = err instanceof Error ? err.message : 'Save failed.';
    } finally {
      saving = false;
    }
  }

  onMount(() => {
    if (auth.isAdmin) {
      void fetchSettings();
    } else {
      loading = false;
    }
  });

  // If admin state activates after mount (e.g. sign-in without page reload)
  $effect(() => {
    if (auth.isAdmin && fields.length === 0 && !loading) {
      void fetchSettings();
    }
  });
</script>

<svelte:head>
  <title>Application Settings — Cetana Labs</title>
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
        You must be signed in with administrator privileges to access Application Settings.
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
    <!-- Top Navigation & Header -->
    <header class="mb-8 flex flex-col gap-4 border-b border-line pb-6">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <a
            href="{base}/"
            class="inline-flex items-center gap-1.5 text-xs font-semibold text-muted hover:text-ink transition-colors"
          >
            <span>←</span>
            <span>Back to Dashboard</span>
          </a>
          <span class="text-line-strong">•</span>
          <span class="text-xs font-mono text-muted">Admin Controls</span>
        </div>
        <div class="flex items-center gap-2">
          <span
            class="inline-flex items-center gap-1 rounded-[6px] bg-brand-soft px-2 py-0.5 text-xs font-medium text-brand-ink"
          >
            <span>🛡️</span>
            <span>Administrator Tier</span>
          </span>
        </div>
      </div>

      <div>
        <h1 class="text-3xl font-bold tracking-tight text-ink">Application Settings</h1>
        <p class="mt-1 text-sm text-muted">
          Configure application branding, titles, and logo asset URLs. Changes update in-app branding live.
        </p>
      </div>
    </header>

    {#if loading}
      <div class="flex items-center justify-center py-20 text-muted">
        <span class="text-sm">Loading application settings…</span>
      </div>
    {:else if loadError}
      <div class="rounded-card border border-critical/30 bg-critical-soft/30 p-6 text-critical">
        <h2 class="text-base font-semibold">Failed to load settings</h2>
        <p class="mt-1 text-sm">{loadError}</p>
        <button
          type="button"
          onclick={fetchSettings}
          class="mt-4 rounded-control border border-critical bg-panel px-3 py-1.5 text-xs font-semibold text-critical hover:bg-critical-soft"
        >
          Retry
        </button>
      </div>
    {:else}
      <form
        onsubmit={(e) => {
          e.preventDefault();
          handleSave();
        }}
        class="space-y-6 max-w-3xl"
      >
        {#if saveSuccess}
          <div
            class="flex items-center justify-between rounded-control border border-live/40 bg-live-soft/50 p-4 text-sm text-live"
          >
            <div class="flex items-center gap-2">
              <span>✅</span>
              <span>{saveSuccess}</span>
            </div>
            <button
              type="button"
              onclick={() => (saveSuccess = null)}
              class="text-xs font-semibold hover:underline"
            >
              Dismiss
            </button>
          </div>
        {/if}

        {#if saveError}
          <div
            class="flex items-center justify-between rounded-control border border-critical/40 bg-critical-soft/50 p-4 text-sm text-critical"
          >
            <div class="flex items-center gap-2">
              <span>⚠️</span>
              <span>{saveError}</span>
            </div>
            <button
              type="button"
              onclick={() => (saveError = null)}
              class="text-xs font-semibold hover:underline"
            >
              Dismiss
            </button>
          </div>
        {/if}

        <div class="rounded-card border border-line bg-panel p-6 shadow-sm space-y-6">
          <div class="border-b border-line pb-4">
            <h2 class="text-lg font-semibold text-ink">Branding &amp; Identity</h2>
            <p class="text-xs text-muted mt-0.5">
              Custom branding parameters for the Cetana Labs Control Hub.
            </p>
          </div>

          <div class="space-y-5">
            {#each fields as field}
              <div class="flex flex-col gap-1.5">
                <div class="flex items-center justify-between">
                  <label for={field.key} class="text-xs font-semibold text-ink">
                    {field.label}
                    <span class="ml-1 text-[11px] font-mono text-muted font-normal">({field.key})</span>
                  </label>
                  {#if field.draft !== field.original}
                    <span class="text-[10px] font-medium text-warn font-mono">modified</span>
                  {/if}
                </div>

                {#if field.description}
                  <p class="text-xs text-muted">{field.description}</p>
                {/if}

                <div class="flex items-center gap-3">
                  <input
                    id={field.key}
                    type={field.type === 'url' ? 'url' : 'text'}
                    bind:value={field.draft}
                    oninput={() => validateField(field)}
                    placeholder={field.type === 'url' ? 'https://example.com/logo.png (optional)' : ''}
                    class="flex-1 rounded-[6px] border bg-canvas px-3 py-2 text-sm text-ink transition-colors placeholder:text-muted/60 focus:border-brand focus:outline-none {field.error
                      ? 'border-critical'
                      : field.draft !== field.original
                        ? 'border-warn-ink'
                        : 'border-line'}"
                  />

                  {#if field.type === 'url' && field.draft && isValidUrl(field.draft)}
                    <div
                      class="flex h-10 w-10 shrink-0 items-center justify-center rounded-[6px] border border-line bg-canvas p-1"
                      title="Logo preview"
                    >
                      <img
                        src={field.draft}
                        alt="Preview"
                        class="max-h-full max-w-full object-contain"
                        onerror={(e) => {
                          (e.currentTarget as HTMLElement).style.display = 'none';
                        }}
                      />
                    </div>
                  {/if}
                </div>

                {#if field.error}
                  <p class="text-xs text-critical font-medium">{field.error}</p>
                {/if}
              </div>
            {/each}
          </div>

          <div class="flex items-center justify-between border-t border-line pt-5">
            <div class="text-xs text-muted">
              {#if hasChanges}
                <span class="text-warn font-medium">Unsaved changes pending</span>
              {:else}
                <span>All settings up to date</span>
              {/if}
            </div>

            <div class="flex items-center gap-3">
              <button
                type="button"
                onclick={handleReset}
                disabled={!hasChanges || saving}
                class="rounded-control border border-line bg-canvas px-3.5 py-1.5 text-xs font-semibold text-muted transition-colors hover:text-ink disabled:opacity-50"
              >
                Discard Changes
              </button>

              <button
                type="submit"
                disabled={!hasChanges || hasValidationErrors || saving}
                class="rounded-control bg-brand-soft px-4 py-1.5 text-xs font-semibold text-brand-ink transition-colors hover:brightness-110 disabled:opacity-50"
              >
                {saving ? 'Saving…' : 'Save Settings'}
              </button>
            </div>
          </div>
        </div>
      </form>
    {/if}
  </div>
{/if}
