// Domain types for the Control Hub dashboard (RFC-LAB-000-002 / -005).

export type Archetype = 'control-plane' | 'mini-app' | 'research' | 'data-collection' | 'verification';
export type DevEnvironment = 'cloud' | 'local';
export type Role = 'owner' | 'lead' | 'contributor' | 'stakeholder' | 'reviewer';

export interface User {
  id: string;
  name: string;
  email: string | null;
  github_handle: string | null;
  role: Role;
  org: string | null;
  active: boolean;
}

export interface ProjectRecord {
  id: string;
  slug: string;
  name: string;
  descriptor: string | null;
  archetype: Archetype;
  owner_id: string;
  repo_url: string | null;
  reference_url: string | null;
  dev_environment: DevEnvironment;
  status_source: 'local' | 'remote';
  // M3–M4: the PocketBase record id (NOT lab_id) — needed for owner writes
  // (pb.collection('projects').update(pb_id, …)). Null when snapshot-sourced.
  pb_id: string | null;
  // M3–M4: owner-editable status stored on the PB `projects` record (RFC-LAB-000-008
  // §9.1a). Distinct from the status.json executive status (dual-track for MVP).
  status_health: string | null;
  status_note: string | null;
  status_updated_at: string | null;
}

// Live-status layer, keyed by LAB id. `last_updated` is the source of truth for
// time; `days_ago` and `is_stale` are DERIVED from it at read-time (data.ts) and
// are NOT persisted in data/status.json — see BK-020 / RFC-LAB-000-012 §7. Storing
// time-relative values made the file drift stale purely by the calendar advancing.
export interface StatusRecord {
  id: string;
  health: string;
  last_updated: string;
  pitch: string;
  wins: string[];
  focus: string;
  blockers: string;
  risks: string;
  metrics: string[];
  is_onboarding_pending: boolean;
  is_completed: boolean;
  // Derived at read-time from `last_updated` (not present in status.json):
  days_ago: number;
  is_stale: boolean;
}

// The on-disk / on-wire shape of a status.json record: StatusRecord minus the
// read-time-derived time fields.
export type StoredStatusRecord = Omit<StatusRecord, 'days_ago' | 'is_stale'>;

// Merged view consumed by the UI (structural + live status + resolved owner).
export interface Project extends ProjectRecord, Omit<StatusRecord, 'id'> {
  owner_name: string;
  owner_github: string | null;
  archetype_label: string;
  archetype_icon: string;
  has_blocker: boolean;
  severity: 'live' | 'warn' | 'critical' | 'info';
  priority_score: number;
  tags: string[];
}

// App-level settings (RFC-LAB-000-013 / BK-012)
export type SettingType = 'string' | 'number' | 'boolean' | 'url';

export interface SettingRecord {
  key: string;
  value: string;
  type: SettingType;
  group?: string | null;
}
