# Port 80 "not open" can be a cloud EIP firewall, not nginx

**Signal.** A user reports that typing the bare domain does not open the site
("browser does not default to https"), while `https://<domain>` works. On the
host everything looks correct:

```bash
nginx -T | grep -A3 'listen.*80'      # listen 80; return 301 https://$host$request_uri;
curl -H 'Host: <domain>' http://127.0.0.1/ -o /dev/null -w '%{http_code}\n'   # 301
curl http://<domain>/ -o /dev/null -w '%{http_code}\n'                        # 301 from the office egress
ss -lntp | grep ':80 '                # nginx on 0.0.0.0:80
```

Both the loopback and the office egress answer 301, so the obvious conclusion
"the redirect is missing / nginx is not listening" is wrong.

**Distinguish app from network from outside.** Probe the same IP on both ports
from public nodes; a cloud firewall that blocks 80 but allows 443 shows up as a
clean 0/20 vs 20/20 split:

```bash
# start a check, then poll the returned request_id
curl -s -H 'Accept: application/json' \
  'https://check-host.net/check-tcp?host=<public-ip>:80&max_nodes=20'
curl -s 'https://check-host.net/check-result/<request_id>'
```

Real case 2026-11-17 (`token.shanedit.com`, UCloud `cn-gd`): 20/20 nodes timed
out on TCP 80 while 20/20 reached TCP 443 at the same moment. That rules out
DNS, certificate, nginx and the backend in one shot.

**The whitelist trap.** A 301 from your own egress only proves *your* source IP
is allowed. The host can carry no firewall at all and inbound can still be
filtered upstream:

```bash
iptables -S                           # empty
which ufw firewalld nft               # not installed
```

On UCloud the instance metadata records the public EIP and its id, and inbound
is controlled by the console's "外网防火墙", which is invisible on the box:

```bash
python3 -m json.tool /usr/local/ucloud/.cache/metadata.json
# uhost-1vnv4xpp0yso (newapi-token.shanedit.com), eip-1vnv51y0tng2, 106.75.145.225
```

So "the server has no http access" is right, but the fix is an inbound rule for
TCP 80 in the cloud console — changing nginx again changes nothing. State the
allowed source explicitly (`0.0.0.0/0`, or the users' egress ranges if the
whitelist policy is deliberate) and re-run the 20-node check afterwards; the
first accepted request then appears in the access log with `status=301`.

**Related.** `firewall-rule-needs-a-packet.md` covers a host UFW that drops the
packet; this file covers the layer above it, where there is no host rule to
inspect. `vhost-repo-is-not-live.md` covers a correct repo file whose live vhost
is stale; here the live vhost is correct too, and the block is one layer further
out. Check the outermost layer with an external probe before editing nginx.