# Company server access needs an IP whitelist request to 孔俊

Confirmed by the user on 2026-11-12; updated 2026-11-24 after operations moved
the whitelist from single IPs to a **network segment**.

- The user is on a labour contract (劳务合同), not an employee account, so
  there is no default intranet access. Reaching company servers from the
  public internet requires the source IP to be inside a whitelisted segment
  maintained by colleague 孔俊.
- An IP change no longer implies an SSH outage: if the new address still falls
  inside the segment, the three machines stay reachable. Do not call access
  "blocked" from the IP alone — probe SSH.
- If a probe fails with `connect to host <ip> port 22: Connection timed out`
  while DNS resolves fine, that is still the whitelist/firewall, not sshd, the
  key or the route. Do not debug the server or the client config; report the
  new IPv4 and wait.
- Three machines are in scope:
  - `sctest.hosts.d3v.cn` = 47.237.217.143
  - `newapi-cn-201.hosts.d3v.cn` = 106.75.145.225
  - `newapi-us-101.hosts.d3v.cn` = 52.9.253.68
- The hourly cron job watches the public IPv4 **and** probes SSH on all three:
  `0 * * * * /usr/bin/python3 /home/catroll/Projects/Mine/WLB/tools/scripts/publicipchk.py >> /tmp/public_ip.err 2>&1`.
  Host list and thresholds live in `tools/scripts/publicipchk.toml`; do not
  hard-code them again. It pushes when the IP changes or any probe fails, and
  reports the current IP, whether it changed, and each machine's status.
- A changed IP with all three green is explicitly "no action needed". A failed
  probe is reminded every 6 hours (configurable) and a recovery is pushed once.
- When SSH is unreachable, message 孔俊 with the new public IP and the three
  machine IPs, e.g.:
  `我这里的公网 IP 又变了：117.152.220.97 还是那三台机器帮忙配置一下：47.237.217.143 106.75.145.225 52.9.253.68`
- Confirm the current **IPv4** egress before reporting it — this host is
  dual-stack, and `ifconfig.me` answers the IPv6 address, which is not what the
  whitelist takes:
  `curl -4 -s https://myip.ipip.net` (2026-11-12: `117.152.220.97`, 湖北武汉移动;
  `-4` against ifconfig.me, api.ipify.org and ip.sb all returned empty).
  2026-11-24 19:51: `117.152.145.232`, 湖北武汉移动; all three SSH probes
  passed from that address.
- Check the current view with
  `/usr/bin/python3 tools/scripts/publicipchk.py --dry-run -v`; use
  `--force-notify` only when a real test message is wanted.
- If the probe fails, anything that needs those machines (deploys, log reads,
  config changes) is blocked; say so instead of retrying ssh. If the probe is
  green, the machines are reachable even after an IP change.
