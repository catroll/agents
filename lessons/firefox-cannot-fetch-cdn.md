# Headless Firefox in this environment cannot fetch external CDNs — vendor local assets

**Signal.** A page loaded over `127.0.0.1` has local assets but every
`https://cdn.*` resource fails: resource timing shows `responseStatus: 0` and
`transferSize: 0`, page `fetch()` rejects with
`TypeError: NetworkError when attempting to fetch resource`, and an SRI-enabled
`<script>` reports:

```
None of the “sha384” hashes in the integrity attribute match ... The computed hash is “OLBgp1GsljhM2TJ+sbHjaiH9txEUvgdDTAzHv2P24donTt6/529l+9Ua0vFImLlb”.
```

The decisive tell: the **same** "computed hash" appears for two unrelated files
(e.g. easymde and bootstrap.bundle). Two files cannot share a hash — the response
is an interception/error body, not the asset, so the integrity value is not the
bug. Do not "fix" SRI, and do not conclude the library or typings are wrong.

**Check.** In the browser context, not with `curl` (curl works; this is
browser/network policy):

```js
performance.getEntriesByType('resource')
  .map(e => ({n: e.name, status: e.responseStatus, bytes: e.transferSize}));
await fetch(url, {mode: 'cors'}).then(r => r.status).catch(e => String(e));
```

`responseStatus: 0` + `NetworkError` means the asset never reached the page.
Note the existing page may look "styled enough" to hide it: an admin whose
Bootstrap CSS is CDN-hosted will render unstyled in this browser, so a layout
or colour finding measured here is about missing CSS, not about your change.

**Fix.** For locally served tools (admin panels, internal dashboards) vendor the
runtime asset under the app's own static directory and reference it with a local
URL; then there is no SRI, no CDN outage, no runtime network request, and the
page is verifiable and usable offline. Keep the upstream `LICENSE` beside it and
record the version. This is the second reason vendoring beats a pinned CDN URL
for a local tool; the first is that the tool must work when the network doesn't.

