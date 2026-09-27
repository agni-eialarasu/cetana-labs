/// <reference types="vite/client" />

// Client-exposed env vars for the Sleek UI data layer (RFC-LAB-000-008 M1).
interface ImportMetaEnv {
  /** Base URL of the live PocketBase backend (default http://127.0.0.1:8090). */
  readonly VITE_PB_URL?: string;
  /** Data source switch: 'pocketbase' | 'snapshot' | 'auto' (default 'auto'). */
  readonly VITE_PB_SOURCE?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
