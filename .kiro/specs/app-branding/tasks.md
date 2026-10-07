# App Branding & White-Labeling — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `app-branding` |
| **Branch** | `feat/app-branding` (self-created by the build; off up-to-date `main`) |
| **Execution** | **Antigravity Executor** (clone `cetana-labs-antigravity/`) — SPA wiring + reserved-key seed, cost-first default per `RFC-LAB-000-014`. Escalate to Kiro IDE only if the logo-render/theme path proves deeper than scoped (record why). |
| **Kickoff** | `/spec-run app-branding` |
| **EARS target** | R1–R5 in `requirements.md`; DoD = the Human Verification Plan (V1–V7). |

---

## T0 — Preflight + baseline (STOP on failure) → P1–P6
- [ ] Surface = an Executor clone; local PocketBase + SvelteKit reachable (`/start-local`); `git`, Node/pnpm on PATH. *(P1, P2)*
- [ ] This Spec merged to `main` (merge-first). *(P4)*
- [ ] **BK-012 present on `main`:** `settings` collection + `SettingsAccessor` exist (PR #64). *(P5)*
- [ ] Create `feat/app-branding` off up-to-date `main`; clean tree; not `main`. *(P3)*
- [ ] Baseline green: 5 validators + `generate_pb_schema.py --check` + `pnpm --dir app/web check && build`. *(P6)*

## T1 — Seed the logo set → R1
- [ ] Add `logo_icon_url`, `logo_small_url`, `logo_medium_url` to `data/settings.json` (`type: "url"`, `group: "branding"`, `value: ""`). *(R1.1)*
- [ ] Confirm `data/settings.schema.json` already permits them; run `generate_pb_schema.py --check` → green (additive data only, no collection change). *(R1.2)*

## T2 — Extend the accessor → R2
- [ ] Add `logo_icon_url`/`logo_small_url`/`logo_medium_url: ''` to `SETTINGS_DEFAULTS`. *(R2.2)*
- [ ] Add typed getters `logoIconUrl()`/`logoSmallUrl()`/`logoMediumUrl()` on `SettingsAccessor`, built on `get<T>()` (no raw-row access). *(R2.1)*

## T3 — Render branding with fallback → R3
- [ ] `+layout.svelte` header: render logo (`logoSmallUrl()` ‖ `logoIconUrl()`) before `appName()`, guarded by `{#if url}`. *(R3.1)*
- [ ] `+page.svelte` masthead: logo beside the `<h1>` app name. *(R3.1)*
- [ ] Fallback: empty URL ⇒ text-only, no broken image, no layout shift (fixed height reserves space). *(R3.2)*
- [ ] `<img alt={appName()}>`; size-by-height + `w-auto`, no forced background (theme-safe). *(R3.3)*

## T4 — White-label deploy path → R4
- [ ] Document "White-labeling a deploy" in `developer-guide.md`: set name/description/logo via `data/settings.json` (snapshot) or the `settings` collection (live); the `VITE_PB_SOURCE` toggle; data-change-not-code-change. *(R4.1)*
- [ ] Prove end-to-end: set a non-default `app_name` + `logo_small_url`, confirm the served UI reflects both. *(R4.2 → V4)*

## T5 — Gates, lockstep, PR → R5
- [ ] `pnpm --dir app/web check && build`, `just validate-local`, 5 validators (incl. `--check`) all green. *(R5.1)*
- [ ] No secret in settings; with no logo set the app is unchanged from today. *(R5.2)*
- [ ] Scope floor held: `data/settings.json` + accessor + 2 surfaces + docs only; no new field type / upload / editor UI / collection change. *(R5.3)*
- [ ] Lockstep: `CHANGELOG.md` `[Unreleased]` entry (BK-013 / TSK-060); flip `SPRINT_TRACKER.md` TSK-060 status at build.
- [ ] Append `REPORT.md` (implementation summary + the Human Verification Plan V1–V7, left for `/verification-done`).
- [ ] Open PR `feat/app-branding → main`; **self-validate against the EARS DoD**; STOP-and-hold (never merge).

## Post-build (back on the Operator)
- `/verification-done` (Executor) records V1–V7 PASS → IN_REVIEW.
- `/review-pr` (Operator) gates → human squash-merge → BK-013 Done; the SPRINT-12 BK-012→BK-013 product line is complete.
