# ClawX skill calls hit a 50/day cap: `该skill今日调用额度已达上限(50次)`

Signal: `{"success": false, "code": "429", "message": "该skill今日调用额度已达上限(50次)"}`
returned with **HTTP 200** by `gold-analysis-hub` and, minutes later,
`clawx-market-query` — so the counter is per API key (shared across skill
codes), not per script. It does not recover until the next day; retrying is
useless.

Trigger: one afternoon of exploration for a 1-year gold series — roughly 10
`cli_backup.py` probes (variants for 现货黄金/沪金/纽约金), 2 `cli.py` main
calls, 4 gold-hub snapshots (price / opportunity / order-book / resonance /
bomb) and one `news-search` call. That is enough to exhaust a 50-call budget
when each probe is a separate call.

Consequences and procedure:

- Cache every result that matters (the 241-close series is at
  `work/2026/Q4/11/20261116-gold-price-trend/series.json`) and answer follow-up
  questions from the cache; the quota makes refetching expensive.
- Before a batch of probes, spend one call on the phrasing that is most likely
  correct; do not fan out five synonyms.
- A 429 body still has `success: false`; a caller that only checks the exit code
  sees success. Check `success` and `code`.
- When the quota is gone, report the price as of its timestamp rather than
  reusing an old value as if it were live. `realtime-quote` for CMBC-JCJ last
  answered `834.56 / -0.22%` at `2026-11-16 10:09:05`; the 20:41 retry was 429.
- Failure is not a network problem: do not retry through the proxy or a mirror.