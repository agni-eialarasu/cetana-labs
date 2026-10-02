// Validates that all allow-listed docs in src/lib/docs/registry.ts exist in docs/
// Build-time fail-loud per BK-024 R5.1.
import { existsSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const repoDocs = resolve(here, '../../../docs');
const registryFile = resolve(here, '../src/lib/docs/registry.ts');

const content = readFileSync(registryFile, 'utf8');
const lines = content.split('\n');
const allowListedSrcs = [];
for (const line of lines) {
  const trimmed = line.trim();
  if (trimmed.startsWith('//') || trimmed.startsWith('/*') || trimmed.startsWith('*')) continue;
  const match = trimmed.match(/src:\s*'([^']+)'/);
  if (match) {
    allowListedSrcs.push(match[1]);
  }
}

if (allowListedSrcs.length === 0) {
  console.error('[check-docs] No allow-listed docs found in registry.ts');
  process.exit(1);
}

for (const src of allowListedSrcs) {
  const fullPath = resolve(repoDocs, src);
  if (!existsSync(fullPath)) {
    console.error(
      `[check-docs] FATAL: Missing allow-listed doc: "${src}" (expected at ${fullPath}). Build failed loud per R5.1.`
    );
    process.exit(1);
  }
}

console.log(`[check-docs] verified ${allowListedSrcs.length} allow-listed docs exist in docs/`);
