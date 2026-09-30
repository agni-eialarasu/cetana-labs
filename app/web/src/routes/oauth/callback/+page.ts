// OAuth redirect callback route (BK-018 / RFC-011 §4.5). Client-side only and NOT under
// the (member) group — it must be reachable while still anonymous, mid sign-in flow.
// Not prerendered: it only ever runs in the browser on return from GitHub.
export const ssr = false;
export const prerender = false;
