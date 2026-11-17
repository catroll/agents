# Config pushed through an admin API is not persisted

## Signal

`https://host/home` answers 200 right after `POST http://127.0.0.1:2019/load`,
then returns `no certificate available for 'host'` / 404 after
`systemctl restart caddy`, with no change to the project files.

## Cause

The admin API replaces the *running* configuration. `/etc/caddy/Caddyfile` still
lacks the block, so any restart or reload re-reads the file and drops the
runtime change. nginx (`-s reload` reads files), HAProxy's data-plane API
(in-memory until committed) and most similar surfaces behave the same way.

## Check

- Ask where the config will come from on restart before trusting the URL:
  `grep -n '<block marker>' /etc/caddy/Caddyfile` must also match.
- `systemctl show -p ActiveEnterTimestamp caddy` shows whether the daemon
  restarted during your session; that is the moment the runtime config died.
- Dump the running config (`curl 127.0.0.1:2019/config/`) before restarting a
  proxy for an unrelated permission test, so it can be replayed afterwards.

## Negative result

`caddy reload --config <file>` also only posts that file's config; it does not
write `/etc/caddy/Caddyfile`. Persistence needs the file edit (root) and a
reload — for this machine that is `sudo scripts/install-caddy.sh install` in
`tools/homepage`.
