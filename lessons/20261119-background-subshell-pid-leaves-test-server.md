# `kill "$(cat app.pid)"` leaves the test server running; the browser measures the old build

**Signal.** A UI test still observes the *previous* behaviour after the fix —
in this case the served page still had `target="_blank"` after the template was
changed and the binary rebuilt. The next start logs:

```
wlb-homepage: listen on 127.0.0.1:18080: bind: address already in use
```

and `ss -ltnp 'sport = :18080'` shows an older `wlb-homepage` pid that the
cleanup step claimed to have stopped.

**Cause.** The instance was started as

```sh
cd /tmp/app && bin --config config.yaml > app.log 2>&1 & echo $! > app.pid
```

`cmd1 && cmd2 &` is one background **subshell**; `$!` is that subshell's pid.
Killing it does not take the binary child with it (no signal propagation), so
the old process keeps the port and serves the old embedded assets.

**Check.**

```sh
ss -ltnp 'sport = :18080'          # real listener, not the pid you recorded
strings bin/app | grep -c '<new marker>'   # binary changed?
```

Assert a marker that only the new build has **on the served page** before driving
the browser:

```sh
curl -s http://127.0.0.1:18080/ | grep -c 'target="_blank"'   # 0 means new build
```

**Fix in the harness.** Start with an exec so `$!` is the binary, or kill the
listener by pid:

```sh
( cd /tmp/app && exec bin --config config.yaml ) > app.log 2>&1 & echo $! > app.pid
```

Cleanup then uses that pid, but treat `ss -ltnp` as the source of truth when
the port matters.

**Negative result.** `strings` on the rebuilt binary showed the old marker was
gone, so the code was fine; the false failure came entirely from the stale
process. A browser assertion failing "right after" a rebuild should first prove
which process answered the request.

**Variant: a failed second start overwrites the pid file.** Starting again while
the old process is alive logs `bind: address already in use` and exits, but the
launcher still writes its pid. `kill "$(cat app.pid)"` then hits a dead process,
and the old server keeps the port. Worse, if the SQLite file was deleted and
recreated during the "restart", the old process still holds the *unlinked* old
inode and serves stale rows while the new file passes checks. Check the real
listener and, when data looks stale, the open file:

```sh
ss -ltnp 'sport = :8791'
ls -l /proc/<pid>/fd | grep -E 'keyops.db|\(deleted\)'
```

Stop by listener pid, verify the port is free, then start; assert the new pid is
the listener before trusting the pid file. `make status` / `make stop` now
resolve the listener rather than a recorded pid.
