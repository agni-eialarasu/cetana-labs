// Auth store (Svelte 5 runes) — GitHub OAuth sign-in via PocketBase (RFC-LAB-000-008 M2).
//
// Client-side only (static SPA, ssr=false). Backed by the shared `pb.authStore`
// (localStorage-persisted → returning users stay signed in, R2.2) and subscribed via
// `onChange` so the UI reacts to token changes (R2.1). Scope is sign-in only — no RBAC
// enforcement (M3), no writes (M4).
import { pb } from './pb';
import type { User, Role } from './types';

// A signed-in identity resolved against the seeded portfolio (link-by-github_handle, R3).
export interface AuthIdentity {
  /** GitHub login from the OAuth profile (always present when authenticated). */
  githubLogin: string;
  /** Display name — seeded record's name if linked, else the GitHub name/login. */
  name: string;
  /** GitHub avatar URL if trivially available from the OAuth meta (OQ-3). */
  avatarUrl: string | null;
  /** The matched seeded portfolio user, or null when authenticated-but-unlinked (R3.2). */
  linkedUser: User | null;
}

/** Map a PocketBase auth record → the UI `User` shape (mirrors data.ts owner mapping). */
function mapRecord(rec: Record<string, unknown> | null): User | null {
  if (!rec) return null;
  return {
    id: (rec.seed_id as string) ?? (rec.id as string),
    name: (rec.name as string) ?? '',
    email: (rec.email as string) ?? null,
    github_handle: (rec.github_handle as string) || null,
    role: (rec.role as Role) ?? 'contributor',
    org: (rec.org as string) || null,
    active: (rec.active as boolean) ?? true
  };
}

class AuthState {
  /** The resolved identity, or null when anonymous. Reactive. */
  identity = $state<AuthIdentity | null>(null);

  constructor() {
    // Rehydrate from a persisted authStore on load (R2.2), then keep in sync (R2.1).
    this.#sync();
    pb.authStore.onChange(() => this.#sync());
  }

  get isAuthenticated(): boolean {
    return pb.authStore.isValid;
  }

  /** The linked seeded portfolio user, or null if authenticated-but-unlinked. */
  get user(): User | null {
    return this.identity?.linkedUser ?? null;
  }

  /** True when signed in but the GitHub login matches no seeded `github_handle` (R3.2). */
  get isUnlinked(): boolean {
    return this.isAuthenticated && this.identity?.linkedUser == null;
  }

  async signInWithGitHub(): Promise<void> {
    // All-in-one popup OAuth2 flow (R1.1). onChange → #sync updates `identity`.
    await pb.collection('users').authWithOAuth2({ provider: 'github' });
  }

  signOut(): void {
    pb.authStore.clear(); // R1.3 — onChange resets identity to null
  }

  // Resolve the current authStore record into a linked identity (R3.1/R3.2).
  #sync(): void {
    if (!pb.authStore.isValid || !pb.authStore.record) {
      this.identity = null;
      return;
    }
    const rec = pb.authStore.record as unknown as Record<string, unknown>;
    const linked = mapRecord(rec);
    // github_handle on the auth record is the link key against the seeded portfolio.
    const githubLogin = (linked?.github_handle ?? (rec.username as string) ?? '').toString();
    // A record with a seeded github_handle is "linked"; otherwise authenticated-but-unlinked.
    const isLinked = !!linked?.github_handle;
    this.identity = {
      githubLogin,
      name: linked?.name || githubLogin || 'Signed in',
      avatarUrl: (rec.avatarURL as string) || (rec.avatarUrl as string) || null,
      linkedUser: isLinked ? linked : null
    };
  }
}

export const auth = new AuthState();
