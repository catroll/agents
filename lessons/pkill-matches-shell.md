# `pkill -f <pattern>` kills the shell you are typing it in

**Signal.** A bash call dies mid-script with `[killed by signal: SIGTERM]` and no
output from the rest of the command. Nothing is wrong with the target process.

**Cause.** `bash -c '<command>'` puts the whole command line in
`/proc/<pid>/cmdline`, so `pkill -f` matches the invoking shell whenever the
pattern appears anywhere in that command — including inside the pkill argument
itself, a heredoc, an echo, or a `python3 -c` snippet in the same call. The
bracket trick (`[/]tmp/x.py`) only defeats shells that exclude their own pid by
matching the literal text; it does not help when the *same literal string* is
elsewhere in the command line, which it usually is.

**What works.** Kill by pid (`pgrep -f pattern` in one call, `kill <pid>` in the
next), or make the pattern unable to appear in the command:
`P="fake_$(printf smtp)"; pkill -f "$P"`. Check with `ss -ltnp`/`ps -eo pid,args`
before assuming an orphan is still holding the port.

**The same trap reaches `pgrep` when the pipeline is in one call.** A cleanup
written as `pgrep -f 'remote-debugging-port 9222' | while read pid; do kill
"$pid"; done; rm -f preview.tsx` matched the shell running it (that shell's
argv *is* the pattern) and killed the shell, so the `rm` never ran: the call
reported `[killed by signal: SIGTERM]` and silently left two temporary files in
the tree. The "two calls" rule above is not optional, and the damaging part is
the abandoned work after the kill, not the signal.

A single-call form that does work excludes itself by a token only the target
lacks: `ps -eo pid,args | awk '/snap.firefox.*--headless/ && !/awk/ {print $1}'`.
The shell's own line contains `awk`, so the filter drops it. Either way, verify
the cleanup in a *separate* call — `test ! -e <file>` — rather than trusting a
step that follows a kill in the same command.

**Related trap.** A port can report `EADDRINUSE` from `bind()`
while `ss -ltn` shows no listener and only TIME-WAIT connections remain;
`SO_REUSEADDR` did not clear it here (`127.0.0.1:2526`), and the same bind
succeeded immediately on `2537`. Move to another port instead of debugging the
old one.

