<script lang="ts">
  import '../app.css';
  import { theme } from '$lib/theme.svelte';
  import AuthControl from '$lib/components/AuthControl.svelte';
  import { onMount } from 'svelte';

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

<!-- Global auth bar (M2, R4). Present on every route; never gates the public dashboard. -->
<!-- Full-bleed border/background; inner container matches the page body width so the -->
<!-- control aligns to the body's right edge (not the browser edge). -->
<div class="border-b border-line bg-panel/40">
  <div class="mx-auto flex max-w-content justify-end px-4 py-2 sm:px-6 lg:px-8">
    <AuthControl />
  </div>
</div>

{@render children()}
