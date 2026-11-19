# An app behind `forward_auth` still shows its own login page — the gate covers the page, not the app's API calls

Symptom: the browser is signed in to tinyauth (the gate returns 302→login→302 for
the document), the app's HTML loads, and then the app renders its own username /
password page — which is closed (`local_login: false`) and answers 403 on submit.

Cause: the edge gate was applied to the SPA document only. The SPA probes its own
API to learn whether the edge identified it (`GET /api/v1/auth/me` without a
bearer token), and those XHRs were routed straight to the upstream, so the
upstream never received the `Remote-User` header and answered 401. The app then
"correctly" showed its login page. The page was gated; the requests that decide
whether to show a login page were not.

The same misconfiguration is an impersonation hole, because the upstream trusts
`Remote-User` only from a loopback peer and the proxy connects from loopback:

```sh
curl -s -o /dev/null -w '%{http_code}\n' -H 'Remote-User: admin' \
  https://app.example.com/api/v1/auth/me        # 200 → anyone can be anyone
```

Fix, in the reverse proxy, for every path the app's SPA calls:

1. Strip client-supplied identity headers on every route that reaches an
   upstream; `forward_auth`'s `copy_headers` must be the only source.
2. Gate the API paths too, but let requests that carry their own credential
   (`Authorization`, `x-api-key`, `x-winnie-key`) skip the gate — machine
   clients cannot complete a browser login, and the app's own token auth still
   checks them.
3. Keep the order explicit with `route`, otherwise Caddy sorts the strip after
   `forward_auth` and deletes the header the gate just set. (Observed: adapted
   `request_header` handlers landed *after* the forward_auth route until the
   handler bodies were wrapped in `route {}`.)
4. Make the app probe the edge identity first and fall back to a stored token
   second; an expired local token must not hide a working edge login.

Caddy shape that worked (Caddy 2.6.2, which has no `or` matcher — multiple
`not` lines inside a named matcher are ANDed):

```caddyfile
(winnie_edge_identity) {
	request_header -Remote-User
}

@api_browser {
	not header Authorization *
	not header x-api-key *
	not header x-winnie-key *
}
@winnie_api path /api /api/*
handle @winnie_api {
	route {
		import winnie_edge_identity
		forward_auth @api_browser 127.0.0.1:3000 {
			uri /api/auth/caddy
			copy_headers Remote-User
		}
		reverse_proxy 127.0.0.1:8000
	}
}
```

Verification that proves the chain, not the halves: run a local Caddy on a high
port with `tls internal`, a stub auth server that returns `Remote-User: admin`,
and the real frontend build. Load it in a headless browser and assert the app's
authenticated shell renders with no login form. Then re-send the forged header
with and without a bogus bearer token; both must fail (the second one at the app,
which proves the strip ran).

Also check the account names match: an edge identity the app has no account for
is a 401, so the person sees the login page again. Either an explicit alias
(`auth.proxy_user_map: {catroll: admin}`) or the same username on both sides; do
not silently fall back to the app's default admin.
