# A vhost rule in the repo is not a live header

**Signal.** A sidebar fed by `/meta.json` stops updating while the article pages
stay fresh; the repo's `nginx.conf` has the `no-cache` rule and the docs say so,
yet the response carries no header:

```bash
curl -sD- -o /dev/null https://host/meta.json | grep -i cache-control   # nothing
```

**Cause.** The vhost on the server was four months old; three blocks added to
the repo file since (the cache rule among them) had never been installed,
because the publish job only rsyncs the generated site. Without an explicit
policy the browser guesses freshness from `Last-Modified` (~10% of the file's
age), so the one JSON behind every non-HTML widget keeps a cached copy for
hours. The access log settles it: non-bot HTML views against `/meta.json`
requests and the 200/304 split — 5,699 vs 550, 549 of them unconditional 200s.

**Check.** Verify the response, not the file: stage with a timestamped backup,
`nginx -t`, restore on failure, reload, then assert the observable header. A
reload is graceful and returns before the old workers drain, so a probe started
right after it can still hit the previous config — retry instead of reporting a
false failure. A reader holding the old copy needs one hard reload; prefer a
cache-buster in the caller when a widget must never lag.

