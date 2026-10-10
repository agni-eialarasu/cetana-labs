import DOMPurify from 'dompurify';

let idCounter = 0;

/**
 * Renders all mermaid code blocks inside a given container element.
 * - Dynamic-imports mermaid lazily only when mermaid blocks are present.
 * - Client-only, SSR-safe (requires DOM and window).
 * - Sanitizes SVG output with DOMPurify SVG profile before DOM injection.
 * - Fail-soft: per-block try/catch leaves the original <pre><code> intact on failure.
 * - Supports re-rendering on theme change ('dark' | 'default').
 */
export async function renderMermaidIn(
  container: HTMLElement | null,
  theme: 'dark' | 'default' = 'dark'
): Promise<void> {
  if (typeof window === 'undefined' || !container) {
    return;
  }

  const rawBlocks = Array.from(container.querySelectorAll<HTMLElement>('code.language-mermaid'));
  const renderedBlocks = Array.from(container.querySelectorAll<HTMLElement>('div[data-mermaid-src]'));

  if (rawBlocks.length === 0 && renderedBlocks.length === 0) {
    return;
  }

  try {
    const mermaidModule = await import('mermaid');
    const mermaid = mermaidModule.default;

    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      theme
    });

    // 1. Process unrendered raw blocks: <pre><code class="language-mermaid">...</code></pre>
    for (const codeEl of rawBlocks) {
      const source = codeEl.textContent?.trim() || '';
      if (!source) continue;

      const preEl = codeEl.closest('pre') || codeEl;
      const renderId = `mermaid-svg-${Date.now()}-${++idCounter}`;

      try {
        const { svg } = await mermaid.render(renderId, source);
        const cleanSvg = DOMPurify.sanitize(svg, {
          USE_PROFILES: { svg: true, svgFilters: true }
        });

        const wrapper = document.createElement('div');
        wrapper.className = 'mermaid-block flex justify-center my-6 overflow-x-auto';
        wrapper.setAttribute('data-mermaid-src', source);
        wrapper.innerHTML = cleanSvg;

        preEl.parentNode?.replaceChild(wrapper, preEl);
      } catch (err) {
        console.warn(`[mermaid] Failed to render block (renderId: ${renderId}):`, err);
        // Clean up any lingering temporary DOM nodes created by mermaid
        const stray = document.getElementById(renderId) || document.getElementById(`d${renderId}`);
        if (stray) stray.remove();
        // Fail-soft: leave original pre/code block untouched
      }
    }

    // 2. Process previously rendered blocks on theme change
    for (const blockEl of renderedBlocks) {
      const source = blockEl.getAttribute('data-mermaid-src')?.trim() || '';
      if (!source) continue;

      const renderId = `mermaid-svg-${Date.now()}-${++idCounter}`;

      try {
        const { svg } = await mermaid.render(renderId, source);
        const cleanSvg = DOMPurify.sanitize(svg, {
          USE_PROFILES: { svg: true, svgFilters: true }
        });

        blockEl.innerHTML = cleanSvg;
      } catch (err) {
        console.warn(`[mermaid] Failed to re-render block on theme change (renderId: ${renderId}):`, err);
        const stray = document.getElementById(renderId) || document.getElementById(`d${renderId}`);
        if (stray) stray.remove();
      }
    }
  } catch (err) {
    console.warn('[mermaid] Failed to load mermaid module:', err);
  }
}
