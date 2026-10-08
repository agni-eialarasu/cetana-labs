// CRUD data layer & API façade (BK-014 / RFC-LAB-000-008 A1 & D-CRUD-1).
//
// Admin-gated write and read operations for projects and developers (users),
// interacting directly with live PocketBase collections via pb.collection(...).

import { base } from '$app/paths';
import { pb } from './pb';
import type { Archetype, DevEnvironment, Role } from './types';

export interface EditableProjectRecord {
  id: string; // PocketBase internal record ID
  lab_id: string; // e.g. LAB-000
  slug: string;
  name: string;
  descriptor: string | null;
  archetype: Archetype;
  owner: string; // User PB record ID
  owner_seed_id: string | null;
  owner_name: string;
  owner_github: string | null;
  repo_url: string | null;
  reference_url: string | null;
  dev_environment: DevEnvironment;
  status_source: 'local' | 'remote';
  status_health: string | null;
  status_note: string | null;
  status_updated_at: string | null;
}

export interface EditableUserRecord {
  id: string; // PocketBase internal record ID
  seed_id: string | null; // e.g. usr-eialarasu
  name: string;
  email: string | null;
  github_handle: string | null;
  role: Role;
  org: string | null;
  active: boolean;
  is_admin: boolean;
  owned_projects: string[]; // List of lab_ids owned
}

export interface ProjectInputPayload {
  lab_id: string;
  slug: string;
  name: string;
  descriptor?: string | null;
  archetype: Archetype;
  owner: string; // PB record ID
  repo_url?: string | null;
  reference_url?: string | null;
  dev_environment: DevEnvironment;
  status_source: 'local' | 'remote';
  status_health?: string | null;
  status_note?: string | null;
}

export interface UserInputPayload {
  name: string;
  seed_id?: string | null;
  email?: string | null;
  github_handle?: string | null;
  role: Role;
  org?: string | null;
  active: boolean;
  is_admin: boolean;
}

export const ARCHETYPES: { value: Archetype; label: string; icon: string }[] = [
  { value: 'control-plane', label: 'Control Plane', icon: '💻' },
  { value: 'mini-app', label: 'Mini-App', icon: '💻' },
  { value: 'research', label: 'Research', icon: '📑' },
  { value: 'data-collection', label: 'Data Collection', icon: '📊' },
  { value: 'verification', label: 'Verification', icon: '🔬' }
];

export const HEALTH_OPTIONS = [
  '🟢 On Track',
  '🟡 At Risk',
  '🔴 Blocked',
  '⏸️ Paused',
  '✅ Completed',
  '⏳ Onboarding Pending'
] as const;

export const ROLES: Role[] = ['owner', 'lead', 'contributor', 'stakeholder', 'reviewer'];

/** Load all projects from live PocketBase with owner expanded */
export async function loadEditableProjects(): Promise<EditableProjectRecord[]> {
  const records = await pb.collection('projects').getFullList({
    expand: 'owner',
    sort: 'lab_id'
  });

  return records.map((r): EditableProjectRecord => {
    const ownerRec = (r.expand as { owner?: Record<string, unknown> } | undefined)?.owner;
    return {
      id: r.id,
      lab_id: (r.lab_id as string) || '',
      slug: (r.slug as string) || '',
      name: (r.name as string) || '',
      descriptor: (r.descriptor as string) || null,
      archetype: (r.archetype as Archetype) || 'mini-app',
      owner: (r.owner as string) || '',
      owner_seed_id: (ownerRec?.seed_id as string) || null,
      owner_name: (ownerRec?.name as string) || (ownerRec?.github_handle as string) || 'Unknown',
      owner_github: (ownerRec?.github_handle as string) || null,
      repo_url: (r.repo_url as string) || null,
      reference_url: (r.reference_url as string) || null,
      dev_environment: (r.dev_environment as DevEnvironment) || 'cloud',
      status_source: (r.status_source as 'local' | 'remote') || 'local',
      status_health: (r.status_health as string) || null,
      status_note: (r.status_note as string) || null,
      status_updated_at: (r.status_updated_at as string) || null
    };
  });
}

/** Create a new project in PocketBase */
export async function createProject(payload: ProjectInputPayload): Promise<EditableProjectRecord> {
  const data: Record<string, unknown> = {
    lab_id: payload.lab_id.trim().toUpperCase(),
    slug: payload.slug.trim().toLowerCase(),
    name: payload.name.trim(),
    descriptor: payload.descriptor?.trim() || '',
    archetype: payload.archetype,
    owner: payload.owner,
    repo_url: payload.repo_url?.trim() || '',
    reference_url: payload.reference_url?.trim() || '',
    dev_environment: payload.dev_environment,
    status_source: payload.status_source,
    status_health: payload.status_health || '',
    status_note: payload.status_note?.trim() || '',
    status_updated_at: new Date().toISOString()
  };

  const rec = await pb.collection('projects').create(data, { expand: 'owner' });
  const ownerRec = (rec.expand as { owner?: Record<string, unknown> } | undefined)?.owner;

  return {
    id: rec.id,
    lab_id: rec.lab_id as string,
    slug: rec.slug as string,
    name: rec.name as string,
    descriptor: (rec.descriptor as string) || null,
    archetype: rec.archetype as Archetype,
    owner: rec.owner as string,
    owner_seed_id: (ownerRec?.seed_id as string) || null,
    owner_name: (ownerRec?.name as string) || (ownerRec?.github_handle as string) || 'Unknown',
    owner_github: (ownerRec?.github_handle as string) || null,
    repo_url: (rec.repo_url as string) || null,
    reference_url: (rec.reference_url as string) || null,
    dev_environment: rec.dev_environment as DevEnvironment,
    status_source: rec.status_source as 'local' | 'remote',
    status_health: (rec.status_health as string) || null,
    status_note: (rec.status_note as string) || null,
    status_updated_at: (rec.status_updated_at as string) || null
  };
}

/** Update an existing project in PocketBase */
export async function updateProject(id: string, payload: Partial<ProjectInputPayload>): Promise<void> {
  const data: Record<string, unknown> = {};
  if (payload.lab_id !== undefined) data.lab_id = payload.lab_id.trim().toUpperCase();
  if (payload.slug !== undefined) data.slug = payload.slug.trim().toLowerCase();
  if (payload.name !== undefined) data.name = payload.name.trim();
  if (payload.descriptor !== undefined) data.descriptor = payload.descriptor?.trim() || '';
  if (payload.archetype !== undefined) data.archetype = payload.archetype;
  if (payload.owner !== undefined) data.owner = payload.owner;
  if (payload.repo_url !== undefined) data.repo_url = payload.repo_url?.trim() || '';
  if (payload.reference_url !== undefined) data.reference_url = payload.reference_url?.trim() || '';
  if (payload.dev_environment !== undefined) data.dev_environment = payload.dev_environment;
  if (payload.status_source !== undefined) data.status_source = payload.status_source;
  if (payload.status_health !== undefined) data.status_health = payload.status_health || '';
  if (payload.status_note !== undefined) data.status_note = payload.status_note?.trim() || '';

  data.status_updated_at = new Date().toISOString();

  await pb.collection('projects').update(id, data);
}

/** Delete a project in PocketBase */
export async function deleteProject(id: string): Promise<void> {
  await pb.collection('projects').delete(id);
}

/** Load all developers (users) from live PocketBase */
export async function loadEditableUsers(): Promise<EditableUserRecord[]> {
  const [users, projects] = await Promise.all([
    pb.collection('users').getFullList({ sort: 'name' }),
    pb.collection('projects').getFullList()
  ]);

  // Compute map of user PB ID -> list of owned project lab_ids
  const ownedMap = new Map<string, string[]>();
  for (const p of projects) {
    const ownerId = p.owner as string;
    if (!ownerId) continue;
    const list = ownedMap.get(ownerId) || [];
    list.push((p.lab_id as string) || (p.name as string));
    ownedMap.set(ownerId, list);
  }

  return users.map((u): EditableUserRecord => {
    return {
      id: u.id,
      seed_id: (u.seed_id as string) || null,
      name: (u.name as string) || '',
      email: (u.email as string) || null,
      github_handle: (u.github_handle as string) || null,
      role: (u.role as Role) || 'contributor',
      org: (u.org as string) || null,
      active: (u.active as boolean) ?? true,
      is_admin: (u.is_admin as boolean) === true,
      owned_projects: ownedMap.get(u.id) || []
    };
  });
}

/** Create a new developer (user) in PocketBase */
export async function createUser(payload: UserInputPayload): Promise<EditableUserRecord> {
  const generatedId = (
    payload.seed_id?.trim() || `usr-${payload.name.toLowerCase().replace(/[^a-z0-9]/g, '-')}`
  ).replace(/--+/g, '-');
  const email = payload.email?.trim() || `${generatedId}@cetana.local`;
  // PocketBase auth collections require password and passwordConfirm on create
  const randomPw = Math.random().toString(36).slice(-10) + 'A1!aX#9';

  const data: Record<string, unknown> = {
    seed_id: generatedId,
    name: payload.name.trim(),
    email,
    github_handle: payload.github_handle?.trim().replace(/^@/, '') || '',
    role: payload.role,
    org: payload.org?.trim() || '',
    active: payload.active,
    is_admin: payload.is_admin,
    password: randomPw,
    passwordConfirm: randomPw
  };

  const rec = await pb.collection('users').create(data);

  return {
    id: rec.id,
    seed_id: (rec.seed_id as string) || null,
    name: (rec.name as string) || '',
    email: (rec.email as string) || null,
    github_handle: (rec.github_handle as string) || null,
    role: (rec.role as Role) || 'contributor',
    org: (rec.org as string) || null,
    active: (rec.active as boolean) ?? true,
    is_admin: (rec.is_admin as boolean) === true,
    owned_projects: []
  };
}

/** Update an existing user in PocketBase */
export async function updateUser(id: string, payload: Partial<UserInputPayload>): Promise<void> {
  const data: Record<string, unknown> = {};
  if (payload.name !== undefined) data.name = payload.name.trim();
  if (payload.seed_id !== undefined) data.seed_id = payload.seed_id?.trim() || '';
  if (payload.github_handle !== undefined)
    data.github_handle = payload.github_handle?.trim().replace(/^@/, '') || '';
  if (payload.role !== undefined) data.role = payload.role;
  if (payload.org !== undefined) data.org = payload.org?.trim() || '';
  if (payload.active !== undefined) data.active = payload.active;
  if (payload.is_admin !== undefined) data.is_admin = payload.is_admin;

  await pb.collection('users').update(id, data);
}

export interface DivergenceStatus {
  isDiverged: boolean;
  projectDiff: number;
  userDiff: number;
  details: string[];
}

/**
 * Check if the live PocketBase database differs from the committed data/ snapshot (D-CRUD-1 / R7.2).
 * Compares record counts and key identifiers/properties.
 */
export async function checkDataDivergence(fetchFn: typeof fetch = fetch): Promise<DivergenceStatus> {
  try {
    const [snapshotUsersRes, snapshotProjectsRes, liveProjects, liveUsers] = await Promise.all([
      fetchFn(`${base}/data/users.json`),
      fetchFn(`${base}/data/portfolio.json`),
      loadEditableProjects(),
      loadEditableUsers()
    ]);

    if (!snapshotUsersRes.ok || !snapshotProjectsRes.ok) {
      return {
        isDiverged: false,
        projectDiff: 0,
        userDiff: 0,
        details: []
      };
    }

    const snapshotUsers = (await snapshotUsersRes.json()) as {
      id: string;
      name: string;
      role: string;
      active?: boolean;
    }[];
    const snapshotProjects = (await snapshotProjectsRes.json()) as {
      id: string;
      name: string;
      slug: string;
      owner_id: string;
    }[];

    const details: string[] = [];

    // 1. Projects comparison
    let projectDiff = 0;
    const snapProjMap = new Map(snapshotProjects.map((p) => [p.id, p]));
    const liveProjMap = new Map(liveProjects.map((p) => [p.lab_id, p]));

    for (const [lab_id, live] of liveProjMap) {
      const snap = snapProjMap.get(lab_id);
      if (!snap) {
        projectDiff++;
        details.push(
          `Project ${lab_id} (${live.name}) is present in live DB but missing in data/portfolio.json`
        );
      } else if (snap.name !== live.name || snap.slug !== live.slug) {
        projectDiff++;
        details.push(`Project ${lab_id} differs in live DB vs snapshot (name or slug modified)`);
      }
    }
    for (const [id] of snapProjMap) {
      if (!liveProjMap.has(id)) {
        projectDiff++;
        details.push(`Project ${id} exists in data/portfolio.json but was removed from live DB`);
      }
    }

    // 2. Users comparison
    let userDiff = 0;
    const snapUserMap = new Map(snapshotUsers.map((u) => [u.id, u]));
    const liveUserMap = new Map(liveUsers.map((u) => [u.seed_id || `usr-${u.id}`, u]));

    for (const [uid, live] of liveUserMap) {
      const snap = snapUserMap.get(uid);
      if (!snap) {
        userDiff++;
        details.push(`User ${uid} (${live.name}) is present in live DB but missing in data/users.json`);
      } else if (snap.role !== live.role || snap.active !== live.active) {
        userDiff++;
        details.push(`User ${uid} differs in live DB vs snapshot (role or active status modified)`);
      }
    }
    for (const [id] of snapUserMap) {
      if (!liveUserMap.has(id)) {
        userDiff++;
        details.push(`User ${id} exists in data/users.json but was removed from live DB`);
      }
    }

    const isDiverged = projectDiff > 0 || userDiff > 0;
    return {
      isDiverged,
      projectDiff,
      userDiff,
      details
    };
  } catch (err) {
    console.warn('[divergence] check failed', err);
    return {
      isDiverged: false,
      projectDiff: 0,
      userDiff: 0,
      details: []
    };
  }
}
