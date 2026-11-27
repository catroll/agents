# A crash-looping unit with a per-start log file fills the disk silently

Observed 2026-11-25 on `eqr`. `new-api.service` had restarted **8684 times**
and left **920,979** empty log files in `/var/log/new-api`.

## Signal

- `systemctl is-active new-api` prints `activating`, not `failed` — easy to
  read as "starting up" and move on.
- `systemctl status` shows `Active: activating (auto-restart) (Result: exit-code)`.
- The real number is in `NRestarts`:
  `systemctl show new-api -p NRestarts -p Result -p ExecMainStatus`.
- The app's own log tail repeats the same fatal line every 5 s:
  `dial tcp 127.0.0.1:3306: connect: connection refused`.
- `/var/log/<app>` holds a six-digit file count; `ls` fails with
  `argument list too long` before you ever see the total.

## Cause

`Restart=always` + `RestartSec=5` + a binary that opens a **new timestamped log
file on every start** (`--log-dir`) = one file per 5 s. Each file is ~260 B, so
the byte total looks small; the damage is inode count and directory churn, and
it grows without bound as long as the dependency stays down.

A crash loop is not self-limiting. Nothing in the unit or in `journald` notices
that the *application* log directory is exploding, because those files never
pass through the journal.

## Check

```sh
systemctl show <unit> -p NRestarts -p Result -p ExecMainStatus
systemctl is-active <unit>          # "activating" is NOT healthy
ls -1 /var/log/<app> | wc -l        # count files, not size
du -sb /var/log/<app>
tail -c 4000 /var/log/<app>/<stdout-file>
ss -tln | grep <dependency-port>    # is the dependency even listening?
```

Prefer `ls -1 | wc -l` over `ls`/`find ... | wc -l` on such a directory: with
~10^6 entries a plain `ls` aborts with `argument list too long` and the count
never prints.

## Do

1. Find the dependency first (`connection refused` → is MySQL/Redis actually
   running, and is the unit `enabled`?). `systemctl is-enabled mysql` returning
   `disabled` next to a `disabled`-but-installed package is the tell.
2. Stop the loop before deleting anything:
   `busctl --system call org.freedesktop.systemd1 /org/freedesktop/systemd1 \
     org.freedesktop.systemd1.Manager StopUnit ss <unit>.service replace`
   (works without sudo when polkit allows; a wrong unit name answers
   `Unit name <x> is not valid.` — quote the `.service` suffix).
3. Delete the orphaned files with `find <dir> -maxdepth 1 -name '<pattern>' -type f -delete`,
   which avoids the argument-list limit.
4. Fix the unit so a future outage cannot repeat it: bound the log rotation, and
   consider `RestartSec` backoff or `StartLimitBurst`/`StartLimitIntervalSec` so
   a permanent failure stops retrying.

## Negative results

- `sudo -n` on this host returns `sudo: interactive authentication is required`;
  root-side fixes (journald limits, apt clean, mysql enable) could not be run
  from the agent session and had to be handed to the user.
- `/proc/<pid>/environ` of a root-owned container process is unreadable
  (`权限不够`), so container identity must come from the cgroup path or the
  k3s/containerd metadata, not from its environment.
