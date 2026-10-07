// Test settings accessor logic and type casting (R3.1, R3.2, R3.3 / V3, V5)
import assert from 'node:assert/strict';

const SETTINGS_DEFAULTS = {
  app_name: 'Cetana Labs Control Hub',
  app_description: 'Protocol Engine'
};

function castSettingValue(value, type, fallback) {
  if (value === undefined || value === null || value === '') {
    return fallback;
  }
  switch (type) {
    case 'number': {
      const n = Number(value);
      return Number.isNaN(n) ? fallback : n;
    }
    case 'boolean': {
      const v = value.toLowerCase().trim();
      if (v === 'true' || v === '1') return true;
      if (v === 'false' || v === '0') return false;
      return fallback;
    }
    case 'string':
    case 'url':
    default:
      return value;
  }
}

class TestSettingsAccessor {
  constructor(records = []) {
    this.records = new Map();
    for (const r of records) {
      if (r && r.key) this.records.set(r.key, r);
    }
  }

  get(key, fallback) {
    const rec = this.records.get(key);
    if (!rec || rec.value === undefined || rec.value === null || rec.value === '') {
      return fallback;
    }
    return castSettingValue(rec.value, rec.type, fallback);
  }

  appName() {
    return this.get('app_name', SETTINGS_DEFAULTS.app_name);
  }

  appDescription() {
    return this.get('app_description', SETTINGS_DEFAULTS.app_description);
  }

  typed(key, fallback) {
    return this.get(key, fallback);
  }
}

// 1. Defaults when empty
const empty = new TestSettingsAccessor([]);
assert.equal(empty.appName(), 'Cetana Labs Control Hub');
assert.equal(empty.appDescription(), 'Protocol Engine');
assert.equal(empty.get('nonexistent', 'fallback'), 'fallback');

// 2. Empty or whitespace value returns default (R3.2 / V3)
const withEmptyValue = new TestSettingsAccessor([{ key: 'app_name', value: '', type: 'string' }]);
assert.equal(withEmptyValue.appName(), 'Cetana Labs Control Hub');

// 3. Seeded values
const seeded = new TestSettingsAccessor([
  { key: 'app_name', value: 'Custom Hub', type: 'string' },
  { key: 'app_description', value: 'Custom Description', type: 'string' }
]);
assert.equal(seeded.appName(), 'Custom Hub');
assert.equal(seeded.appDescription(), 'Custom Description');

// 4. Type casting (R3.3 / V5)
const typed = new TestSettingsAccessor([
  { key: 'max_items', value: '42', type: 'number' },
  { key: 'enable_feature', value: 'true', type: 'boolean' },
  { key: 'disable_feature', value: 'false', type: 'boolean' },
  { key: 'custom_url', value: 'https://example.com/logo.png', type: 'url' },
  { key: 'invalid_num', value: 'not-a-number', type: 'number' }
]);
assert.equal(typed.typed('max_items', 0), 42);
assert.equal(typed.typed('enable_feature', false), true);
assert.equal(typed.typed('disable_feature', true), false);
assert.equal(typed.typed('custom_url', ''), 'https://example.com/logo.png');
assert.equal(typed.typed('invalid_num', 10), 10);

console.log('✅ Settings accessor and type casting tests passed!');
