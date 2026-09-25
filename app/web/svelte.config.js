import adapterStatic from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    // Static SPA (RFC-LAB-000-005 §2): build to a static bundle for GitHub Pages
    // / PocketBase pb_public/. SPA fallback so client-side routing works.
    adapter: adapterStatic({
      pages: 'build',
      assets: 'build',
      fallback: 'index.html',
      precompress: false,
      strict: true
    }),
    // Served under /cetana-labs/ on GitHub Pages (project pages); overrideable.
    paths: {
      base: process.env.BASE_PATH ?? ''
    }
  }
};

export default config;
