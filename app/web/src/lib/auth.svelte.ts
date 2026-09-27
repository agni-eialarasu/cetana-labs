// Auth store (Svelte 5 runes) — GitHub OAuth sign-in via PocketBase (RFC-LAB-000-008 M2).
//
// Client-side only (static SPA, ssr=false). Backed by the shared `pb.authStore`
// (localStorage-persisted → returning users stay signed in, R2.2). All UI-facing state
// is exposed via `$state` so the header reacts live to sign-in/out (R2.1) without a reload.
//
// Linking (R3): PocketBase creates a SEPARATE auth record per GitHub identity — it does
// NOT reuse a pre-seeded row. So we resolve the seeded portfolio owner by matching the
// GitHub login (from the OAuth `meta`, or the record's stored github_handle on rehydrate)
// against the seeded `users` records' `github_handle`, case-insensitive. No match ⇒
// authenticated-but-unlinked (R3.2); we never auto-provision a seeded record.
import { pb } from './pb';
import type { User, Role } from './types';

const LINK_KEY = 'cetana-gh-login'; // persist the resolved GitHub login across reloads

export interface AuthIdentity {
  /** GitHub login (lowercased) resolved from OAuth meta / persisted on rehydrate. */
  githubLogin: string;
  /** Display name — seeded record's name if linked, else the GitHub name/login. */
  name: string;
  /** GitHub avatar URL if available from the OAuth meta (OQ-3). */
  avatarUrl: string | null;
  /** The matched seeded portfolio user, or null when authenticated-but-unlinked (R3.2). */
  linkedUser: User | null;
}

/** Map a seeded PocketBase `users` record → the UI `User` shape (mirrors data.ts). */
function mapRecord(rec: Record<string, unknown> | null): User | null {
  if (!rec) return null;
  return {
    id: (rec.seed_id as string) || (rec.id as string),
    name: (rec.name as string) ?? '',
    email: (rec.email as string) ?? null,
    github_handle: (rec.github_handle as string) || null,
    role: (rec.role as Role) ?? 'contributor',
    org: (rec.org as string) || null,
    active: (rec.active as boolean) ?? true
  };
}

/** Look up a seeded user whose github_handle matches `login` (case-insensitive). */
async function resolveSeededOwner(login: string): Promise<User | null> {
  if (!login) return null;
  try {
    const safe = login.replace(/["\\]/g, '');
    // github_handle is publicly viewable (M1 viewRule=""), so this works while signed in too.
    const list = await pb.collection('users').getFullList({
      filter: `github_handle ~ "${safe}"`
    });
    const hit = list.find(
      (r) => ((r as Record<string, unknown>).github_handle as string)?.toLowerCase() === login
    );
    return hit ? mapRecord(hit as unknown as Record<string, unknown>) : null;
  } catch (err) {
    console.warn('[auth] owner resolution failed; treating as unlinked.', err);
    return null;
  }
}

/** Extract the GitHub login from an authWithOAuth2 result's meta. */
function loginFromMeta(meta: unknown): string {
  const m = (meta ?? {}) as Record<string, unknown>;
  const raw = (m.rawUser ?? {}) as Record<string, unknown>;
  return ((raw.login as string) || (m.username as string) || '').toString().toLowerCase();
}

class AuthState {
  /** Reactive auth flag — drives the UI (do NOT read pb.authStore.isValid in templates). */
  #authed = $state<boolean>(pb.authStore.isValid);
  /** The resolved identity, or null when anonymous. Reactive. */
  identity = $state<AuthIdentity | null>(null);

  constructor() {
    // Rehydrate from a persisted authStore on load (R2.2).
    if (pb.authStore.isValid) void this.#rehydrate();
    // Keep the reactive flag in sync with token changes across tabs / SDK events.
    pb.authStore.onChange((token) => {
      this.#authed = pb.authStore.isValid;
      if (!token) this.identity = null;
    });
  }

  get isAuthenticated(): boolean {
    return this.#authed;
  }

  get user(): User | null {
    return this.identity?.linkedUser ?? null;
  }

  get isUnlinked(): boolean {
    return this.#authed && this.identity?.linkedUser == null;
  }

  async signInWithGitHub(): Promise<void> {
    // All-in-one popup OAuth2 flow (R1.1). Capture meta to resolve the seeded owner.
    const res = await pb.collection('users').authWithOAuth2({ provider: 'github' });
    this.#authed = pb.authStore.isValid; // reactive flip immediately (R1.2 — no reload)
    const login = loginFromMeta(res.meta);
    if (login && typeof localStorage !== 'undefined') localStorage.setItem(LINK_KEY, login);
    await this.#resolve(login, res.meta);
  }

  signOut(): void {
    pb.authStore.clear(); // R1.3
    this.#authed = false; // reactive flip immediately (no reload)
    this.identity = null;
    if (typeof localStorage !== 'undefined') localStorage.removeItem(LINK_KEY);
  }

  // Rebuild identity from persisted state on page load (no OAuth meta available).
  async #rehydrate(): Promise<void> {
    const login =
      (typeof localStorage !== 'undefined' && localStorage.getItem(LINK_KEY)) ||
      ((pb.authStore.record as unknown as Record<string, unknown>)?.github_handle as string) ||
      '';
    await this.#resolve(login.toLowerCase(), null);
  }

  // Resolve the seeded owner for `login` and set the reactive identity (R3.1/R3.2).
  async #resolve(login: string, meta: unknown): Promise<void> {
    const linked = await resolveSeededOwner(login);
    const m = (meta ?? {}) as Record<string, unknown>;
    const raw = (m.rawUser ?? {}) as Record<string, unknown>;
    const rec = pb.authStore.record as unknown as Record<string, unknown> | null;
    this.identity = {
      githubLogin: login,
      name: linked?.name || (raw.name as string) || login || 'Signed in',
      avatarUrl: (m.avatarURL as string) || (raw.avatar_url as string) || (rec?.avatar as string) || null,
      linkedUser: linked
    };
  }
}

export const auth = new AuthState();
