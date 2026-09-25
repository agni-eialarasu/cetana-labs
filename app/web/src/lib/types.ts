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
}

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
  days_ago: number;
  is_onboarding_pending: boolean;
  is_completed: boolean;
  is_stale: boolean;
}

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
