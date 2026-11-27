# An agent loop that calls `pkexec` per step charges the operator one password prompt per step

Learned 2026-11-27, during the k3s/iptables caddy outage (`20261127-iptables-dnat-hijacks-listening-port.md`).
The incident needed ~45 privileged reads and writes; each `pkexec` raised a separate polkit
dialogue, and the cost was the operator sitting in front of the machine, not the work.

## The mechanism

- The agent's shell is a child of a **user** systemd unit (`dsh-web.service`,
  `ExecStart=dsh web …`, uid `catroll`), so every tool call runs unprivileged.
- polkit action `org.freedesktop.policykit.exec` is `implicit active: auth_admin` with **no**
  `_keep` / `auth_admin_keep` variant: no caching, one prompt per invocation.
- `sudo` was equally useless: no timestamp cache in that session, so `sudo -n true` failed with
  `sudo: interactive authentication is required`.

Check before promising an unattended workflow:

```bash
systemctl --user cat dsh-web.service | grep -E 'ExecStart|User'
pkaction --action-id org.freedesktop.policykit.exec --verbose | grep -E 'implicit|_keep'
sudo -n true && echo "have passwordless sudo" || echo "no passwordless sudo"
```

## What to do instead: a narrow sudo broker

Give the operator's account one `NOPASSWD` rule for **one root-owned wrapper binary** that exposes
fixed subcommands — not `NOPASSWD: ALL`, not a `pass-through exec "$@"`.

- `Defaults:catroll !lecture`, `catroll ALL=(root) NOPASSWD: /usr/local/bin/eqr-ops`
- The wrapper validates every argument (regex/allowlist) and exits 2 on anything unexpected.
- Mutating subcommands keep a gate: validate the candidate config, `cp -a` a timestamped backup,
  then install with the right owner/mode.
- A `check` mode diffs the repo copy against the installed copy; installation refuses to
  overwrite a drifted live file unless `--force`, and validates the candidate with `visudo -cf`.

Working implementation: `~/Projects/Mine/WLB/eqr/host/agent/`.

## Negative result worth keeping: verify as the target user, not as root

`sudo -n true` succeeds when run from a root shell regardless of the sudoers rule — testing the
install that way proves nothing. Run the probe as the account that will use it:

```bash
runuser -u catroll -- sudo -n /usr/local/bin/eqr-ops status caddy
```

Also assert the boundary still holds, i.e. the broker did not become general root:

```bash
sudo -n true                      # must still fail: interactive authentication is required
sudo -n eqr-ops unit-start nginx  # must exit 2: unit not allowlisted
sudo -n eqr-ops lsof-port 99999   # must exit 2: port out of range
```

## Do not escalate reads that need no privilege

Half the prompts were avoidable: `/etc/caddy/Caddyfile` is mode 644, `journalctl` works through the
`adm` group, `ss -tln` needs no `-p`, and the Caddy admin API on `127.0.0.1:2019` answered the
unprivileged user — `caddy reload` never needed root, only `caddy validate` did (private keys are
`caddy:caddy 600`). Sort commands into "root required" and "root-free" first; the wrapper only
needs the former.
