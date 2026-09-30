<script lang="ts">
  // OAuth callback handler (BK-018 redirect flow, R1.2/R1.4). On mount, read `code`+`state`
  // from the query, hand them to auth.completeOAuthCallback() (which verifies the CSRF state
  // and exchanges the code — no popup, no /api/realtime), then land back in the app. On
  // failure (bad/absent state, exchange error) show a clear message + a retry link.
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { auth } from '$lib/auth.svelte';

  let error = $state<string | null>(null);

  onMount(async () => {
    const code = page.url.searchParams.get('code') ?? '';
    const state = page.url.searchParams.get('state') ?? '';
    try {
      await auth.completeOAuthCallback(code, state);
      // Success — replace history so the callback URL (with code/state) isn't in the
      // back-stack, then land on the dashboard.
      await goto('/', { replaceState: true });
    } catch (err) {
      error = err instanceof Error ? err.message : 'Sign-in failed. Please try again.';
      console.warn('[auth] OAuth callback did not complete.', err);
    }
  });
</script>

<section class="mx-auto flex min-h-[40vh] max-w-md flex-col items-center justify-center gap-3 text-center">
  {#if error}
    <p class="text-sm font-semibold text-ink">Sign-in didn’t complete</p>
    <p class="text-xs text-muted">{error}</p>
    <a
      href="/"
      class="rounded-control bg-brand-soft px-3 py-1.5 text-xs font-semibold text-brand-ink transition-colors hover:brightness-110"
    >
      Back to dashboard
    </a>
  {:else}
    <p class="text-sm font-semibold text-ink">Signing you in…</p>
    <p class="text-xs text-muted">Completing GitHub sign-in.</p>
  {/if}
</section>
