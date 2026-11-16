# DeepSeek platform API: 429 "Request Blocked" is the WAF, not a bad token

Signal: a call to `https://platform.deepseek.com/api/v0/usage/by_api_key/*`
returns HTTP 429 whose body is an HTML page (`<!DOCTYPE html>`,
`Error - Request Blocked`, `Event ID: ...`), not JSON.

What it actually means: the HWWAF in front of the platform rate-limits per IP
(+ user agent). On 2026-11-16 five calls within about two minutes were enough to
get blocked, and the block lasted roughly 15 minutes; every request in that
window returned the same HTML page, including ones identical to earlier
successful calls.

The wrong conclusion is "the Bearer token expired". It did not: the same token
worked again after the pause, and an API-level rejection is answered with JSON
`{"code":..., "msg":...}`, not an HTML block page.

Checklist before changing credentials:

- Look at the body: HTML block page = WAF; JSON with `code` = API verdict.
- Re-run a request that worked before. If that also 429s, it is the rate limit,
  not the new parameter and not the token.
- Wait about 15 minutes. A 15-60 s backoff is usually too short.
- Cache the raw JSON response on disk and analyse from the cache; only refetch
  when the window changes. Useful shape:

```
GET /api/v0/usage/by_api_key/amount?start=<epoch>&end=<epoch>&tz=28800
Authorization: Bearer <token>
```

Bucket granularity is chosen by the server from the window length, not by a
parameter, and the response echoes it:

- `end - start <= 86400` -> `"bucket": 3600` (hourly, one bucket per hour);
- longer window -> `"bucket": 86400` (one bucket per day).

`bucket=` is not an accepted query parameter; adding it changes nothing about
the granularity (and at the time of writing coincided with a 429, which is why
this note originally blamed it — the rate limit is the proven cause, the
parameter theory is not).
