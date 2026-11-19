# `sudo scripts/install-caddy.sh install` → `certificate not found: /root/.acme.sh/...`

Symptom: an installer that reads files from the invoking user's home works as
`bash scripts/install-x.sh render`, then fails under sudo with

```
error: certificate not found: /root/.acme.sh/hosts.d3v.cn_ecc/fullchain.cer (issue it with acme.sh first)
```

while `ls -l /home/<user>/.acme.sh/hosts.d3v.cn_ecc/fullchain.cer` is fine.

Cause: `sudo` runs a root login shell environment and sets `HOME=/root`. Any
default written as `${HOME:-/root}/...` silently points at root's home, and the
first check that needs the file dies before touching the target.

Fix: resolve the invoking user's home from `SUDO_USER`, and keep an explicit
escape hatch:

```sh
ACME_HOME=${ACME_HOME:-}
if [ -z "$ACME_HOME" ] && [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != "root" ]; then
	ACME_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
fi
ACME_HOME=${ACME_HOME:-$HOME}
```

Name `--cert-src` / `ACME_HOME` in the error message, and put the caveat in the
runbook next to the `sudo` command — it is a property of sudo, not of one
script.

Check without root (the resolution, not the privileged part):

```sh
env -i PATH=/usr/bin:/bin SUDO_USER=<user> HOME=/root bash -c '...resolution snippet...; echo "$ACME_HOME"'
```

Negative results: `sudo -E` preserves HOME but is not always permitted and still
runs a root shell; hardcoding `/home/<user>` breaks on any other account or
machine. Prefer SUDO_USER plus an explicit override.

## 2026-11-18: a migration script silently imported nothing under sudo

Second occurrence, different script: `sudo scripts/migrate-auth-users.sh apply`
printed success and left `/etc/tinyauth/users.txt` unchanged. The source paths
were built as `${HOME}/Projects/...`, and under sudo `HOME=/root`, so every
source was "missing" and the loop had nothing to do. No error: the script
treated "no sources" as "nothing to migrate".

Two fixes, both worth keeping:

1. Resolve the caller's home from `SUDO_USER` (`getent passwd … | cut -d: -f6`)
   before building any default path, with the same env override as
   install-caddy (`CALLER_HOME`).
2. Fail loudly when the collected source set is empty. "Nothing to do" is a
   correct outcome only when the sources were read and contained no accounts;
   it is never correct when the sources were never found.

Test it the way the installer is tested: `env -i PATH=/usr/bin:/bin
SUDO_USER=<user> HOME=/root` and assert the plan lists the expected source rows.
