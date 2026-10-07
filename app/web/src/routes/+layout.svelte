<script lang="ts">
  import '../app.css';
  import { theme } from '$lib/theme.svelte';
  import { settings } from '$lib/settings';
  import AuthControl from '$lib/components/AuthControl.svelte';
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
  <!-- Global auth bar (M2, R4). Present on every route; never gates the public dashboard. -->
  <!-- Full-bleed border/background; inner container matches the page body width so the -->
  <!-- control aligns to the body's right edge (not the browser edge). -->
  <div class="border-b border-line bg-panel/40">
    <div class="mx-auto flex max-w-content justify-end px-4 py-2 sm:px-6 lg:px-8">
      <AuthControl />
    </div>
  </div>

  <div class="flex-1">
    {@render children()}
  </div>

  <!-- Minimal consumer-facing footer (BK-024 R2; branded footer chrome deferred to BK-013) -->
  <footer class="border-t border-line bg-panel/20 py-6 mt-12">
    <div
      class="mx-auto flex max-w-content items-center justify-between px-4 sm:px-6 lg:px-8 text-xs text-muted"
    >
      <div>{settings.appName()}</div>
      <div class="flex items-center gap-4">
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
