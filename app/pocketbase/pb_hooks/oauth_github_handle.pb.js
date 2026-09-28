/// <reference path="../pb_data/types.d.ts" />
//
// M3–M4 (RFC-LAB-000-008 §6): populate `github_handle` on GitHub OAuth sign-in.
//
// PocketBase creates a SEPARATE auth record per OAuth identity and does not fill custom
// fields (mappedFields only covers id/name/username/avatarURL). The app resolves project
// ownership by `github_handle` — and the projects.updateRule matches owner.github_handle
// against @request.auth.github_handle — so a signed-in owner MUST carry their GitHub login
// in `github_handle` for the owner-write path to work. This hook copies the GitHub login
// (oAuth2User.username, falling back to rawUser.login) into the record's github_handle
// when it's empty, on every OAuth2 auth. Idempotent; never overwrites an existing value.
onRecordAuthWithOAuth2Request((e) => {
  try {
    const rec = e.record;
    if (rec && e.oAuth2User) {
      const login =
        e.oAuth2User.username ||
        (e.oAuth2User.rawUser && e.oAuth2User.rawUser.login) ||
        '';
      if (login && !rec.get('github_handle')) {
        rec.set('github_handle', String(login));
        e.app.save(rec);
      }
    }
  } catch (err) {
    // Non-fatal: never block sign-in if handle population fails.
    console.log('[oauth_github_handle] could not set github_handle:', err);
  }
  e.next();
}, 'users');
