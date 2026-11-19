# A helper that returns 1 as a normal outcome silently kills the script under `set -e`

Symptom: `sudo scripts/install-tinyauth.sh install` printed
`==> created first user 'alice' in /etc/tinyauth/users.txt` and then exited,
with no error line, status 1. The next step (installing the systemd unit) never
ran, so the service was never created.

Cause: a guard written as a boolean:

```sh
port_owned_by_other() {
	listener=$(ss -lnt | awk ...)
	[ -n "$listener" ] || return 1        # normal "free port" outcome
	...
}
```

and called bare:

```sh
port_owned_by_other    # under set -e: return 1 aborts the whole script
```

`set -e` cannot distinguish "false" from "failed". The failure looks like a
silent stop right after the last successful log line, which reads like a crash
in the command that just succeeded.

Fix: a shell helper should return 0 on success and `die`/`exit` on failure; use
non-zero returns only for values the caller deliberately branches on, and then
always call them as `if helper; then ...` or `helper || true`.

Because this path only runs as root, `bash -n` and an unprivileged dry run both
miss it: test it by sourcing the installer (guard the action dispatch with
`if [ "${BASH_SOURCE[0]}" = "$0" ]`), pointing every path at a temp tree and
stubbing `systemctl`/`curl` in `PATH`. The test then calls the same helpers the
root path calls.
