# A synthetic ETag in If-None-Match defeats If-Modified-Since

## Symptom

An icon cache stored a locally computed ETag for providers that did not send
one, then revalidated with both:

```text
If-None-Match: "sha256-..."
If-Modified-Since: Wed, 29 Jul 2026 ...
```

A restart logged `fetched=3, not_modified=0`; the same URLs returned 304 to
`curl -H 'If-Modified-Since: ...'` when the If-None-Match header was absent.

## Cause

RFC 9110 gives `If-None-Match` precedence over `If-Modified-Since`. The provider
had no ETag, so the synthetic value never matched and the provider returned 200
instead of evaluating the otherwise valid Last-Modified validator.

## Fix

Store the provider ETag separately from the ETag used for local/browser
responses:

```json
{"etag": "\"sha256-...\"", "remote_etag": "", "last_modified": "..."}
```

Send `If-None-Match` only when `remote_etag` is non-empty; always send
`If-Modified-Since` when a provider Last-Modified exists. Re-test: restart sync
now reports `not_modified=21`.

## Check

After a cache warm-up and restart, assert the sync log reports
`not_modified > 0` (or inspect the provider response). If a provider has no ETag,
`remote_etag` must remain empty and the request must still carry
`If-Modified-Since`.
