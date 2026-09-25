// Theme store (Svelte 5 runes). Dark-first per docs/DESIGN.md, with System/Light/Dark.
import { browser } from '$app/environment';

export type Theme = 'system' | 'light' | 'dark';

const KEY = 'cetana-theme';

function initial(): Theme {
  if (!browser) return 'dark';
  const saved = localStorage.getItem(KEY);
  return saved === 'light' || saved === 'dark' || saved === 'system' ? saved : 'system';
}

class ThemeState {
  choice = $state<Theme>(initial());

  resolved = $derived.by<'light' | 'dark'>(() => {
    if (this.choice !== 'system') return this.choice;
    if (!browser) return 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  set(theme: Theme) {
    this.choice = theme;
    if (browser) {
      localStorage.setItem(KEY, theme);
      document.documentElement.setAttribute('data-theme', this.resolved);
    }
  }

  apply() {
    if (browser) document.documentElement.setAttribute('data-theme', this.resolved);
  }
}

export const theme = new ThemeState();
