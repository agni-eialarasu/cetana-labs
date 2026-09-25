<script lang="ts">
  import type { Project } from '$lib/types';
  let { health, severity }: { health: string; severity: Project['severity'] } = $props();

  // severity -> soft/ink token classes (color + word, never color alone).
  const styles: Record<Project['severity'], string> = {
    live: 'bg-live-soft text-live border-live/30',
    warn: 'bg-warn-soft text-warn-ink border-warn/30',
    critical: 'bg-critical-soft text-critical border-critical/40',
    info: 'bg-info-soft text-info border-info/30'
  };
</script>

<span
  class="inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold {styles[
    severity
  ]}"
>
  {health}
</span>
