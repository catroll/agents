# An `ImportError` for a name that is in the file means the process is older than its source

**Signal.** A long-running Python service answers a request with a bare 500, and
the traceback ends:

```
ImportError: cannot import name 'article_source_url' from
'markjour.utils.article' (/path/markjour/utils/article.py)
```

The import is at the top of a file pulled in **lazily inside the request**
(`from markjour.scripts.articles import do_new`). The name *is* in the target
file, and a fresh interpreter imports it without error.

**Cause.** The service was started before the file changed (here: process
start `12:00:27`, refactor written `12:13`), and it has no reloader
(`ADMIN_DEBUG=0`, gunicorn/uwsgi without `--reload`). Interpreter module objects
are frozen at import, but a lazy import still reads the **new** file off disk.
That mixes a fresh module with old in-memory dependencies: the *file* has the
re-export, the *loaded* module does not.

**Two checks that are decisive and cheap.**

```bash
ps -eo pid,lstart,args | grep '<service invocation>'   # start time
find admin markjour -name '*.py' -newer <the pid's start time>   # edited after start
```

and re-run the failing import in a fresh interpreter (same venv, same
`sys.path`). If that succeeds, the code is fine and the process is stale —
restart and re-test the real HTTP request. Do not "fix" the module.

**Fix without sudo.** When the service is owned by a root supervisor and
`supervisorctl` needs an unreachable password, the child usually runs as the
normal user: `kill -TERM <pid>` and `autorestart=true` brings up a fresh process.
Confirm with a new start time in the log, not just a listening port.

**Why a banner beats a note.** This recurs (three incidents in this repo:
2026-10-14, 2026-10-30, 2026-11-03), because the reminder lives in docs nobody
reads while operating the panel. Make the process compare the newest source
mtime with its own start time and say so **where the operator is looking** —
a page banner plus a startup log line with `pid=… started=… newest_source=…`,
which is also what a later diagnosis greps for.

**Generalisable.** "The file says X but the object does not have X" is a
statement about process age, not about code. A lazy import makes the discovery
happen at request time and disguises it as a 500.

