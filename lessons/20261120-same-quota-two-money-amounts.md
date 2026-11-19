# Same quota reported as ¥12.72 and ¥92.87: read the serving system's display currency

Symptom: a local dashboard and the platform it reads show the same day's
consumption for the same user as ¥92.87 vs ¥12.72. The ratio equals a plausible
USD/CNY rate (7.30), not a data gap, and the wrong number looked plausible until
the two screens were compared.

Check, in this order:

1. Compare the underlying quantity, not the money. Both sides summed
   `quota = 6,389,311`; the request log (`type=2`) and the hourly `quota_data`
   table agree to the unit. So the money difference is a conversion one.
2. Fetch the serving system's own currency constants. New API publishes them at
   `GET /api/status` (`quota_per_unit`, `price`, `usd_exchange_rate`) and stores
   them in `options` (`Price`, `USDExchangeRate`, `general_setting.quota_display_type`).
   Here token: `price=1` (CNY-native, one yuan = 500,000 quota);
   hub: `price=6.680778` (USD site, live rate).
3. Recompute one charged request from its billing expression. Coefficients
   `4.5 / 13.5 / 0.15` are yuan per 1M tokens, so `quota / 500000` is already
   yuan; multiplying by 7.3 is a double conversion.
4. Cross-check a payment. Successful `top_ups` rows pair `money` with
   `amount * 500000`; one yuan per 500,000 quota confirms the CNY-native reading.

Fix: compute every displayed amount with the rate read from that platform
(`price` in CNY mode, `usd_exchange_rate` in USD mode); show "—" when it is
missing instead of falling back to a constant.

Negative result: a hardcoded 7.3 is not a safe default. On token it overstates
by exactly 7.3x; on hub (6.68) it is about 9% high. Both look like normal money
on screen, so no check caught it.

Project record: `~/Projects/Mine/WLB/work/2026/Q3/09/20260921-newapi/20261119-newapi-webapp-review.md`
W-26 (execution record 2026-11-20).
