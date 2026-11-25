# A daemon-spawned script has no HOME (and `set -u` makes that fatal)

## Trigger

- `tools/publish.sh: line 49: HOME: unbound variable` (exit 1, 0.01 s, no stage ran)
  when the same script worked from cron and from a shell.
- Or: any child of a systemd/supervisor service reaches a `$HOME` expansion and
  aborts, or ssh/uv cannot find `~/.ssh/config` / `~/.local/bin`.
- Symptom shape: the job dies before its first real step, so the log shows only
  the shebang/metadata lines.

## What was actually true (2026-11-25, markjour admin panel)

`property: markjour:admin` in `/etc/supervisor/conf.d/markjour.conf` runs
`app.py` as `user=catroll`. The panel starts `tools/publish.sh` as a subprocess
with the inherited environment. That environment had **no `HOME` at all**:

```
$ tr '\0' '\n' < /proc/2372/environ | sort
ADMIN_DEBUG=0
LANG=zh_CN.UTF-8
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/snap/bin
USER=root
...
```

Two traps met: supervisord itself runs from a systemd **system** service (no
login shell), and supervisor's `user=` only setuids — it does not add HOME or
any other login variable. The script's `set -uo pipefail` then turned the PATH
export `export PATH="$HOME/.local/bin:…"` into a hard exit.

Cron was never affected because cron sets HOME; that is why the failure looked
like "only the panel is broken".

## Diagnose in this order

1. Reproduce from the failing caller's environment, not from your shell:
   `env -u HOME bash tools/publish.sh --no-search` — instant, no side effects
   when the die is before the first stage.
2. Read the parent's environment, not its config:
   `tr '\0' '\n' < /proc/<pid>/environ | sort`.
3. Confirm the spawn path: `ps -o user,pid,ppid,cmd -p <pid>`, then read the
   supervisor program block or unit.

## Fixes (do the script fix first, it applies without a restart)

- Script: derive the login home when unset, not from `$USER` (see below):
  `HOME="$(getent passwd "$(id -u)" | cut -d: -f6)"`, fallback
  `HOME="$(cd ~ && pwd)"` (bash substitutes the passwd home for `~` when HOME
  is unset). Fail loudly if both are empty.
- Daemon: add `HOME="/home/catroll"` to the program's `environment=` in the
  tracked supervisor config, then `supervisorctl reread && supervisorctl
  update` (update restarts the changed program; a plain restart does not
  re-read the file). If the installed file is a symlink to the repo copy,
  editing the repo file is the install.
- Validate the config *before* restarting, without root and without touching
  the live process:

  ```python
  from supervisor.options import ServerOptions
  o = ServerOptions(); o.realize(['-c', '/etc/supervisor/supervisord.conf'])
  [ (p.name, p.uid, p.environment.get('HOME'))
    for g in o.process_group_configs if g.name == 'markjour'
    for p in g.process_configs ]
  ```

  Output confirmed `('admin', 1000, '/home/catroll')` before the restart.

## Do not use `$USER` for this

The panel's environment carries `USER=root` while the process runs as catroll;
`USER` is inherited text, not the effective identity. `id -u` + passwd is the
only trustworthy source.

## The check that catches it next time

A shell script's environment contract is testable: source the script's top
block under the daemon's recorded environment and assert the variables it
derives.

```python
DAEMON_ENV = {'PATH': '/usr/local/sbin:…', 'LANG': 'zh_CN.UTF-8'}  # no HOME
subprocess.run(['bash', '-c', 'source "$1"; printf "%s\\n" "$HOME"',
                'bash', str(PUBLISH), '--bogus'], env=DAEMON_ENV)
```

Pass a bogus argument so that if the script ever loses its
`if [ "${BASH_SOURCE[0]}" = "$0" ]` guard, the sourced run exits on the usage
error instead of starting a real deploy. Implemented in
`staticize/tests/test_publish_script.py` (4 tests; the sitemap-target half of the
same run is pinned in `staticize/tests/test_sitemap_target.py`).

## Negative results

- `set -u` alone is not the bug: with HOME set, the same script ran from
  `env -i` (no HOME added by hand, PATH minimal) end to end; exit 0 in 7.2 s.
- `sudo -n true` fails here (`interactive authentication is required`), but the
  supervisor socket is group-writable by `catroll`
  (`srwxrw---- root catroll /run/supervisor.sock`), so `supervisorctl
  reread/update` works without sudo. `supervisorctl` does not need root for a
  group-writable socket — do not assume a restart needs sudo.
