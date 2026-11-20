# `sudo: interactive authentication is required` — the agent shell cannot read UFW/iptables or install root-owned artifacts

Symptom: `sudo -n ufw status` (and `sudo -n ss -lntp`, `sudo -n true`) exits
non-zero with

```
sudo: interactive authentication is required
```

even though the session runs with `danger-full-access` file policy.

What it means: the DSH file policy only governs file reads/writes. `sudo` still
asks for the user's password, there is no passwordless rule for `catroll`, and
approval prompts cannot be used as a substitute. `ufw` is active and enabled on
this machine (`systemctl is-active ufw` → `active`), but its rule set lives in
root-only `/etc/ufw/user.rules`.

Do not:

- retry `sudo -n …` with variations, or set `sandbox_permissions`; the sandbox
  is not what blocked it.
- infer firewall state from a listening socket. A service bound to `0.0.0.0` is
  not proof that UFW allows the port, and a loopback bind says nothing about
  other ports. State "could not read the rules" instead of "the port is open".

Instead: hand the check to the user and wait for the output, e.g.

```
sudo ufw status numbered
sudo ufw delete allow 3080/tcp
```

Everything that must land outside the repo (systemd units, `/etc/caddy`,
ufw rules) also follows the project-source-of-truth rule: track the copy in the
repo and ship a script, then have the user run the privileged step.

## The password prompt belongs to the user's tty

`terminal_send` of `sudo -v` stops at `[sudo: authenticate] 密码：`, and the user
types the password into that pty. After that the terminal is user-owned (the
agent can only read it), and sudo's timestamp is per-tty, so a fresh agent shell
still gets `interactive authentication is required` even though the user just
authenticated in a neighbouring terminal. Do not plan on reusing the credential.

Also, do not avoid the privilege problem by starting a parallel instance of the
service under the agent's own user (e.g. a second `ollama serve` on another
port): the user asked for the real service to be tested, and it costs a large
download into a second model store. From the first failed `sudo -n`, hand over a
single paste-ready block that contains the privileged step, then measure from
the unprivileged side.
