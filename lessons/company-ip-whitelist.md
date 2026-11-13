# Company server access needs an IP whitelist request to 孔俊

Confirmed by the user on 2026-11-12.

- The user is on a labour contract (劳务合同), not an employee account, so
  there is no default intranet access. Reaching company servers from the
  public internet requires the source IP on a whitelist maintained by
  colleague 孔俊.
- After a public-IP change, `ssh <user>@<ip>` fails with
  `connect to host <ip> port 22: Connection timed out` while DNS resolves
  fine. That is the whitelist, not sshd, the key or the route — do not debug
  the server or the client config; report the new IP and wait.
- Three machines need the whitelist:
  - `sctest.hosts.d3v.cn` = 47.237.217.143
  - `newapi-cn-201.hosts.d3v.cn` = 106.75.145.225
  - `newapi-us-101.hosts.d3v.cn` = 52.9.253.68
- A local cron job watches the public IP and pushes a WeChat message when it
  changes: `0 * * * * /usr/bin/python3 /home/catroll/Projects/Mine/WLB/tools/scripts/publicipchk.py >> /tmp/public_ip.err 2>&1`.
- On an alert, the user messages 孔俊 with the new public IP and the three
  machine IPs, e.g.:
  `我这里的公网 IP 又变了：117.152.220.97 还是那三台机器帮忙配置一下：47.237.217.143 106.75.145.225 52.9.253.68`
- Confirm the current **IPv4** egress before reporting it — this host is
  dual-stack, and `ifconfig.me` answers the IPv6 address, which is not what the
  whitelist takes:
  `curl -4 -s https://myip.ipip.net` (2026-11-12: `117.152.220.97`, 湖北武汉移动;
  `-4` against ifconfig.me, api.ipify.org and ip.sb all returned empty).
- Until the whitelist is updated, anything that needs those machines (deploys,
  log reads, config changes) is blocked; say so instead of retrying ssh.

