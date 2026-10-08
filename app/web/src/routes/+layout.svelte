<script lang="ts">
  import '../app.css';
  import { theme } from '$lib/theme.svelte';
  import { settings } from '$lib/settings';
  import AuthControl from '$lib/components/AuthControl.svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import { auth } from '$lib/auth.svelte';
  import { onMount } from 'svelte';
  import { base } from '$app/paths';
  import { page } from '$app/state';

  let { children } = $props();

  const pathname = $derived(page.url.pathname);

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
  <header class="border-b border-line bg-panel/60 backdrop-blur-sm sticky top-0 z-40">
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

      <!-- CENTER: unified primary nav slot (BK-027 / BK-031 / BK-014 CRUD) -->
      <nav class="flex items-center gap-1.5 text-xs font-medium" aria-label="Primary">
        <a
          href="{base}/"
          class="flex items-center gap-1.5 rounded-md px-3 py-1.5 transition-all {pathname === '/'
            ? 'bg-panel text-brand font-semibold shadow-sm border border-line'
            : 'text-muted hover:text-ink hover:bg-panel/50'}"
        >
          <span>📊</span>
          <span>Portfolio</span>
        </a>

        {#if auth.isAdmin}
          <div class="h-4 w-px bg-line mx-1" aria-hidden="true"></div>

          <a
            href="{base}/admin/projects"
            class="flex items-center gap-1.5 rounded-md px-3 py-1.5 transition-all {pathname.startsWith(
              '/admin/projects'
            )
              ? 'bg-panel text-brand font-semibold shadow-sm border border-line'
              : 'text-muted hover:text-ink hover:bg-panel/50'}"
          >
            <span>📁</span>
            <span>Projects</span>
          </a>
          <a
            href="{base}/admin/developers"
            class="flex items-center gap-1.5 rounded-md px-3 py-1.5 transition-all {pathname.startsWith(
              '/admin/developers'
            )
              ? 'bg-panel text-brand font-semibold shadow-sm border border-line'
              : 'text-muted hover:text-ink hover:bg-panel/50'}"
          >
            <span>👥</span>
            <span>Developers</span>
          </a>
          <a
            href="{base}/admin/settings"
            class="flex items-center gap-1.5 rounded-md px-3 py-1.5 transition-all {pathname.startsWith(
              '/admin/settings'
            )
              ? 'bg-panel text-brand font-semibold shadow-sm border border-line'
              : 'text-muted hover:text-ink hover:bg-panel/50'}"
          >
            <span>⚙️</span>
            <span>Settings</span>
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
  <footer class="border-t border-line bg-panel/20 py-3.5 mt-6">
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
