<script lang="ts">
  // Auth-reactive control (RFC-LAB-000-008 M2, R4). Anon → "Sign in with GitHub";
  // authed → identity (name/avatar) + "Sign out". Never gates the public dashboard.
  import { auth } from '$lib/auth.svelte';

  let busy = $state(false);

  async function signIn() {
    busy = true;
    try {
      await auth.signInWithGitHub();
    } catch (err) {
      // OAuth popup closed/failed — non-fatal; stay anonymous.
      console.warn('[auth] GitHub sign-in did not complete.', err);
    } finally {
      busy = false;
    }
  }
</script>

{#if auth.isAuthenticated}
  <div class="inline-flex items-center gap-2">
    {#if auth.identity?.avatarUrl}
      <img
        src={auth.identity.avatarUrl}
        alt=""
        class="h-6 w-6 rounded-full border border-line"
        aria-hidden="true"
      />
    {/if}
    <span class="text-xs font-semibold text-ink">
      {auth.identity?.name}
      {#if auth.isUnlinked}
        <span
          class="ml-1 rounded-[6px] bg-panel px-1.5 py-0.5 text-[10px] font-medium text-muted"
          title="Signed in, but this GitHub account isn't linked to a portfolio project."
        >
          unlinked
        </span>
      {/if}
    </span>
    <button
      type="button"
      class="rounded-control border border-line bg-panel px-2.5 py-1.5 text-xs font-semibold text-muted transition-colors hover:text-ink"
      onclick={() => auth.signOut()}
    >
      Sign out
    </button>
  </div>
{:else}
  <button
    type="button"
    class="inline-flex items-center gap-1.5 rounded-control bg-brand-soft px-3 py-1.5 text-xs font-semibold text-brand-ink transition-colors hover:brightness-110 disabled:opacity-60"
    onclick={signIn}
    disabled={busy}
  >
    <span aria-hidden="true">🔑</span>
    <span>{busy ? 'Signing in…' : 'Sign in with GitHub'}</span>
  </button>
{/if}
