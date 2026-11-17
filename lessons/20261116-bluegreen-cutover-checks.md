# Blue-green cutover checks: retired units come back, and a version check proves nothing

2026-11-16, New API blue-green rollout: two systemd slots on 8080/8081, nginx reload to
switch, `active-port` as the single knob. Three traps, each of which produced or nearly
produced a user-visible 502.

## 1. A unit that `Wants=` the retired unit resurrects it

Symptom: a unit you stopped comes back a few minutes later and occupies a port.

Cause: `newapi-landing.service` carried `After=new-api.service` / `Wants=new-api.service`
from before the split. `Wants` starts the dependency on **every** activation, regardless
of `systemctl disable` on the dependency. Once the app moved to `new-api@<port>`, every
5-minute landing refresh started the old single-instance unit on 8080.

Check before retiring a unit:

```sh
grep -rn "Wants=\|Requires=\|After=\|BindsTo=\|PartOf=" /etc/systemd/system/ | grep -F "new-api.service"
systemctl list-dependencies --reverse new-api.service
```

Fix or remove the dependents, then `systemctl daemon-reload`. `disable` alone is not enough.

## 2. "Expected version" from `/api/status` does not mean *your* instance is up

The health check polled the target port and accepted `data.version == tag`. A resurrected
single-instance unit on that same port ran the same binary and returned the same version,
so the check passed while the new slot had not bound the port. The switch happened, the
stray process was stopped, and new connections were refused for ~0.5 s.

Check that the listener is the unit you started:

```sh
port=8081
ss -ltnp | grep -F ":$port " | grep -o 'pid=[0-9]*'
systemctl show -p MainPID --value "new-api@$port.service"
```

Compare the two, and keep this inside the deploy script, not only in the runbook.

## 3. Right after `systemctl reload nginx`, an old worker still answers

`reload` starts new workers and retires old ones gracefully; an old worker keeps serving
the old upstream for a moment. A one-shot smoke test right after reload read the old
version and rolled the healthy switch back. On a healthy site the first cutover attempt
aborted this way.

Give the post-reload assertion a retry window (40 × 0.25 s) and keep the failure path
switching back (it did, and nothing dropped).

## Also

- Probing a rate-limited endpoint at 10 req/s triggers 429s that look like an outage. Use
  <=2 req/s, and keep the probe files so a 429 can be told apart from a 502.
- `systemctl stop --no-block` returns immediately; a `deactivating` slot still holds its
  port. Check `systemctl show -p ActiveState` before reusing the slot.

## 4. Over HTTP/2 an old worker can proxy one more request a second after reload

Measured on 2026-11-17: a switch and an immediate `systemctl stop` of the old slot
produced two 502s, both `connect() failed (111) ... upstream: http://127.0.0.1:8080`,
both `GET /api/status HTTP/2.0`. The reload is asynchronous and an old worker busy
with something else can accept another stream on its HTTP/2 connection before it
gets to the GOAWAY, so the window is seconds, not milliseconds.

Put the settle inside the switch primitive (`switch-site.sh`), not in each caller:
deploy, rollback and manual switches then cannot forget it. Three seconds covered
the observed case; a worker busy with a slow request can still outlive it, so keep
the smoke's version retry as a second layer.
