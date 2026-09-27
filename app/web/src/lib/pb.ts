// Shared PocketBase client (RFC-LAB-000-008 M2).
//
// A single `pb` instance for the whole app so `pb.authStore` is consistent across
// the data layer (data.ts) and the auth store (auth.svelte.ts). The app is a static
// SPA (ssr=false), so this runs client-side; the JS SDK persists the auth token to
// localStorage by default (returning users stay signed in — R2.2).
import PocketBase from 'pocketbase';

export const PB_URL = import.meta.env.VITE_PB_URL ?? 'http://127.0.0.1:8090'; // R4.1

export const pb = new PocketBase(PB_URL);

// The portfolio load is a single burst of requests; disable auto-cancellation so
// concurrent reads aren't cancelled (preserves the M1 behavior from data.ts).
pb.autoCancellation(false);
