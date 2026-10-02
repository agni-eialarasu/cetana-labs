import DOMPurify from 'dompurify';
import { marked, Renderer } from 'marked';

// src/lib/docs/registry.ts  — the ONE place the in-app doc set is defined.
// NOTE: a doc listed here becomes a CONSUMER SURFACE — editing it changes what
// leads/leadership see in the product. Review such edits with UX impact in mind.
// (See docs/governance/ai-collaboration-model.md — in-app docs are consumer surfaces.)
export const INCLUDED_DOCS = [
  { slug: 'user-guide', src: 'guides/user-guide.md', title: 'User Guide' },
  { slug: 'project-owner', src: 'guides/project-owner-guide.md', title: 'Project Owner Guide' }
  // OPTIONAL third ("how we build this"): enable deliberately.
  // { slug: 'how-we-build', src: 'governance/ai-collaboration-model.md', title: 'How We Build This' },
] as const;

export interface RenderedDoc {
  slug: string;
  src: string;
  title: string;
  html: string;
}

const rawDocs = import.meta.glob<string>('../../../../../docs/**/*.md', {
  query: '?raw',
  import: 'default',
  eager: true
});

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Strips the leading breadcrumb line conforming to docs/README.md navigation standard:
 * e.g. [🏠 Cetana Labs](../../README.md) / [📚 Docs](../README.md) / Guides / **User Guide**
 */
export function stripBreadcrumb(markdown: string): string {
  const lines = markdown.split(/\r?\n/);
  let firstNonEmptyIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim().length > 0) {
      firstNonEmptyIdx = i;
      break;
    }
  }

  if (firstNonEmptyIdx !== -1) {
    const line = lines[firstNonEmptyIdx].trim();
    if (
      /^\[🏠.*?\]\(.*?README\.md\).*?\/\s*\*\*.*?\*\*\s*$/.test(line) ||
      (line.startsWith('[🏠') && line.includes('README.md') && line.includes('**'))
    ) {
      lines.splice(firstNonEmptyIdx, 1);
      while (lines.length > firstNonEmptyIdx && lines[firstNonEmptyIdx].trim().length === 0) {
        lines.splice(firstNonEmptyIdx, 1);
      }
    }
  }
  return lines.join('\n');
}

/**
 * Rewrites a relative repo link from a source doc:
 * - Links to another included doc resolve to that doc's in-app section (?doc=<slug>)
 * - Links to excluded / out-of-app repo files resolve to their canonical GitHub URL
 * - Anchor-only links (#anchor) remain anchors
 * - External URLs remain external
 * - Unresolvable links return null href so they render as plain text
 */
export function rewriteRelativeRepoLink(
  docSrc: string,
  href: string | undefined
): { href: string | null; isExternal: boolean } {
  if (!href) return { href: null, isExternal: false };
  if (/^[a-z]+:/i.test(href)) return { href, isExternal: true };
  if (href.startsWith('#')) return { href, isExternal: false };

  const [pathPart, hashPart] = href.split('#');
  const hash = hashPart ? '#' + hashPart : '';
  if (!pathPart) return { href: hash, isExternal: false };

  // docSrc e.g. 'guides/user-guide.md'. Full path relative to repo root is 'docs/guides/user-guide.md'.
  const docDirParts = ['docs', ...docSrc.split('/').slice(0, -1)];
  const targetParts = pathPart.split('/');

  const resolved = [...docDirParts];
  for (const part of targetParts) {
    if (!part || part === '.') continue;
    if (part === '..') {
      if (resolved.length > 0) {
        resolved.pop();
      } else {
        // Points outside repo root — unresolvable
        return { href: null, isExternal: false };
      }
    } else {
      resolved.push(part);
    }
  }

  const normalized = resolved.join('/');
  if (normalized.startsWith('docs/')) {
    const innerDocPath = normalized.slice(5);
    const included = INCLUDED_DOCS.find((d) => d.src === innerDocPath);
    if (included) {
      return { href: `?doc=${included.slug}${hash}`, isExternal: false };
    }
  }

  const githubUrl = `https://github.com/agni-eialarasu/cetana-labs/blob/main/${normalized}${hash}`;
  return { href: githubUrl, isExternal: true };
}

function createRenderer(docSrc: string): Renderer {
  const renderer = new Renderer();
  renderer.link = ({ href, title, text }) => {
    const resolved = rewriteRelativeRepoLink(docSrc, href);
    if (!resolved.href) {
      return text;
    }
    const titleAttr = title ? ` title="${escapeHtml(title)}"` : '';
    const targetAttr = resolved.isExternal ? ' target="_blank" rel="noopener noreferrer"' : '';
    return `<a href="${escapeHtml(resolved.href)}"${titleAttr}${targetAttr}>${text}</a>`;
  };
  return renderer;
}

export function sanitizeHtml(html: string): string {
  if (typeof window !== 'undefined' && typeof DOMPurify.sanitize === 'function') {
    return DOMPurify.sanitize(html, { ADD_ATTR: ['target', 'rel'] });
  }
  return html;
}

export function loadAndRenderDocs(): RenderedDoc[] {
  return INCLUDED_DOCS.map((doc) => {
    const expectedSuffix = `docs/${doc.src}`;
    const foundEntry = Object.entries(rawDocs).find(([key]) => key.endsWith(expectedSuffix));

    if (!foundEntry || typeof foundEntry[1] !== 'string') {
      throw new Error(
        `[docs/registry] Missing allow-listed doc: "${doc.src}" (expected at docs/${doc.src}). Build failed loud per R5.1.`
      );
    }

    const rawMarkdown = foundEntry[1];
    const strippedMarkdown = stripBreadcrumb(rawMarkdown);
    const renderer = createRenderer(doc.src);
    const renderedHtml = marked.parse(strippedMarkdown, { renderer, gfm: true }) as string;
    const cleanHtml = sanitizeHtml(renderedHtml);

    return {
      slug: doc.slug,
      src: doc.src,
      title: doc.title,
      html: cleanHtml
    };
  });
}

export const DOCS: RenderedDoc[] = loadAndRenderDocs();
