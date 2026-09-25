<script lang="ts">
  import { theme, type Theme } from '$lib/theme.svelte';

  const options: { value: Theme; label: string; icon: string }[] = [
    { value: 'system', label: 'System', icon: '🖥' },
    { value: 'light', label: 'Light', icon: '☀' },
    { value: 'dark', label: 'Dark', icon: '🌙' }
  ];
</script>

<div class="inline-flex rounded-control border border-line bg-panel p-0.5" role="group" aria-label="Theme">
  {#each options as opt (opt.value)}
    <button
      type="button"
      class="flex items-center gap-1 rounded-[6px] px-2.5 py-1.5 text-xs font-semibold transition-colors
        {theme.choice === opt.value ? 'bg-brand-soft text-brand-ink' : 'text-muted hover:text-ink'}"
      aria-pressed={theme.choice === opt.value}
      onclick={() => theme.set(opt.value)}
    >
      <span aria-hidden="true">{opt.icon}</span>
      <span>{opt.label}</span>
    </button>
  {/each}
</div>
