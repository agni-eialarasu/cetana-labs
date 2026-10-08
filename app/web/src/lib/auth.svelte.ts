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
// Cross-redirect state for the manual OAuth2 code-exchange flow (BK-018 / RFC-011 §4.5).
// The redirect flow leaves the page to GitHub and returns to /oauth/callback, so the
// PKCE codeVerifier + CSRF state must survive the round-trip. sessionStorage (not local)
// because they're single-use and short-lived — least residue (design §8, OQ-2).
const OAUTH_VERIFIER_KEY = 'cetana-oauth-code-verifier';
const OAUTH_STATE_KEY = 'cetana-oauth-state';
const OAUTH_PROVIDER = 'github';

/** The frontend callback URL GitHub redirects back to (env-derived — design §2, OQ-3). */
function redirectURL(): string {
  return `${window.location.origin}/oauth/callback`;
}

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

  get isAdmin(): boolean {
    return (
      this.#authed && (pb.authStore.record as unknown as Record<string, unknown> | null)?.is_admin === true
    );
  }

  // START half of the redirect OAuth2 flow (R1.1, R1.3). Unlike the old all-in-one popup
  // (authWithOAuth2), this NEVER opens /api/realtime — the channel Railway's proxy breaks
  // on PB 0.40 (spike-confirmed, RFC-011 §4.5). Instead we redirect the whole page to
  // GitHub and finish on the /oauth/callback route via completeOAuthCallback().
  async signInWithGitHub(): Promise<void> {
    const methods = await pb.collection('users').listAuthMethods();
    const provider = methods.oauth2?.providers?.find((p) => p.name === OAUTH_PROVIDER);
    if (!provider) {
      throw new Error(`OAuth provider "${OAUTH_PROVIDER}" is not configured on the server.`);
    }
    // Persist the PKCE verifier + CSRF state across the redirect round-trip (R1.2).
    sessionStorage.setItem(OAUTH_VERIFIER_KEY, provider.codeVerifier);
    sessionStorage.setItem(OAUTH_STATE_KEY, provider.state);
    // Leave the SPA for GitHub; provider.authURL already carries ?state= and PKCE params,
    // we only append our own redirect target. Returns to /oauth/callback.
    window.location.assign(provider.authURL + encodeURIComponent(redirectURL()));
  }

  // CALLBACK half (R1.2, R1.4): invoked by the /oauth/callback route on return from GitHub.
  // Verifies the CSRF state, exchanges the code for a session via authWithOAuth2Code (no
  // popup, no realtime), then reuses the M2 post-auth resolve so github_handle linking and
  // owner-write (R2.1/R2.2) are unchanged. Throws on any failure so the route can show a
  // clear error + retry (design §4).
  async completeOAuthCallback(code: string, state: string): Promise<void> {
    const savedVerifier = sessionStorage.getItem(OAUTH_VERIFIER_KEY);
    const savedState = sessionStorage.getItem(OAUTH_STATE_KEY);
    // One-shot values — clear immediately so a replayed callback can't reuse them.
    sessionStorage.removeItem(OAUTH_VERIFIER_KEY);
    sessionStorage.removeItem(OAUTH_STATE_KEY);

    if (!code || !state) throw new Error('Missing authorization code or state.');
    if (!savedState || !savedVerifier) throw new Error('No pending sign-in — please try again.');
    if (state !== savedState) throw new Error('State mismatch — sign-in was rejected (CSRF guard).');

    const res = await pb
      .collection('users')
      .authWithOAuth2Code(OAUTH_PROVIDER, code, savedVerifier, redirectURL());
    this.#authed = pb.authStore.isValid; // reactive flip immediately (R1.4 — no reload)
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
