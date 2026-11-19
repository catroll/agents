# The proxy sent `Remote-User`, the app still answered 401 — uvicorn rewrote `request.client` from `X-Forwarded-For`

Symptom: Caddy's `forward_auth` succeeds (tinyauth 200, upstream receives
`Remote-User: catroll` in Caddy's debug log), and the app still answers 401 for
that request. `curl` with the same header straight to the app's loopback port
returns 200.

Cause: the app is served by uvicorn with its default proxy-header handling
(`proxy_headers=True`, `forwarded_allow_ips=127.0.0.1`). Behind Caddy the
transport peer is loopback, so uvicorn replaces `scope["client"]` with the
`X-Forwarded-For` value — the browser's address. A trust check of the form
"accept `Remote-User` only from a loopback peer" then compares the *browser's*
IP against loopback and fails closed.

The tell is a contradiction between two logs: Caddy's debug roundtrip shows
`Remote-User` was sent to the upstream, while the app's access log shows the
request arriving from the public client address even though the app is bound to
127.0.0.1.

Fix, keeping the real client in logs and audit records:

- run uvicorn with `proxy_headers=False` (`--no-proxy-headers` in the CLI, and
  `proxy_headers=False` in a programmatic `uvicorn.Config`);
- add one ASGI middleware that records the pre-rewrite peer
  (`scope["...transport_client"] = scope["client"]`) and then delegates to
  uvicorn's own `ProxyHeadersMiddleware`, so `request.client` is still the real
  client for logs;
- trust checks read the stored transport peer; nothing else changes.

```python
class TransportAwareProxyHeaders:
    def __init__(self, app, trusted_hosts="127.0.0.1"):
        self.app = ProxyHeadersMiddleware(app, trusted_hosts=trusted_hosts)

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            scope.setdefault(KEY, scope.get("client"))
        await self.app(scope, receive, send)
```

Testing trap that hides the bug: an end-to-end test with browser, proxy and app
all on the same host sends `X-Forwarded-For: 127.0.0.1`, so the loopback check
passes and the test is a false positive. Force a non-loopback forwarded address
in the test proxy (`header_up X-Forwarded-For 2409:...`) — or assert on the
app's view of the client — before declaring the chain verified.

Check:

```sh
curl -s -o /dev/null -w '%{http_code}\n' -H 'X-Forwarded-For: 2409:8a4d::1' \
  -H 'Remote-User: <user>' http://127.0.0.1:<app-port>/<protected-path>
```

If that 401s while the same request without `X-Forwarded-For` returns 200, the
peer is being shadowed by the proxy-header middleware.
