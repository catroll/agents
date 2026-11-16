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

## Wider damage: a missing 301 is a lost URL, not a missing header

A stale vhost loses every rule added to the repo since it was installed, not only
the one you were chasing. On markjour.com the same drift dropped the legacy-URL
redirect: 2026-08-07 the new host got a 1,635-byte stub with no
`location ~ "^/article/(\d{4})(\d{2})(\d{2})-(.+)\.html$"`, so every
`/article/YYYYMMDD-slug.html` — the URL Google had indexed for each article for
years — answered 404 instead of 301, for 90 days, until 2026-11-05.

```bash
# live config age vs repo config age
ssh host 'ls -la --time-style=full-iso /etc/nginx/sites-available/<site>.conf*'
git log --format='%h %ad %s' --date=short -- nginx.conf
# the stub that was live during the window
grep -c 'location' host:/etc/nginx/sites-available/<site>.conf.bak-*
```

The deploy script keeps a timestamped backup before each install, so the drift
window is bounded exactly by `markjour.conf.bak-<timestamp>`'s own mtime — no log
retention needed.

Confirm from the access log that the missing rule is a 404, and from the traffic
that the old URLs still matter:

```bash
zcat -f www.<site>_access.log* | awk '$9==404 && $7 ~ /^\/article\/[0-9]{8}-/' \
  | awk '{print $4}' | cut -c2-12 | sort | uniq -c        # stops on the fix date
zcat -f www.<site>_access.log* | awk '$9==301 && $7 ~ /^\/article\/[0-9]{8}-/' \
  | awk '{print $7}' | sort -u | wc -l                    # 1469 still crawling
```

**Check.** After any vhost install, assert one legacy URL end-to-end
(`curl -sSI …/article/20150212-python-rabbitmq.html` → 301 → target 200), not just
the header the change was about. A 301 whose target was renamed or unpublished is
still a dead end: count how many redirect targets 404 and give those slugs an
explicit redirect.
