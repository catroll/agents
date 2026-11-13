# A cron line that has never run looks installed

**Signal.** A crontab entry has been in place for weeks and its log contains the
same one-line failure on every attempt:

```
make: uv: 没有那个文件或目录
make: *** [Makefile:80：deps] 错误 127
```

**Cause.** cron runs a job with `PATH=/usr/bin:/bin`, not your shell's `PATH`.
Anything installed per-user (`uv`, `cargo`, `pipx` shims in `~/.local/bin`) is
invisible there, so a job that shells out to `make`/`uv`/`node` dies before it
does any work — while the same command typed in a terminal succeeds.

**Check.** Run the job the way cron does before installing it, and again after:

```bash
env -i HOME="$HOME" PATH=/usr/bin:/bin SHELL=/bin/sh LOGNAME="$USER" \
  /path/to/job.sh; echo "exit=$?"
```

**Fix.** Set `PATH` (plus `LANG`, and any transport variable such as
`RSYNC_RSH` or `GIT_SSH_COMMAND`) inside the script, not in the crontab line, so
a manual run and a cron run behave identically. Then read the job's existing log
once: "it is in the crontab" is not evidence that it has ever worked.

**Also: `%` in a crontab command is not a literal.** cron turns an unescaped
`%` into a newline and feeds the rest to the command's stdin, so a probe written
as `* * * * * date "+%F %T" >> log` is executed as `date "+` and silently
produces nothing (journal shows `(catroll) CMD (date "+cron-alive )`). Use
`date -Is` in a crontab, or escape every percent sign as `\%`. A probe that
produces no output is more likely a quoting bug than a dead daemon — check
`journalctl -u cron -n 20` for the `CMD (...)` line, which shows the command
after cron has rewritten it.

