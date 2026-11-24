# EnvironmentFile= overrides Environment= from a drop-in

Observed 2026-11-24 on `eqr`, testing a systemd **user** unit's `OnFailure=`
path. A "test" notification reached the production ntfy topic.

## Signal

- The unit has `EnvironmentFile=%h/.config/update-check.env` (real topic URL).
- A drop-in adds `Environment=NTFY_TOPIC_URL=http://127.0.0.1:18099/topic` so a
  test run cannot reach the real topic.
- The run "succeeds" (`alert sent` printed), the local capture server logs zero
  requests, and the production topic receives the message.

## Cause

systemd applies `EnvironmentFile=` after `Environment=`, so values read from a
file win over inline values — including inline values added by a drop-in.
`systemctl cat` shows both lines and looks correct.

## Check

```sh
systemctl --user cat update-check-failure.service
systemctl --user show update-check-failure.service -p Environment -p EnvironmentFiles
```

The second command shows inline values and the file path, but not the file
contents; read the file as well before claiming the effective value.

## Do

- To redirect a unit for a test, **replace the env file it reads**: copy the
  live file aside, write the test file, run, restore, then `cmp` both sides.
- Or copy the whole unit to a throwaway name that points at a test env file and
  run that unit.
- Never add `Environment=` to a drop-in to override an `EnvironmentFile=`.

## Also

The cleanup after this test never ran: the command was a `set -e` script and its
check `ls /tmp/ntfy-capture && cat ...` failed first, so the drop-in and the test
HTTP server stayed behind. Put the check that can fail last, or run cleanup
under `trap ... EXIT`.
