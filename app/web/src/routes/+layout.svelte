<script lang="ts">
  import '../app.css';
  import { theme } from '$lib/theme.svelte';
  import { settings } from '$lib/settings';
  import AuthControl from '$lib/components/AuthControl.svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import { auth } from '$lib/auth.svelte';
  import { onMount } from 'svelte';
  import { base } from '$app/paths';

  let { children } = $props();

  onMount(() => {
    theme.apply();
    // Re-apply on OS scheme change while in 'system'.
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const onChange = () => theme.choice === 'system' && theme.apply();
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  });
</script>

<div class="min-h-screen flex flex-col bg-canvas text-ink">
  <!-- Global auth bar (M2, R4) + app branding header (BK-013 / R3.1) + center nav slot (BK-027) -->
  <header class="border-b border-line bg-panel/40">
    <div class="mx-auto flex max-w-content items-center justify-between px-4 py-2 sm:px-6 lg:px-8">
      <!-- LEFT: branding -->
      <a href="{base}/" class="flex items-center gap-2 text-sm hover:text-brand transition-colors">
        {#if settings.logoSmallUrl() || settings.logoIconUrl()}
          <img
            src={settings.logoSmallUrl() || settings.logoIconUrl()}
            alt={settings.appName()}
            class="h-6 w-auto"
          />
        {/if}
        <span class="font-semibold text-ink">{settings.appName()}</span>
        <span class="text-xs text-muted hidden sm:inline">{settings.appDescription()}</span>
      </a>

      <!-- CENTER: nav slot (BK-027 center nav / BK-031 admin settings link / BK-014 CRUD) -->
      <nav class="flex items-center gap-2 text-sm" aria-label="Primary">
        {#if auth.isAdmin}
          <a
            href="{base}/admin/projects"
            class="rounded-[6px] px-2.5 py-1 text-xs font-semibold text-ink-secondary transition-colors hover:bg-panel hover:text-ink"
          >
            📁 Projects
          </a>
          <a
            href="{base}/admin/developers"
            class="rounded-[6px] px-2.5 py-1 text-xs font-semibold text-ink-secondary transition-colors hover:bg-panel hover:text-ink"
          >
            👥 Developers
          </a>
          <a
            href="{base}/admin/settings"
            class="rounded-[6px] px-2.5 py-1 text-xs font-semibold text-ink-secondary transition-colors hover:bg-panel hover:text-ink"
          >
            ⚙️ Settings
          </a>
        {/if}
      </nav>

      <!-- RIGHT: auth -->
      <AuthControl />
    </div>
  </header>

  <div class="flex-1">
    {@render children()}
  </div>

  <!-- Minimal consumer-facing footer (BK-024 R2 / BK-013 branding / BK-027 global theme toggle) -->
  <footer class="border-t border-line bg-panel/20 py-6 mt-12">
    <div
      class="mx-auto flex max-w-content items-center justify-between px-4 sm:px-6 lg:px-8 text-xs text-muted"
    >
      <div class="flex items-center gap-2">
        {#if settings.logoIconUrl() || settings.logoSmallUrl()}
          <img
            src={settings.logoIconUrl() || settings.logoSmallUrl()}
            alt={settings.appName()}
            class="h-4 w-auto"
          />
        {/if}
        <span>{settings.appName()}</span>
      </div>
      <div class="flex items-center gap-4">
        <ThemeToggle />
        <a href="{base}/docs" class="text-ink-secondary hover:text-ink transition-colors font-medium">Docs</a>
        <a
          href="https://github.com/agni-eialarasu/cetana-labs"
          target="_blank"
          rel="noopener noreferrer"
          class="hover:text-ink transition-colors"
        >
          GitHub ↗
        </a>
      </div>
    </div>
  </footer>
</div>
