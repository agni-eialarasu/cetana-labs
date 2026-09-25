<script lang="ts">
  import '../app.css';
  import { theme } from '$lib/theme.svelte';
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

{@render children()}
