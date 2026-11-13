# A prefix proxy location can swallow an SPA's routes, and `auto_redirect` can loop

**Signal.** A deep link (`https://token.shanedit.com/dashboard/overview`) renders a
bare placeholder page — 104 bytes saying `frontend is served by nginx` — while
clicking around inside the running app works and `/` is fine. The app is a history
routing SPA whose `basePath` is `/dashboard`, so the URL is a legitimate page, not an
API path.

**Cause.** `location /dashboard/ { proxy_pass ... }` had been added for the two
OpenAI billing-compat endpoints (`/dashboard/billing/subscription|usage`). A prefix
location is all-or-nothing: every refresh under `/dashboard` reached the Go backend,
which has no such route, so its `NoRoute` handler answered with the placeholder index
page **and HTTP 200**. In-app navigation is `pushState` and never touches nginx,
which is why only refreshes, direct opens and shared links showed it.

**Check.** Compare a deep link against the real shell, then ask the config who owns
the prefix:

```sh
curl -s -o /dev/null -w '%{http_code} %{size_download}\n' https://host/dashboard/overview  # 200 104  -> placeholder
curl -s -o /dev/null -w '%{http_code} %{size_download}\n' https://host/index.html           # 200 1683 -> real shell
nginx -T | grep -n 'location.*dashboard'
grep -rn 'GET("' /opt/app/router/*.go    # what the backend really serves
```

The bundle names the routes it owns: `grep -o 'path:"/[^"]*"' static/js/index.*.js | sort -u`.

**Fix.** Exact matches for the endpoints that are actually API; everything else falls
through `try_files $uri $uri/ /index.html`.

**Second failure mode in the same config, worth recognising separately.** A prefix
location ending in `/` that contains `proxy_pass` makes nginx redirect `/x` → `/x/`
(`auto_redirect`); if the upstream also canonicalises the slash (gin's
`RedirectTrailingSlash` answers `/x/` with `301 -> /x`), the two bounce forever and
`curl -L` dies with `Maximum (50) redirects followed`. Both directions disappear when
the prefix location is removed — never "fix" it by adding `location = /dashboard`,
which just pages the loop's first hop.

**Lesson for the smoke test.** A routing regression that only shows on refresh is
invisible to a `/`-only probe. Request one deep link the SPA owns and assert a shell
marker (`id="root"`), not the status code — the wrong answer here is 200 with the
right content type.

