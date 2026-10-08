/// <reference path="../pb_data/types.d.ts" />
//
// RFC-016 Phase 1 (BK-034): GitHub-Handle Identity & Single-User Enforcement.
//
// 1. On GitHub OAuth2 sign-in, if an existing users record matches github_handle
//    (case-insensitively), bind the OAuth session to that existing record (enriching it)
//    rather than creating a second duplicate row (R2.1).
// 2. If no matching record exists, populate createData.github_handle from the GitHub identity
//    so the newly created record is keyed by handle (R2.2, R2.3).
// 3. If an existing linked record has no github_handle, populate it (R2.3).
onRecordAuthWithOAuth2Request((e) => {
  try {
    const oAuth2User = e.oAuth2User;
    const login = (
      (oAuth2User && oAuth2User.username) ||
      (oAuth2User && oAuth2User.rawUser && oAuth2User.rawUser.login) ||
      ''
    ).toString().trim();

    if (!login) {
      e.next();
      return;
    }

    if (!e.record) {
      // No externalAuth link yet. Check if an existing record has this github_handle (case-insensitive).
      let existing = null;
      try {
        existing = e.app.findFirstRecordByFilter('users', 'github_handle = {:handle}', { handle: login });
      } catch (_) {}

      if (!existing) {
        try {
          const candidates = e.app.findRecordsByFilter('users', 'github_handle ~ {:handle}', '', 10, 0, { handle: login });
          for (const c of candidates) {
            if (c && String(c.get('github_handle')).toLowerCase() === login.toLowerCase()) {
              existing = c;
              break;
            }
          }
        } catch (_) {}
      }

      if (existing) {
        // R2.1: Bind OAuth session to the existing record
        e.record = existing;
      } else {
        // R2.2 & R2.3: New record creation path; ensure createData is keyed by handle
        if (e.createData) {
          e.createData['github_handle'] = login;
        }
      }
    }

    // Enrich the record (either pre-existing, bound above, or previously linked)
    const rec = e.record;
    if (rec) {
      let needsSave = false;
      if (!rec.get('github_handle')) {
        rec.set('github_handle', login);
        needsSave = true;
      }
      if (!rec.get('name')) {
        const ghName = (oAuth2User && oAuth2User.name) ||
          (oAuth2User && oAuth2User.rawUser && oAuth2User.rawUser.name) ||
          login;
        if (ghName) {
          rec.set('name', ghName);
          needsSave = true;
        }
      }
      if (needsSave) {
        e.app.save(rec);
      }
    }
  } catch (err) {
    console.log('[oauth_github_handle] error during OAuth processing:', err);
  }
  e.next();
}, 'users');
