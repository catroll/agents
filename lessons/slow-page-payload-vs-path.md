# "The page is slow" is two questions: how big, and how fast

Never start with the nginx/application config. Split the delay into **payload** and
**transport** first; they have completely different fixes, and the config is
usually innocent.

1. **Ask the browser which file is slow.** WebDriver `execute/sync` on a real
   page, one row per resource — `duration` and `transferSize` identify the single
   critical-path file where static analysis would only produce a list:

   ```javascript
   performance.getEntriesByType("resource").map(e => ({
     n: e.name, t: Math.round(e.startTime),
     d: Math.round(e.duration), s: e.transferSize
   }));
   ```

   Real case: 51 s to a login form, of which `main.js` was 49 s / 903,792 B, while
   HTML TTFB was 267 ms and every API call was under 1.3 s. One number, no guessing.

2. **Measure both endpoints independently before blaming either.** From the client,
   a well-peered CDN (`speed.cloudflare.com`) or a domestic mirror. From the server,
   the same trick reversed — `__up` for egress, `__down` for ingress. Here the
   server did 37 MB/s to Cloudflare and the client 20 MB/s from a domestic mirror,
   yet 8 KB/s to each other: the **path**, not the host. An EIP/bandwidth cap would
   have capped the Cloudflare test too, so that measurement also clears the bill.

3. **Get the loss ratio from `ss -tin` on both ends.** `bytes_retrans / bytes_sent`
   is the number that settles it (19 % here), and `cwnd:2 ssthresh:2` shows the
   congestion window pinned at its floor. Prefer this over packet captures — no
   root needed.

4. **Distinguish loss from a rate limit with a 1-second rate profile.** Loss gives
   burst-and-nothing (`12K, 32K, 16K, 0, 0, 16K, …` — retransmission timeouts);
   `limit_rate`/token-bucket gives a steady floor. Parallel connections scaling
   linearly (~4 × 11 KB/s ≈ 44 KB/s) also means per-connection loss, not a total cap.

**Corollary.** A cross-border SPA that is fine warm can be a minute cold: check the
cache both ways. Here a warm reload was 2 s with `transferSize=0` while the cold
load was 51 s, so "slow for me" and "slow for everyone" are different reports.

**And.** Test more than one hour before writing "peak-hour congestion". This one
was 13.6 KB/s at 00:13 and 7.6 KB/s at 14:07 — bad at both ends of the day, which
makes it persistent peering damage rather than a busy hour, and that changes the
recommendation (accelerate the path; do not wait for off-peak).

**HTTP/2 is a pessimisation on a lossy path.** "Enable h2, it is faster" is the
default reflex and it is wrong here. HTTP/1.1 gives the browser six connections per
origin, each with its own congestion window, so throughput multiplies with
parallelism (measured on this path: 4 parallel connections ≈ 4× one connection,
~44 KB/s vs ~13 KB/s). HTTP/2 multiplexes every stream onto a single TCP connection,
which is exactly the wrong shape when that connection is losing 19 % of its packets.
Leave `http2 on;` out on a lossy vhost and say why in the config, or the next person
will helpfully "fix" it.

**Check the compression headroom before adding a compressor.** The instinct is to
switch on nginx gzip, but the app server may already be compressing. Compare the
bytes actually on the wire against `gzip -9` of the same file before claiming a win:
here the backend produced 903,492 B and `gzip -9` only reached 894,805 B (1 %), so
nginx-side compression was pointless. A whole class of "optimisations" evaporates
once you measure the number first.

**Changing the sender's congestion control is not a fix for peering loss.** The
tempting next step after "cubic collapses to cwnd 2" is `tcp_congestion_control=bbr`
on the server. A/B it before keeping it: six 100 KB samples per arm on the same
lossy path gave cubic 11.7 KB/s mean vs BBR 9.2 KB/s — no win, because the loss is
random peering damage, not a capacity signal. Two samples cannot resolve this
(variance here was 5–17 KB/s); use several short ranges and compare the means, then
revert. The module loads, the sysctl is host-wide, and neither improves the path.

**"Extract the statics to nginx" is not a path fix.** Same host + same wire = same
throughput; the extraction only pays if it changes something else: a better path
(CDN/other host), more parallel connections (split the one bundle the browser
serialises), or a smaller encoding (brotli/zstd needs a custom nginx build). Check
the server first — a 0.66 s TTFB and a 3.36 MB body is a transport problem, not a
web-server problem.

