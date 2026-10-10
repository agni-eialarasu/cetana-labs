<script lang="ts">
  import { theme } from '$lib/theme.svelte';

  interface Props {
    src: string;
    title: string;
    description?: string;
    heightClass?: string;
  }

  let { src, title, description, heightClass = 'h-[620px]' }: Props = $props();

  const themeVars = $derived.by(() => {
    const isDark = theme.resolved === 'dark';
    if (isDark) {
      return `
        color-scheme: dark;
        --text: #f1f2fa;
        --text-strong: #ffffff;
        --text-secondary: #c2c7d9;
        --muted: #9aa3bb;
        --muted-strong: #c2c7d9;
        --bg: #13151f;
        --bg-elevated: #1b1e2b;
        --bg-subtle: #242839;
        --bg-hover: #242839;
        --card: #1b1e2b;
        --card-fg: #f1f2fa;
        --border: #2b3043;
        --border-strong: #414a63;
        --accent: #60a5fa;
        --accent-hover: #93c5fd;
        --accent-subtle: #1e3a5f;
        --info: #60a5fa;
        --info-subtle: #1e3a5f;
        --ok: #34d399;
        --ok-subtle: #10331f;
        --warn: #fbbf24;
        --warn-subtle: #3a2f0c;
      `;
    } else {
      return `
        color-scheme: light;
        --text: #202436;
        --text-strong: #111827;
        --text-secondary: #50596d;
        --muted: #667086;
        --muted-strong: #50596d;
        --bg: #f5f7fc;
        --bg-elevated: #ffffff;
        --bg-subtle: #edf0f7;
        --bg-hover: #e5e7eb;
        --card: #ffffff;
        --card-fg: #202436;
        --border: #e3e7f0;
        --border-strong: #cbd2e2;
        --accent: #2563eb;
        --accent-hover: #1d4ed8;
        --accent-subtle: #eff6ff;
        --info: #2563eb;
        --info-subtle: #dbeafe;
        --ok: #059669;
        --ok-subtle: #e7f6ee;
        --warn: #b45309;
        --warn-subtle: #fef3e2;
      `;
    }
  });

  const srcdoc = $derived.by(() => {
    const styleOpen = '<' + 'style>';
    const styleClose = '<' + '/style>';
    const injection = `<base target="_parent">${styleOpen}
      :root {
        ${themeVars}
      }
      html, body {
        background-color: var(--bg) !important;
        color: var(--text) !important;
      }
    ${styleClose}`;

    if (src.includes('<head>')) {
      return src.replace('<head>', `<head>${injection}`);
    }
    return `${injection}${src}`;
  });
</script>

<div class="rounded-card border border-line bg-panel/30 p-5 md:p-6 shadow-sm">
  <div class="mb-4 flex flex-col gap-1 border-b border-line pb-4">
    <div class="flex items-center justify-between gap-3">
      <h3 class="text-base font-bold text-ink">{title}</h3>
      <span class="rounded-full border border-line bg-panel px-2.5 py-0.5 text-[11px] font-mono text-muted">
        Living Diagram
      </span>
    </div>
    {#if description}
      <p class="text-xs text-muted leading-relaxed">{description}</p>
    {/if}
  </div>

  <div class="relative w-full overflow-hidden rounded-control border border-line bg-panel">
    <!-- Sandboxed iframe: strictly allow-scripts only; no allow-same-origin, no allow-top-navigation -->
    <iframe
      sandbox="allow-scripts"
      {srcdoc}
      {title}
      class="w-full {heightClass} border-0 transition-opacity duration-150"
      loading="lazy"
    ></iframe>
  </div>

  <div class="mt-3 flex items-center justify-between text-[11px] text-muted">
    <span>Interactive · Click tabs and nodes for detail popovers</span>
    <span class="font-mono">sandbox="allow-scripts"</span>
  </div>
</div>
