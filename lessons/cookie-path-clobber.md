# A cookie's `Path` is a routing rule, and a "please log in" flash overwrites the session

**Signal.** A panel mounted at `/app` asks for a password on every visit even
though a session already exists: `/app/` keeps working in the tab that is logged
in, but opening the bare `http://host:port/` shows the login form — and
afterwards `/app/` is logged out too. The access log shows an unauthenticated
request to the app's own root immediately before each login.

**Cause.** The session cookie is written with `Path=/app`. A browser never sends
that cookie to `/`, so the root request was anonymous by construction — and
`login_required` answered with `flash('please log in')`, which is a session
**write**. Flask therefore returned, on the redirect,

```
Set-Cookie: session=eyJfZmxhc2hlcyI6...; Path=/app
```

whose payload is `{"_flashes":[...]}` — the same cookie name and path as the
real session, minus `user`. The browser replaced the authenticated cookie with
the anonymous one. The root URL did not just demand a login; it deleted the
session.

**Check.** Diff two headers: the `Set-Cookie` from a successful login and the
one from the unauthenticated request. Same name and path with different content
is a clobber, not an expiry and not a signature failure (a rotated secret would
fail to decode the *old* value instead). Server side reproduces with two curls
sharing one Cookie header; browser side shows as a single `storage.getCookies`
entry whose value no longer decodes to a user.

**Fix.** Scope the cookie to the origin (`Path=/`) and give it an app-specific
name so another app on the same host cannot collide, then set `SCRIPT_NAME` for
*every* request so pages rendered at the bare root still emit prefixed links.
The narrow path is the wider bug: it makes the app serve a page it can never
authenticate. A redirect from `/` to `/app/` also removes the bounce, but it
loops behind a proxy that strips the prefix — the cookie fix does not.

**Generalisable.** Authentication failures are usually read as "the session is
gone"; here the session was fine and a *different* request rewrote it. When a
login does not stick, compare the cookie the browser ends up with, not the one
the login response set.

