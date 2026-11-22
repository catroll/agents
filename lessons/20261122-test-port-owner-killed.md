# A test that binds a port must not kill the port's owner on cleanup

**Signal.** A test server prints `OSError: [Errno 98] Address already in use`;
the request meant for it is answered by a different application
(`415`, `写接口只接受 application/json`); afterwards that application is down.
`systemctl --user status` shows `code=exited, status=0/SUCCESS`, and a unit with
`Restart=on-failure` did not come back.

**Cause.** Cleanup derived kill targets from the port:

```bash
for p in $(ss -ltnp | grep :8765 | grep -oP 'pid=\K[0-9]+'); do kill "$p"; done
```

The test server had failed to bind, so port 8765 belonged to a pre-existing
user service. Cleanup killed that service instead of the test.

**Check.**

- Before starting a server on a test port, assert it is free and abort if not:
  `ss -ltn | grep -q ":$port " && { echo "port $port busy"; exit 1; }`.
- Keep the PID the shell started (`pid=$!`) and kill only that. Never compute
  kill targets from a port, a process name, or `pgrep -f`.
- After `kill`, check the port is free again. An unclean exit hides the mistake.

**Second trap.** `Restart=on-failure` treats SIGTERM as a clean exit
(`status=0`), so a service killed this way stays down. Restore it with
`systemctl --user start <unit>` and verify with `is-active` plus a `curl` to its
port; do not assume the unit self-heals.

**Evidence (2026-11-22).** Testing `docs/english/web/pronounce_server.py` on
port 8765: bind failed, the curl landed on `newapi-web.service` (415), cleanup
killed pid 2932903, and the unit stayed `inactive (dead)`. Restored with
`systemctl --user start newapi-web.service`; `is-active` → `active`,
`curl http://127.0.0.1:8765/` → `200`. The retest used free ports 18765/18799
and killed only the PIDs it started.
