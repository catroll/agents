# `VAR: 未绑定的变量` only under `sudo` — `bash -n` and a non-root dry run never execute the branch

**Signal.** `sudo scripts/install-caddy.sh install` printed
`==> installing certificates` and then died:

```text
scripts/install-caddy.sh: 行 181: CERT_SRC3: 未绑定的变量
```

The script runs with `set -euo pipefail`. A third certificate source directory
was passed to the sync helper but never defaulted (`CERT_SRC3=${CERT_SRC3:-…}`
missing), and `bash -n` plus `make caddy-cert-check` (`--dry-run`, no root)
both passed because that line sits behind `require_root` / the
system-Caddyfile branch, which neither check reaches.

**Check.** Do not accept "syntax ok + dry run ok" as proof for a script with
privileged branches. Extract everything before the action dispatch and call the
root-only helper with stubbed side effects:

```sh
sed -n '1,/^case "\$ACTION" in/p' script.sh | head -n -1 >"$tmp/funcs.sh"
bash -uc 'source '"$tmp"'/funcs.sh; CERT_SYNC='$tmp'/stub; SYSTEMD_DIR='$tmp'/units; install_certificates' 
```

`bash -uc` turns any still-unset variable into a hard failure, and a stub in
place of `systemctl`/the real copy step keeps it runnable without root. Commit
that harness (here `scripts/tests/test-install-caddy.sh`, run by
`make scripts-test`), and assert the arguments the helper passes (three
`--cert-src` pairs, `--no-reload`, rendered `ExecStart`/`ACME_HOME`) so a
dropped pair also fails in the test rather than under sudo.

**Negative result.** Neither `bash -n`, `shellcheck`-style review, nor a dry
run that takes a different branch can catch a missing default; the failure only
appears at execution time in the privileged branch.
