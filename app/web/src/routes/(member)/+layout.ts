// Guard for the (member) route group (RFC-LAB-000-008 M2, R5.1). Any route nested under
// (member) requires authentication; unauthenticated users are redirected to the public
// dashboard. The public dashboard (routes/+page.*) is OUTSIDE this group and never guarded.
import type { LayoutLoad } from './$types';
import { requireAuth } from '$lib/guard';

export const ssr = false;
export const prerender = false; // member routes are auth-gated, not prerenderable

export const load: LayoutLoad = () => {
  return requireAuth();
};
