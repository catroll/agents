# `forward_auth` upstream down → 502; `handle_response` never runs

**Signal.** An optional-auth block works while the auth service answers:

```caddy
forward_auth 127.0.0.1:3000 {
	uri /api/auth/caddy
	copy_headers Remote-User
	@no_session status 302 400 401 403
	handle_response @no_session {
		request_header -Remote-User
	}
}
```

Stop the auth process and the request gets `502 Bad Gateway` with an empty body;
the `handle_response` route never runs. The Caddy log line is:

```
msg="error handling handler error" error="... reverseproxy.statusError (reverseproxy.go:1272):
HTTP 502: dial tcp 127.0.0.1:3000: connect: connection refused"
```

**Cause.** `handle_response` handles *responses* from the upstream. A dial/TLS
failure is converted into a 502 by `reverseproxy.statusError` outside that path,
so a status matcher in `handle_response` never sees it. `caddy validate` accepts
the config either way.

**Fix.** Catch it at the site level, scoped by path so one upstream outage does
not reroute unrelated routes (Caddy 2.6.2):

```caddy
handle_errors {
	@home_auth_down {
		path /home/*
		expression {http.error.status_code} == 502
	}
	handle @home_auth_down {
		reverse_proxy 127.0.0.1:8080
	}
}
```

A 502 *response* from the app itself is not an error and is not touched, so this
fallback only fires for connection failures (auth or app).

**Security note.** If the fallback proxies without auth, delete client-supplied
`Remote-*` headers in the route *before* `forward_auth`:

```caddy
route {
	request_header -Remote-User
	request_header -Remote-Name
	forward_auth ...
	reverse_proxy ...
}
```

Otherwise the fail-open path hands a forged `Remote-User` to an app that trusts
the loopback + header identity. Test that case explicitly: auth down + forged
header must still produce the app's 401/403, not 200.

**Verification pattern.** Local Caddy with `tls internal` on a high port, a stub
auth that returns 401/200 + `Remote-User`, and a stub upstream that echoes the
header; then: anonymous (no session) → upstream reached with no identity;
session → identity copied; kill the auth stub → upstream still reached
anonymously; app-side privileged paths → 401/403. Use
`https://localhost:18445` (not `https://:18445`) with `tls internal`, otherwise
there is no hostname to issue a certificate for.
