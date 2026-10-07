# Header/Footer Standardization — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `header-footer-standard` |

---

## 1. Approach — consolidate chrome into the global layout

All chrome lives in `+layout.svelte` (header + footer); pages render only their own content. This removes the duplicate branding "second row" and makes the theme toggle global instead of per-page.

```
BEFORE                                   AFTER (standard)
┌ header: logo + name ──── auth ┐        ┌ header: logo + name·desc ─ [nav slot] ─ auth ┐
│ PAGE:                         │        │ PAGE:                                        │
│   masthead: logo+name+desc    │  ──►   │   (dashboard content only — stat cards,      │
│            + ThemeToggle+GH   │        │    tabs, grid)                               │
│   dashboard content           │        │                                              │
└ footer: logo+name · Docs · GH ┘        └ footer: ThemeToggle · logo+name · Docs · GH ─┘
         (ThemeToggle also on /docs)              (single global ThemeToggle)
```

## 2. Component changes

### 2.1 `+layout.svelte` — header (three zones)
```svelte
<header> (border-b, bg-panel/40)
  <div class="mx-auto max-w-content flex items-center justify-between ...">
    <!-- LEFT: branding -->
    <a href="{base}/" class="flex items-center gap-2 ...">
      {#if settings.logoSmallUrl() || settings.logoIconUrl()}
        <img src={...} alt={settings.appName()} class="h-6 w-auto" />
      {/if}
      <span class="font-semibold text-ink">{settings.appName()}</span>
      <span class="text-xs text-muted hidden sm:inline">{settings.appDescription()}</span>
    </a>
    <!-- CENTER: nav slot (empty now; styled container ready for links) -->
    <nav class="hidden md:flex items-center gap-4 text-sm" aria-label="Primary">
      <!-- future routes mount here (R1.2) -->
    </nav>
    <!-- RIGHT: auth -->
    <AuthControl />
  </div>
</header>
```
- Description is a muted inline span, hidden on very narrow screens (keeps the bar uncluttered — standard practice).
- The `<nav>` is present + styled but empty (R1.2) so adding a link later needs no layout change.

### 2.2 `+layout.svelte` — footer (add ThemeToggle, keep Docs public + GitHub)
```svelte
<footer> ...
  <div class="... flex items-center justify-between ...">
    <div class="flex items-center gap-2"> small logo + {appName()} </div>
    <div class="flex items-center gap-4">
      <ThemeToggle />                              <!-- moved here, global (R3.1) -->
      <a href="{base}/docs" ...>Docs</a>           <!-- public, always shown (R3.2/D-HF-1) -->
      <a href="https://github.com/agni-eialarasu/cetana-labs" target="_blank" ...>GitHub ↗</a>
    </div>
  </div>
</footer>
```
- `import ThemeToggle from '$lib/components/ThemeToggle.svelte'` moves into `+layout.svelte`.

### 2.3 `+page.svelte` — strip the second row
- Remove the masthead branding block (logo + `<h1>{appName()}</h1>` + `<p>{appDescription()}</p>`), the `<ThemeToggle/>`, and the GitHub `<a>` (R2).
- Keep everything below it (stat cards, tab bar, sort/search, project grid) untouched. The page's own `<svelte:head><title>` may keep `{appName()}` (that's metadata, not chrome).
- Remove the now-unused `ThemeToggle` import from `+page.svelte`.

### 2.4 `docs/+page.svelte` — drop its ThemeToggle
- Remove the `<ThemeToggle/>` (line 32) + its import; the global footer toggle now serves `/docs` too (R4.4). No other change.

## 3. Risks & mitigations
| Risk | Mitigation |
| :--- | :--- |
| Description crowds a narrow top bar | `hidden sm:inline` on the desc span; name always shows. |
| Theme toggle feels "lost" in the footer | Standard placement; it's global + consistent across routes (V3). A later iteration could add a header affordance if users want it — out of scope here. |
| `/docs` loses its toggle and looks broken | V4/V3 verify the footer toggle controls `/docs` theme; `docs/+page.svelte` keeps its own content. |
| Branding regression | R4.1/R4.2 + V1/V6 — getters unchanged, logo guards unchanged. |

## 4. Why standard header/footer
Conventional webapp chrome: identity + primary nav + account in a fixed header; secondary/utility links + theme + legal in the footer. Centralizing in `+layout.svelte` kills duplication, makes the theme toggle global (one source of truth), and gives a clean, empty nav slot for the routes that come with later features — without touching backend, data, or auth.
