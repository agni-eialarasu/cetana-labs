// App-level settings accessor façade (RFC-LAB-000-013 / BK-012).
//
// A typed TypeScript façade over the PocketBase `settings` key/value collection,
// mirroring the data.ts read pattern. Loads the collection once (eager load, OQ-2),
// and exposes typed getters with hardcoded defaults. Absent or empty keys return
// the default value (R3.2 — no crash, no blank). Values are cast per the `type` column
// (R3.3); callers never touch raw rows.

import { base } from '$app/paths';
import { pb } from './pb';
import type { SettingRecord, SettingType } from './types';

const PB_SOURCE = (import.meta.env.VITE_PB_SOURCE ?? 'auto').toLowerCase();

export const SETTINGS_DEFAULTS = {
  app_name: 'Cetana Labs Control Hub',
  app_description: 'Protocol Engine',
  logo_icon_url: '',
  logo_small_url: '',
  logo_medium_url: ''
} as const;

export function castSettingValue<T = unknown>(
  value: string | undefined | null,
  type: SettingType,
  fallback: T
): T {
  if (value === undefined || value === null || value === '') {
    return fallback;
  }
  switch (type) {
    case 'number': {
      const n = Number(value);
      return (Number.isNaN(n) ? fallback : n) as T;
    }
    case 'boolean': {
      const v = value.toLowerCase().trim();
      if (v === 'true' || v === '1') return true as T;
      if (v === 'false' || v === '0') return false as T;
      return fallback;
    }
    case 'string':
    case 'url':
    default:
      return value as unknown as T;
  }
}

export class SettingsAccessor {
  private records = $state<Map<string, SettingRecord>>(new Map());

  constructor(initialRecords?: SettingRecord[]) {
    if (initialRecords) {
      this.populate(initialRecords);
    }
  }

  populate(records: SettingRecord[]) {
    const next = new Map<string, SettingRecord>();
    for (const r of records) {
      if (r && r.key) {
        next.set(r.key, r);
      }
    }
    this.records = next;
  }

  get<T = string>(key: string, fallback: T): T {
    const rec = this.records.get(key);
    if (!rec || rec.value === undefined || rec.value === null || rec.value === '') {
      return fallback;
    }
    return castSettingValue(rec.value, rec.type, fallback);
  }

  // Typed getters with hardcoded defaults (R3.1, R3.2)
  appName(): string {
    return this.get<string>('app_name', SETTINGS_DEFAULTS.app_name);
  }

  appDescription(): string {
    return this.get<string>('app_description', SETTINGS_DEFAULTS.app_description);
  }

  // Typed logo getters (BK-013 / R2.1)
  logoIconUrl(): string {
    return this.get<string>('logo_icon_url', SETTINGS_DEFAULTS.logo_icon_url);
  }

  logoSmallUrl(): string {
    return this.get<string>('logo_small_url', SETTINGS_DEFAULTS.logo_small_url);
  }

  logoMediumUrl(): string {
    return this.get<string>('logo_medium_url', SETTINGS_DEFAULTS.logo_medium_url);
  }

  // Typed getter for custom/future settings without exposing raw rows (R3.3, V5)
  typed<T = unknown>(key: string, fallback: T): T {
    return this.get<T>(key, fallback);
  }
}

export const settings = new SettingsAccessor();

async function loadFromSnapshot(fetchFn: typeof fetch): Promise<SettingRecord[]> {
  const res = await fetchFn(`${base}/data/settings.json`);
  if (!res.ok) throw new Error(`Failed to load settings.json: ${res.status}`);
  return (await res.json()) as SettingRecord[];
}

async function loadFromPocketBase(): Promise<SettingRecord[]> {
  const records = await pb.collection('settings').getFullList();
  return records.map((r) => ({
    key: r.key as string,
    value: (r.value as string) ?? '',
    type: (r.type as SettingType) ?? 'string',
    group: (r.group as string) || null
  }));
}

export async function loadSettings(fetchFn: typeof fetch = fetch): Promise<SettingsAccessor> {
  if (PB_SOURCE === 'snapshot') {
    try {
      const list = await loadFromSnapshot(fetchFn);
      settings.populate(list);
    } catch (err) {
      console.warn('[settings] Snapshot load failed — using defaults.', err);
    }
    return settings;
  }

  try {
    const list = await loadFromPocketBase();
    if (list.length > 0) {
      settings.populate(list);
      return settings;
    }
    if (PB_SOURCE === 'pocketbase') {
      settings.populate(list);
      return settings;
    }
    console.warn('[settings] PocketBase returned no settings — falling back to snapshot.');
  } catch (err) {
    if (PB_SOURCE === 'pocketbase') throw err;
    console.warn('[settings] PocketBase unreachable — falling back to snapshot.', err);
  }

  try {
    const list = await loadFromSnapshot(fetchFn);
    settings.populate(list);
  } catch (err) {
    console.warn('[settings] Snapshot load failed — using defaults.', err);
  }

  return settings;
}
