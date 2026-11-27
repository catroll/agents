# A listening port that instantly refuses IPv4: check netfilter DNAT before the daemon

## Symptom

A reverse proxy is `active`, its socket shows up in `ss`/`lsof` (dual-stack `*:443`), the kernel
has dual-stack enabled (`net.ipv6.bindv6only=0`), yet every IPv4 connection fails **instantly**:

```
curl: (7) Failed to connect to eqr.hosts.d3v.cn port 443 after 0 ms: Could not connect to server
```

while other loopback ports on the same host work. Also: `bind 0.0.0.0:443` from a test program
returns `[Errno 98] Address already in use` — proof the port *is* bound, so "no listener" is a
wrong reading of `ECONNREFUSED`.

## The check that catches it

`ECONNREFUSED` in 0 ms is either "nothing listening" or "a REJECT / RST was manufactured".
Distinguish with one packet capture and one counter:

```bash
sudo tcpdump -i lo -nn 'tcp port 443'          # run, then curl 127.0.0.1:443 in another shell
sudo iptables -t nat -L -n -v | grep -E 'CNI-|KUBE-|DNAT'
```

If the SYN never appears on `lo`, the packet is being rewritten before it is routed — netfilter,
not the daemon. Re-run the curl and watch the rule counters: a `dpt:443` rule incrementing
(19 → 20) is the culprit, and the target (`--to-destination 10.42.1.2:443`) tells you which
process owned the port. `iptables -t nat -L -n -v` is not optional here: the nat table is where
hostport and LoadBalancer DNAT live, and `ip addr` / `ss` show nothing wrong.

## Root cause that produced it

k3s was stopped with `systemctl stop k3s` (or `disable` + reboot of the unit) instead of
`k3s-killall.sh`. The cluster died but its rules stayed:

```
-A PREROUTING -m addrtype --dst-type LOCAL -j CNI-HOSTPORT-DNAT
-A CNI-HOSTPORT-DNAT -m multiport --dports 80,443 -j CNI-DN-<hash>
-A CNI-DN-<hash> -p tcp --dport 443 -j DNAT --to-destination 10.42.1.2:443
-A KUBE-SERVICES -d <host-ip>/32 -p tcp --dport 443 -j KUBE-EXT-<hash>   # → 10.42.1.8:8443
```

The pod IPs are gone, so the DNAT'd SYN hits a dead address and the host answers `RST`. The
daemon's socket is bound and healthy the whole time; it just never sees the connection.

## Fix

```bash
sudo /usr/local/bin/k3s-killall.sh    # stops k3s, removes KUBE-/CNI-/flannel rules + cni0/flannel
```

No caddy restart needed — the moment the rules are gone the port serves again. Verify both the
rule counters are 0 and a real request returns 200.

## Generalisable rules

- A bound socket + instant `ECONNREFUSED` + working neighbours = **netfilter rewrite**, not a
  daemon problem. Check `nat` PREROUTING, not just `filter` INPUT, and not just UFW: UFW's
  `ufw-user-input` was allowing the port the whole time (its `REJECT` chain was empty).
- `net.ipv6.bindv6only=0` + a `:::443` socket means IPv4 is covered by that socket; a
  `[Errno 98]` on `0.0.0.0:443` is expected and is **not** evidence of a stray process.
- Stopping a container orchestrator (k3s, kube-proxy, docker swarm) without its cleanup script
  leaves host-port DNAT behind. Always run the distro's killall/uninstall, and re-check
  `iptables -t nat -L -n -v` for `CNI-`/`KUBE-` after stopping it.
