# ClawX market CLI answers "我暂时没有相关数据" — the history lives in the backup endpoint

Signal: `clawx-market-query/scripts/cli.py --query "伦敦金最近一年价格走势"` returns
`{"code": "00000000", "message": "success", ..., "answers": "我暂时没有相关数据"}`.
The main `jask/query` endpoint is a snapshot/QA endpoint; it does not serve time
series, and a successful code with empty text is not a network failure.

The time-series path is the **backup** CLI, which wraps `youqian/query` and
parses the phrasing into a table:

```sh
python3 ~/.dsh/skills/clawx-market-query/scripts/cli_backup.py \
  --query "现货黄金近一年现货价格" --page 1 --limit 1000
```

That returns 241 rows of `时间 / 指标 / 指标值 / 单位` (macro `S004242373`,
现货价:黄金, 元/克) covering 2025-11-17 → 2026-11-13 — exactly the 1-year
daily series. `"沪金近一年收盘价"` returns 8 rows (one per contract) where each
row carries 241 `收盘价[YYYYMMDD]` columns (AU2612.SHF). `"纽约金近一年收盘价"`
returns 711 long rows over 8 COMEX contracts (need front-month selection).

Pitfalls found:

- The 品种简称 filter is an equality match and silently substitutes: `"上海金"`
  and `"黄金"` both resolved to 纽约金 / 沪金, `"伦敦金"` resolved to 0 rows
  (`品种简称等于伦敦金 (0)`). Read `chunks_info` and the first row before
  trusting the answer; never assume the named product was honoured.
- Query nouns that select the right shape: `近一年收盘价` (per-contract) versus
  `近一年现货价格` (macro daily rows). `"银行积存金近一年价格"` matched an
  unrelated macro series (M0, 年 周期) — check `周期` and `单位`.
- Store the result under the run directory and plot from the saved CSV; the API
  is not stable enough to refetch while formatting.

Paths used: `/tmp/au_spot.json` (raw), then
`work/2026/Q4/11/20261116-gold-price-trend/{series.csv,series.json,gold-1y-trend.png}`.
Yearly view: 957.63 (2025-11-17) → 840.03 (2026-11-13), -12.28%; high 1243.40
(2026-01-29), low 836.72 (2026-11-02), -32.7% from the high.

Negative results worth not repeating:

- `https://stooq.com/q/d/l/?s=xauusd&i=d` returns HTTP 200 with a 796-byte
  JavaScript PoW challenge page, not CSV.
- `https://query1.finance.yahoo.com/v8/finance/chart/GC=F?range=1y&interval=1d`
  through `source ~/.proxyrc` returns HTTP 429 `Edge: Too Many Requests`.
