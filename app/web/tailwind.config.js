/**
 * Tailwind token map — mirrors the Nexus Pulse --np-* CSS variables
 * (docs/DESIGN.md + docs/design-system-lab000.md). CSS custom properties remain
 * the runtime source of truth; these utilities are conveniences.
 * @type {import('tailwindcss').Config}
 */
export default {
  darkMode: ['selector', '[data-theme="dark"]'],
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        canvas: 'var(--np-bg)',
        panel: 'var(--np-bg-elevated)',
        subtle: 'var(--np-bg-subtle)',
        ink: 'var(--np-text)',
        'ink-secondary': 'var(--np-text-secondary)',
        muted: 'var(--np-text-muted)',
        line: 'var(--np-border)',
        'line-strong': 'var(--np-border-strong)',
        brand: 'var(--np-accent)',
        'brand-hover': 'var(--np-accent-hover)',
        'brand-ink': 'var(--np-accent-ink)',
        'brand-soft': 'var(--np-accent-soft)',
        'brand-line': 'var(--np-accent-line)',
        'brand-mark': 'var(--np-accent-mark)',
        'on-accent': 'var(--np-on-accent)',
        live: 'var(--live)',
        'live-soft': 'var(--live-soft)',
        warn: 'var(--warn)',
        'warn-ink': 'var(--warn-ink)',
        'warn-soft': 'var(--warn-soft)',
        critical: 'var(--critical)',
        'critical-soft': 'var(--critical-soft)',
        info: 'var(--info)',
        'info-soft': 'var(--info-soft)'
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace']
      },
      maxWidth: {
        content: '1500px'
      },
      borderRadius: {
        control: '8px',
        card: '13px'
      }
    }
  },
  plugins: []
};
