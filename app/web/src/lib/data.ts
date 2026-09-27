// Data-access layer (RFC-LAB-000-005 §4, RFC-LAB-000-008 M1).
//
// M1 read model: structural data (projects + resolved owner) is loaded from the
// live PocketBase backend via the JS SDK, while live status (status.json) is still
// merged from the bundled data/ snapshot (status migration into the DB is deferred
// to a later MVP phase — RFC-LAB-000-008 §7). The static-snapshot path is retained
// as a configurable fallback so the dashboard never blanks if PocketBase is
// unreachable (dual-run posture, RFC-LAB-000-008 §9.4).
//
// Source selection (R4/R5):
//   VITE_PB_SOURCE=pocketbase → force live PocketBase
//   VITE_PB_SOURCE=snapshot   → force bundled snapshot
//   unset / "auto"            → PocketBase when reachable, else snapshot fallback

import { base } from '$app/paths';
import { pb } from './pb'; // shared PocketBase client (M2 — one authStore app-wide)
import type { User, ProjectRecord, StatusRecord, Project, Archetype } from './types';

const PB_SOURCE = (import.meta.env.VITE_PB_SOURCE ?? 'auto').toLowerCase();

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

// --- Structural data sources (R1/R5) -------------------------------------------------

interface StructuralData {
  users: User[];
  projects: ProjectRecord[];
}

// Existing behavior: read structural masters from the bundled snapshot (fallback path).
async function loadFromSnapshot(fetchFn: typeof fetch): Promise<StructuralData> {
  const [users, projects] = await Promise.all([
    fetchJson<User[]>(fetchFn, 'users.json'),
    fetchJson<ProjectRecord[]>(fetchFn, 'portfolio.json')
  ]);
  return { users, projects };
}

// M1: read structural data from live PocketBase via the JS SDK (R1.1/R1.2/R1.3).
// Maps PocketBase `projects` fields to the UI ProjectRecord shape (requirements §2)
// and derives the User[] from the expanded owner relation (dedup by seed_id).
async function loadFromPocketBase(): Promise<StructuralData> {
  // Uses the shared `pb` client (autoCancellation already disabled in lib/pb.ts).
  const records = await pb.collection('projects').getFullList({ expand: 'owner' });

  const usersBySeedId = new Map<string, User>();
  const projects: ProjectRecord[] = records.map((r): ProjectRecord => {
    const owner = (r.expand as { owner?: Record<string, unknown> } | undefined)?.owner;
    const ownerSeedId = (owner?.seed_id as string) ?? (r.owner as string);
    if (owner && ownerSeedId && !usersBySeedId.has(ownerSeedId)) {
      usersBySeedId.set(ownerSeedId, {
        id: ownerSeedId,
        name: (owner.name as string) ?? '',
        email: (owner.email as string) ?? null,
        github_handle: (owner.github_handle as string) || null,
        role: (owner.role as User['role']) ?? 'owner',
        org: (owner.org as string) || null,
        active: (owner.active as boolean) ?? true
      });
    }
    return {
      id: r.lab_id as string, // lab_id → UI id
      slug: r.slug as string,
      name: r.name as string,
      descriptor: (r.descriptor as string) || null,
      archetype: r.archetype as Archetype,
      owner_id: ownerSeedId,
      repo_url: (r.repo_url as string) || null,
      reference_url: (r.reference_url as string) || null,
      dev_environment: r.dev_environment as ProjectRecord['dev_environment'],
      status_source: r.status_source as ProjectRecord['status_source']
    };
  });

  return { users: [...usersBySeedId.values()], projects };
}

// Source switch + graceful fallback (R5): PocketBase when configured/reachable,
// else the bundled snapshot. Never throws an unhandled error that blanks the board.
async function loadProjectRecords(fetchFn: typeof fetch): Promise<StructuralData> {
  if (PB_SOURCE === 'snapshot') return loadFromSnapshot(fetchFn);

  try {
    const data = await loadFromPocketBase();
    if (data.projects.length > 0) return data;
    if (PB_SOURCE === 'pocketbase') return data; // forced: honor empty result
    console.warn('[data] PocketBase returned no projects — falling back to snapshot.');
  } catch (err) {
    if (PB_SOURCE === 'pocketbase') throw err; // forced: surface the error
    console.warn('[data] PocketBase unreachable — falling back to snapshot.', err);
  }
  return loadFromSnapshot(fetchFn);
}

export async function loadProjects(fetchFn: typeof fetch): Promise<Project[]> {
  const [{ users, projects }, statuses] = await Promise.all([
    loadProjectRecords(fetchFn),
    fetchJson<StatusRecord[]>(fetchFn, 'status.json') // M1: status stays snapshot-sourced (R2)
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
