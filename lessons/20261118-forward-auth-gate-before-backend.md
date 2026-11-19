# `install-caddy.sh install` succeeds while the `forward_auth` backend is down → 502 for every gated host

Symptom: after adding `forward_auth 127.0.0.1:3000` to a Caddyfile and reloading,
every site that imports the gate answers 502, the auth portal included; the
Caddy log shows `dial tcp 127.0.0.1:3000: connect: connection refused`.

Cause: the Caddyfile is syntactically valid and `caddy validate` passes without
the auth backend running. The installer therefore swapped the config and
reloaded while the service it depends on had never started (its own install had
failed earlier in the same session).

This is a total outage of everything behind the gate, not a degraded mode: the
gate is now on the request path of every protected host.

Fix, in the installer, before the swap:

```sh
grep -q 'forward_auth 127.0.0.1:3000' "$candidate" || return 0
curl -fsS --max-time 3 http://127.0.0.1:3000/api/healthz >/dev/null 2>&1 ||
	die "candidate gates services but the auth backend is not healthy"
```

Do not rely on "the operator ran the auth install first": the two commands are
separate, the first can fail, and the second cannot tell. A health check on the
dependency makes the second command the guard.

Two related traps from the same incident:

- A manual instance of the auth service on the same port makes a *failed*
  systemd start look healthy: `curl /healthz` answers 200 from the manual
  process while the unit is dead. Check `systemctl is-active` first, and refuse
  to install when the port is owned by a non-systemd process.
- Vendor CLIs printed to a TTY emit CRLF and sometimes ANSI colour. Capture both
  streams, strip `\r` and escape codes, and print the raw output when parsing
  yields nothing — a silent "unexpected output" error hides the real message.

Recovery while the backend is missing: run the auth service (even a manual
instance) so the gate can answer, then replace it with the system unit in the
right order (stop the manual one first).
