# A uvicorn reloader can keep the port with a dead child

**Signal.** `ss -ltnp` still shows the port listening and `ps` still shows the
reloader, but `curl -m 5 http://127.0.0.1:8000/healthz` returns no bytes after
the timeout. There is no traceback in the service log because the process that
would print it is gone.

**Cause.** A reload child crashed while importing a newly added editable
package. The reloader did not replace it; the parent stayed in its sleep loop
and kept the listening socket. The port is open, so a supervisor or a naive
health check sees a listener, but no request is served.

**Check the process tree, not only the port:**

```bash
ps -eo pid,ppid,stat,wchan:20,args | grep -E 'uvicorn|<defunct>'
```

A `<defunct>` child under the uvicorn pid plus a listening parent means a dead
app. To separate "code is broken" from "reloader is stale", start the same app
with the same config in a one-off process on another port and read its stderr.
If that starts, the code is fine and the reloader is the problem.

**Fix.** Install the new package, stop the server, and start it again (without
`--reload` while recovering). Verify `/healthz` **and one real route**; a
listener is not evidence that the app works.

**The general bit.** A `--reload` wrapper is not the application. When a port
is open but nothing answers, inspect the child before debugging the framework,
the database or the network.

