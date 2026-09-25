// Data-access layer (RFC-LAB-000-005 §4).
//
// Phase 2 read model: structural data (users/projects) + live status
// (status.json) are loaded from the bundled data/ snapshot. When the PocketBase
// backend is deployed, `loadProjects` can be swapped to read structural data via
// the PocketBase JS SDK (pb.collection('projects').getFullList({expand:'owner'}))
// while continuing to merge live status until Phase 4 migrates it into the DB.

import { base } from '$app/paths';
import type { User, ProjectRecord, StatusRecord, Project, Archetype } from './types';

const ARCHETYPE: Record<Archetype, { label: string; icon: string }> = {
  'control-plane': { label: 'Control Plane', icon: '💻' },
  'mini-app': { label: 'Mini-App', icon: '💻' },
  research: { label: 'Research', icon: '📑' },
  'data-collection': { label: 'Data Collection', icon: '📊' },
  verification: { label: 'Verification', icon: '🔬' }
};

function severityFor(health: string, hasBlocker: boolean): Project['severity'] {
  const h = health.toLowerCase();
  if (hasBlocker || h.includes('block')) return 'critical';
  if (h.includes('risk') || h.includes('pending')) return 'warn';
  if (h.includes('track') || h.includes('completed')) return 'live';
  return 'info';
}

function priorityScore(p: ProjectRecord, s: StatusRecord, hasBlocker: boolean): number {
  if (p.id === 'LAB-000') return 50;
  if (hasBlocker || s.health.toLowerCase().includes('block')) return 10;
  if (s.health.toLowerCase().includes('risk')) return 15;
  if (s.is_completed) return 40;
  if (s.is_onboarding_pending) return 30;
  return 20;
}

function tagsFor(p: ProjectRecord, s: StatusRecord, hasBlocker: boolean): string[] {
  const tags: string[] = [];
  if (p.id === 'LAB-000') tags.push('control-plane');
  else if (s.is_completed) tags.push('completed');
  else {
    tags.push('active');
    tags.push(s.is_onboarding_pending ? 'onboarding-pending' : 'on-track');
  }
  if (hasBlocker) tags.push('blocked');
  return tags;
}

async function fetchJson<T>(fetchFn: typeof fetch, path: string): Promise<T> {
  const res = await fetchFn(`${base}/data/${path}`);
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
  return (await res.json()) as T;
}

export async function loadProjects(fetchFn: typeof fetch): Promise<Project[]> {
  const [users, projects, statuses] = await Promise.all([
    fetchJson<User[]>(fetchFn, 'users.json'),
    fetchJson<ProjectRecord[]>(fetchFn, 'portfolio.json'),
    fetchJson<StatusRecord[]>(fetchFn, 'status.json')
  ]);

  const usersById = new Map(users.map((u) => [u.id, u]));
  const statusById = new Map(statuses.map((s) => [s.id, s]));

  return projects
    .map((p): Project => {
      const s = statusById.get(p.id) ?? emptyStatus(p.id);
      const owner = usersById.get(p.owner_id);
      const blockers = (s.blockers || '').trim().toLowerCase();
      const hasBlocker =
        (!!blockers && !['none', 'none.', 'n/a'].includes(blockers)) ||
        s.health.toLowerCase().includes('block');
      const arch = ARCHETYPE[p.archetype] ?? { label: p.archetype, icon: '💻' };
      return {
        ...p,
        ...stripId(s),
        owner_name: owner?.name ?? '— Unassigned',
        owner_github: owner?.github_handle ?? null,
        archetype_label: arch.label,
        archetype_icon: arch.icon,
        has_blocker: hasBlocker,
        severity: severityFor(s.health, hasBlocker),
        priority_score: priorityScore(p, s, hasBlocker),
        tags: tagsFor(p, s, hasBlocker)
      };
    })
    .sort((a, b) => a.priority_score - b.priority_score || b.last_updated.localeCompare(a.last_updated));
}

function stripId(s: StatusRecord): Omit<StatusRecord, 'id'> {
  const { id: _omit, ...rest } = s;
  return rest;
}

function emptyStatus(id: string): StatusRecord {
  return {
    id,
    health: '🟢 On Track',
    last_updated: '',
    pitch: '',
    wins: [],
    focus: '',
    blockers: 'None',
    risks: '',
    metrics: [],
    days_ago: 0,
    is_onboarding_pending: false,
    is_completed: false,
    is_stale: false
  };
}
