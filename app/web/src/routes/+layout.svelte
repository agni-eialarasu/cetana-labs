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
<div class="flex justify-end border-b border-line bg-panel/40 px-4 py-2">
  <AuthControl />
</div>

{@render children()}
