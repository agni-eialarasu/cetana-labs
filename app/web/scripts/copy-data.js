// Copies the repo's data/ JSON snapshots into static/data/ so the static SPA can
// fetch them at runtime (RFC-LAB-000-005 §4). Runs before dev and build.
import { mkdirSync, copyFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const repoData = resolve(here, '../../../data');
const dest = resolve(here, '../static/data');

const files = ['users.json', 'portfolio.json', 'status.json'];

mkdirSync(dest, { recursive: true });
let copied = 0;
for (const f of files) {
  const src = resolve(repoData, f);
  if (existsSync(src)) {
    copyFileSync(src, resolve(dest, f));
    copied++;
  } else {
    console.warn(`[copy-data] missing ${src}`);
  }
}
console.log(`[copy-data] copied ${copied}/${files.length} data files into static/data/`);
