# A "DDNS failed" alert is the provider's verdict, not the network's

**Signal.** ddns-go posts `- IPv6 (<addr>): failed` (or an ntfy message with a
unix timestamp) while the host's IPv6 egress works and the router is healthy.
The provider's record still holds an address the host no longer has.

**Read the provider's error body first.** ddns-go logs it verbatim:

```
Failed to query domain info! Response body: {"Message":"Specified access key is disabled.",
"Code":"InvalidAccessKeyId.Inactive"} ,Response status code: 400
```

`InvalidAccessKeyId.Inactive` = the credential exists but is disabled: not a
network error, not a missing record, not a firewall problem. Compare the two
sides instead of guessing:

```bash
dig +short AAAA eqr.hosts.d3v.cn @223.5.5.5   # what the world resolves
ip -6 -o addr show scope global               # what the host actually owns
```

A record value absent from the second list is dead, whatever else looks fine.

**One alert can cover days of failure.** ddns-go fires its webhook once, on the
third consecutive failure after start (`current failure times: 407`), then stays
quiet until the next restart. Count before calling it a one-off:

```bash
journalctl -u ddns-go --no-pager | grep -c InvalidAccessKeyId.Inactive
```

**Look for a working credential before minting one.** acme.sh stores
`SAVED_Ali_Key`/`SACED_Ali_Secret` in `~/.acme.sh/account.conf`, and a read-only
`DescribeDomainRecords` proves them without touching DNS. Here acme.sh's key
answered 200 while ddns-go's returned `Inactive` — two consumers of one Aliyun
account drifting apart, most likely a key rotation that updated one and not the
other.

**Then fix the address selection too.** With `net.ipv6.conf.<if>.use_tempaddr=2`
ddns-go publishes the *temporary* privacy address, which is regenerated on every
reboot and prefix change. Pin the IPv6 with ddns-go's regex (e.g. the DHCPv6
`::4`, or the `mngtmpaddr` address) or the record goes stale again at the next
boot even with a healthy key.

**Negative result.** ddns-go v6's config API is not `/api/config` (that serves
index.html); the session cookie comes from `POST /loginFunc` with a JSON body,
and the config is pushed to the page rather than fetched by a known REST path.
The web UI password lives in the install dir (`admin_password.txt`).

**A no-match regex is not a failure, and ddns-go never exits on an IP error.**
I told the owner a prefix change would make it "报错停下". The source says
otherwise (v6.17.1, `config/config.go` `getIpv6AddrFromInterface`): an unmatched
`Ipv6Reg` logs `没有匹配到任何一个IPv6地址, 将使用第一个地址` and returns
`Address[0]`; and `RunOnce` errors only clear that round's cache, the timer
loop keeps firing (the 491-failure morning is the proof — the process never
left). So the risk of pinning is a *silently wrong* address, never a dead
service. When asked what a tool does at an edge, open its twenty lines before
answering: "it will stop" is a claim about code, and a plausible failure mode is
worth less than one `grep`.

