<script lang="ts">
  import { DOCS, INCLUDED_DOCS } from '$lib/docs/registry';
  import { page } from '$app/state';
  import { base } from '$app/paths';

  // Read ?doc=<slug> from query param, default to first included doc
  const docParam = $derived(page.url.searchParams.get('doc'));
  const activeDoc = $derived(DOCS.find((d) => d.slug === docParam) ?? DOCS[0]);
</script>

<svelte:head>
  <title>{activeDoc ? `${activeDoc.title} — Cetana Labs Docs` : 'Documentation — Cetana Labs'}</title>
</svelte:head>

<div class="mx-auto max-w-content px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
  <!-- Top Navigation & Header -->
  <header class="mb-8 flex flex-col gap-4 border-b border-line pb-6">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <a
          href="{base}/"
          class="inline-flex items-center gap-1.5 text-xs font-semibold text-muted hover:text-ink transition-colors"
        >
          <span>←</span>
          <span>Back to Dashboard</span>
        </a>
        <span class="text-line-strong">•</span>
        <span class="text-xs font-mono text-muted">Help &amp; Documentation</span>
      </div>
      <div class="flex items-center gap-3">
        <a
          href="https://github.com/agni-eialarasu/cetana-labs"
          target="_blank"
          rel="noopener noreferrer"
          class="rounded-control border border-line bg-panel px-3.5 py-1.5 text-xs font-semibold text-ink hover:border-brand-line transition-colors"
        >
          GitHub ↗
        </a>
      </div>
    </div>

    <div>
      <h1 class="text-3xl font-bold tracking-tight text-ink">Documentation</h1>
      <p class="mt-1 text-sm text-muted">
        Authoritative guides and playbooks for maintainers, project leads, and collaborators.
      </p>
    </div>
  </header>

  <!-- Two-Column Layout: Doc Picker Sidebar + Rendered Content -->
  <div class="grid grid-cols-1 md:grid-cols-[240px_1fr] gap-8 items-start">
    <!-- Sidebar / Doc Picker -->
    <aside class="sticky top-6 flex flex-col gap-6">
      <div class="rounded-card border border-line bg-panel/40 p-4">
        <div class="mb-3 px-2 text-xs font-semibold uppercase tracking-wider text-muted">
          Included Guides
        </div>
        <nav class="flex flex-col gap-1" aria-label="Documentation navigation">
          {#each DOCS as doc (doc.slug)}
            {@const isActive = activeDoc?.slug === doc.slug}
            <a
              href="{base}/docs?doc={doc.slug}"
              class="flex items-center justify-between rounded-control px-3 py-2 text-sm transition-colors {isActive
                ? 'border border-brand-line bg-brand-soft/30 font-semibold text-brand'
                : 'text-ink-secondary hover:bg-panel hover:text-ink'}"
            >
              <span>{doc.title}</span>
              {#if isActive}
                <span class="text-xs text-brand">●</span>
              {/if}
            </a>
          {/each}
        </nav>
      </div>

      <div class="rounded-card border border-line/60 bg-panel/20 p-4 text-xs text-muted">
        <div class="font-semibold text-ink-secondary mb-1">Looking for Contributor Docs?</div>
        <p class="leading-relaxed">
          RFCs, Decision Journals, and internal architecture specs live on GitHub.
        </p>
        <a
          href="https://github.com/agni-eialarasu/cetana-labs/tree/main/docs"
          target="_blank"
          rel="noopener noreferrer"
          class="mt-2.5 inline-block text-brand hover:underline"
        >
          Browse docs/ on GitHub ↗
        </a>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="min-w-0">
      {#if activeDoc}
        <article class="rounded-card border border-line bg-panel/20 p-6 md:p-8">
          <!-- Doc Meta Header -->
          <div class="mb-6 flex flex-wrap items-center justify-between gap-2 border-b border-line pb-4">
            <div>
              <span class="text-xs font-mono text-muted">docs/{activeDoc.src}</span>
            </div>
            <a
              href="https://github.com/agni-eialarasu/cetana-labs/blob/main/docs/{activeDoc.src}"
              target="_blank"
              rel="noopener noreferrer"
              class="text-xs text-muted hover:text-brand transition-colors"
            >
              View source on GitHub ↗
            </a>
          </div>

          <!-- Rendered HTML Content -->
          <div class="doc-content">
            {@html activeDoc.html}
          </div>
        </article>
      {:else}
        <div class="rounded-card border border-line bg-panel/20 p-8 text-center text-muted">
          Doc not found. Please select a guide from the sidebar.
        </div>
      {/if}
    </main>
  </div>
</div>

<style>
  /* Scoped typography for rendered markdown content, matching Sleek UI design tokens */
  .doc-content :global(h1) {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--np-text);
    margin-top: 1.5rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--np-border);
    line-height: 1.25;
  }

  .doc-content :global(h2) {
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--np-text);
    margin-top: 2rem;
    margin-bottom: 0.75rem;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid var(--np-border);
    line-height: 1.3;
  }

  .doc-content :global(h3) {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--np-text);
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    line-height: 1.35;
  }

  .doc-content :global(h4) {
    font-size: 1rem;
    font-weight: 600;
    color: var(--np-text);
    margin-top: 1.25rem;
    margin-bottom: 0.5rem;
  }

  .doc-content :global(p) {
    font-size: 0.9375rem;
    line-height: 1.65;
    color: var(--np-text-secondary);
    margin-bottom: 1rem;
  }

  .doc-content :global(ul) {
    list-style-type: disc;
    padding-left: 1.5rem;
    margin-bottom: 1.25rem;
    color: var(--np-text-secondary);
    font-size: 0.9375rem;
    line-height: 1.6;
  }

  .doc-content :global(ol) {
    list-style-type: decimal;
    padding-left: 1.5rem;
    margin-bottom: 1.25rem;
    color: var(--np-text-secondary);
    font-size: 0.9375rem;
    line-height: 1.6;
  }

  .doc-content :global(li) {
    margin-bottom: 0.35rem;
  }

  .doc-content :global(blockquote) {
    border-left: 3px solid var(--np-accent);
    background-color: var(--np-bg-subtle);
    padding: 0.75rem 1rem;
    margin: 1.25rem 0;
    border-radius: 0 6px 6px 0;
    color: var(--np-text-muted);
    font-style: italic;
    font-size: 0.9rem;
  }

  .doc-content :global(blockquote p:last-child) {
    margin-bottom: 0;
  }

  .doc-content :global(table) {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    font-size: 0.875rem;
    border: 1px solid var(--np-border);
    border-radius: 8px;
    overflow: hidden;
  }

  .doc-content :global(th) {
    background-color: var(--np-bg-elevated);
    color: var(--np-text);
    font-weight: 600;
    text-align: left;
    padding: 0.65rem 0.85rem;
    border-bottom: 1px solid var(--np-border);
  }

  .doc-content :global(td) {
    padding: 0.65rem 0.85rem;
    border-bottom: 1px solid var(--np-border);
    color: var(--np-text-secondary);
  }

  .doc-content :global(tr:last-child td) {
    border-bottom: none;
  }

  .doc-content :global(pre) {
    background-color: var(--np-bg-subtle);
    border: 1px solid var(--np-border);
    border-radius: 8px;
    padding: 1rem;
    overflow-x: auto;
    font-family: var(--font-mono, monospace);
    font-size: 0.8125rem;
    line-height: 1.5;
    color: var(--np-text);
    margin: 1.25rem 0;
  }

  .doc-content :global(code) {
    font-family: var(--font-mono, monospace);
    font-size: 0.85em;
    background-color: var(--np-bg-subtle);
    border: 1px solid var(--np-border);
    color: var(--np-accent-ink);
    padding: 0.15rem 0.35rem;
    border-radius: 4px;
  }

  .doc-content :global(pre code) {
    background: transparent;
    border: none;
    padding: 0;
    color: inherit;
    font-size: inherit;
  }

  .doc-content :global(a) {
    color: var(--np-accent);
    text-decoration: underline;
    text-underline-offset: 3px;
    transition: color 0.15s ease;
  }

  .doc-content :global(a:hover) {
    color: var(--np-accent-hover);
  }

  .doc-content :global(hr) {
    border: 0;
    border-top: 1px solid var(--np-border);
    margin: 2rem 0;
  }

  .doc-content :global(strong) {
    color: var(--np-text);
    font-weight: 600;
  }
</style>
