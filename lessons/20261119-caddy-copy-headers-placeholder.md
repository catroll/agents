# `Remote-User` arrives as `{http.reverse_proxy.header.Remote-User}` — a non-empty check accepts the placeholder

Signal: an app behind Caddy 2.6.2 `forward_auth` authorizes a request even
though the auth response did not carry the identity header. Printing the
headers the upstream actually received shows:

    Remote-User: {http.reverse_proxy.header.Remote-User}

Cause: `copy_headers` sets the request field to that placeholder and resolves
it from the auth response afterwards. When the auth response does not contain
the field, the literal string stays on the request. An app-side check shaped
like `header == ""` sees a non-empty value and treats it as an authenticated
user.

Proved with a local rig: Caddy 2.6.2 on `:18443` with
`request_header -Remote-User` + `forward_auth` to a stub that sometimes returns
200 without the header, and the real app behind it. The client's forged
`Remote-User: admin` was removed, but the placeholder alone still granted
access — "the strip works" and "the app is closed" are different claims.

Check:

- In the app, reject values that still look like an unresolved placeholder
  (for example anything starting with `{`) before trusting the header, and
  test the "auth returns 2xx without the header" path, not only the
  missing-header-from-client path.
- In the proxy test, assert the exact header value that reaches the upstream.
  A test that only proves the forged value is gone passes while the
  placeholder is still there.
- Caddy 2.6.2 (2022) is the behaviour observed here; newer releases may resolve
  the placeholder to an empty string. Do not assume either way without the rig.

Command that exposed it:

```sh
curl -s -H 'Remote-User: admin' -H 'X-Test-Mode: strip' http://127.0.0.1:18443/
# upstream saw: {"Remote-User": "{http.reverse_proxy.header.Remote-User}"}
```
