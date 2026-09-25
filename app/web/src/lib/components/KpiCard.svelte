<script lang="ts">
  let {
    label,
    value,
    sub,
    tone = 'default',
    onclick
  }: {
    label: string;
    value: number;
    sub: string;
    tone?: 'default' | 'brand' | 'live' | 'warn' | 'critical' | 'muted';
    onclick?: () => void;
  } = $props();

  const toneClass: Record<string, string> = {
    default: 'text-ink',
    brand: 'text-brand',
    live: 'text-live',
    warn: 'text-warn',
    critical: 'text-critical',
    muted: 'text-muted'
  };
</script>

<button
  type="button"
  class="flex flex-col gap-1 rounded-card border border-line bg-panel p-4 text-left transition-colors hover:border-brand-line"
  {onclick}
>
  <span class="text-[11px] font-semibold uppercase tracking-wider text-muted">{label}</span>
  <span class="tabular text-3xl font-bold {toneClass[tone]}">{value}</span>
  <span class="text-xs text-muted">{sub}</span>
</button>
