# tinyauth rejects localhost/IP as APPURL, and its cookie name has a suffix

## Symptom

A temporary tinyauth instance failed to start with:

```text
failed to bootstrap app: failed to get cookie domain: invalid app url,
must be in format subdomain.domain.tld or domain.tld
```

`TINYAUTH_APPURL=http://localhost:3001` was rejected.

A successful login then showed the session cookie as
`tinyauth-session-095d202d`, not `tinyauth`.

## Fix

- Use a `domain.tld` that resolves to loopback for local tests, e.g.
  `TINYAUTH_APPURL=http://lvh.me:3001`; `lvh.me` resolves to `127.0.0.1`.
  With subdomains enabled the cookie domain becomes `.lvh.me`.
- Do not hardcode the cookie name. Read the whole `requests` cookie jar and
  persist every cookie; the suffix may vary by tinyauth configuration.

## Check

`curl http://lvh.me:3001/api/healthz` returns 200, and a login + TOTP flow
leaves a `tinyauth-session-<suffix>` cookie that `/api/context/user` accepts.
