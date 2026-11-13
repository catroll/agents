# A firewall rule is not proven until a packet arrives after it

**Signal.** A LAN client times out to a service that works from the host, and
`/var/log/ufw.log` contains a line like:

```
[UFW BLOCK] IN=eno1 SRC=192.168.1.42 DST=192.168.1.38 PROTO=TCP DPT=8000 ... SYN
```

That log is decisive: DNS resolved, the LAN path works, and the host firewall
dropped the packet. Do not debug the app, the client URL or DNS first.

**Check the timestamps, not only whether the rule exists.** Compare the last
block with the rule file's mtime:

```bash
date -Is
stat -c '%y' /etc/ufw/user.rules
grep 'DPT=8000' /var/log/ufw.log | tail -1
```

Real case: last block `14:44:32`, `user.rules` modified `14:44:48`. The failed
attempt predated the rule, so "I allowed the port and it still fails" was not a
firewall bug — the client had not retried since the rule took effect. Retry
once, then judge.

**Fix and verify.** Prefer a scoped rule, and confirm success in the service log
rather than in `ufw status` alone:

```bash
sudo ufw insert 1 allow from 192.168.1.0/24 to any port 8000 proto tcp
sudo ufw reload
```

The first accepted request shows the client source, for example
`::ffff:192.168.1.42 - "GET /healthz HTTP/1.1" 200 OK`.

**A localhost curl proves nothing about the input chain.** It uses the loopback
path and never traverses the rules that decide whether another LAN host may
connect.

