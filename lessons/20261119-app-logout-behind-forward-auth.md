# App logout behind forward_auth does nothing — the edge re-authenticates the next request

Symptom: clicking "sign out" in an app protected by Caddy `forward_auth` shows a
"local login is disabled" page (or the login page), and revisiting the app finds
the user still signed in. The app's session cookie was cleared, but nothing
changed.

Cause: the app session is no longer the credential. Every request is
re-identified from the identity headers `forward_auth` returns (tinyauth's
`Remote-User`), so clearing the app session only means "no local session" — the
next request is authenticated again from the edge. Redirecting to the app's own
`/login` is wrong twice: local login is closed, and even if it were open the
edge would log the user straight back in.

Fix: hand sign-out to the identity provider. The app clears its own session and
redirects to the provider's logout page/endpoint; clearing the SSO session is
the only thing that actually signs the user out.

One constraint to expect: tinyauth's logout is `POST /api/user/logout`, and a
cross-site form POST does not carry a `SameSite=Lax` session cookie. So the app
cannot fire it directly from its own origin — redirect to the portal's own
`/logout` page, which posts from the same origin (a confirmation click). Do not
try to "fix" the no-op by re-rendering a login form; find whose cookie actually
authenticates the request and end that session at its owner.

Checklist when adding edge auth to an app: audit its logout route and its
`/login` landing, not only its auth middleware. Both should point at the
provider once local login is disabled.
