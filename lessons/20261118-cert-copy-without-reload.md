# A copy-based TLS install has no reload path, so renewal never reaches the server

**Signal.** The certificate a listener actually serves is older than the one
acme.sh holds:

```sh
timeout 6 openssl s_client -connect 127.0.0.1:443 -servername d3v.cn </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -notAfter
# subject=CN=d3v.cn
# notAfter=Nov  4 12:12:50 2026 GMT      <- expired 14 days ago

openssl x509 -in ~/.acme.sh/d3v.cn_ecc/fullchain.cer -noout -enddate
# notAfter=Feb 15 12:14:22 2027 GMT      <- the renewed certificate
```

The Caddyfile pointed at `/etc/caddy/certs/d3v.cn/fullchain.pem`, a copy made
on 2026-08-10; acme.sh renewed on 2026-11-17 but nothing copied the result over,
and Caddy does not watch certificate files, so it kept serving an expired chain.
The weekly `sync_acme_certs.sh` did not cover this destination, and the installer
documented "re-run install after renewal" — a manual step that silently rots.

**Check.** Never trust the acme.sh directory or the install script for "the
server has the current certificate". Ask the listener, per SNI:

```sh
for sni in <host1> <host2>; do
  timeout 6 openssl s_client -connect 127.0.0.1:443 -servername "$sni" </dev/null 2>/dev/null \
    | openssl x509 -noout -subject -enddate
done
```

Compare every result with the matching `openssl x509 -in ~/.acme.sh/<domain>_ecc/fullchain.cer -noout -enddate`.

**Fix pattern.** Make the copy a root `oneshot` service + timer that runs after
the renewal cron, compares bytes (no-op when unchanged), verifies the private
key matches the certificate before replacing anything, then reloads the daemon;
`Persistent=true` covers a machine that was off. Do not rely on acme.sh's
`--reloadcmd` when the destination needs root writes the renewal user does not
have (and remember systemd lacks `SUDO_USER`, so render the acme home into the
unit: `Environment=ACME_HOME=/home/<user>`).

**Negative result.** `systemctl reload caddy` is required after the copy; Caddy
does not detect a changed certificate file on its own, and the file mtime alone
does not prove what is served — only `s_client` does.
