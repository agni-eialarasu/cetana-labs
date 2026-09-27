// Route-guard helper (RFC-LAB-000-008 M2, R5). Redirects to sign-in when the user is
// not authenticated. Used by member-only route groups; the public dashboard is NEVER
// guarded (it lives outside the (member) group). M3/M4 adopt this without rework.
import { redirect } from '@sveltejs/kit';
import { base } from '$app/paths';
import { auth } from './auth.svelte';

/**
 * Guard a member-only route. Call from a `(member)/+layout.ts` `load`.
 * When unauthenticated, redirects to the public dashboard (the sign-in entry point).
 * Returns the resolved auth state for the layout to expose to children.
 */
export function requireAuth(): { authenticated: true } {
  if (!auth.isAuthenticated) {
    // 307: temporary — the user may sign in and retry. base handles the Pages subpath.
    throw redirect(307, `${base}/`);
  }
  return { authenticated: true };
}
