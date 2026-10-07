import { loadSettings } from '$lib/settings';
import type { LayoutLoad } from './$types';

// Static SPA: no SSR (RFC-LAB-000-005 §2 — client-side PocketBase/data access).
export const ssr = false;
export const prerender = true;

export const load: LayoutLoad = async ({ fetch }) => {
  await loadSettings(fetch);
  return {};
};
