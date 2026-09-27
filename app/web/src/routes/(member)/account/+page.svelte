<script lang="ts">
  // Placeholder member-only page (RFC-LAB-000-008 M2, R5.2). Exists to make the
  // (member) route-guard pattern real and testable; M3/M4 will replace/extend it with
  // the owner status-edit view. Reachable only when authenticated (guard in +layout.ts).
  import { auth } from '$lib/auth.svelte';
</script>

<section class="mx-auto max-w-2xl px-4 py-10">
  <h1 class="text-lg font-semibold text-ink">Member area</h1>
  <p class="mt-2 text-sm text-muted">
    You're signed in as <strong class="text-ink">{auth.identity?.name}</strong>.
    {#if auth.isUnlinked}
      This GitHub account isn't linked to a portfolio project yet.
    {:else}
      Owner tools (status editing) arrive in M3–M4.
    {/if}
  </p>
  <a href="../" class="mt-4 inline-block text-xs font-semibold text-brand-ink hover:underline"
    >← Back to dashboard</a
  >
</section>
