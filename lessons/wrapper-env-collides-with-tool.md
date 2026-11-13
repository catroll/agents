# A wrapper's own config name that matches the tool's env var is not namespaced

**Signal.** The notification arrived with the topic name glued to the front of
the body:

```
title:   New API 新版本 v1.0.0-rc.99
message: woodynotice-selftest 上游新发布 1 个版本 tag：\nv1.0.0-rc.99
```

The shell called `ntfy publish --title T --tags ... "$target" "$body"`, and the
same run exported `NTFY_TOPIC=woodynotice-selftest` for the wrapper script.

**Cause.** The ntfy CLI reads `NTFY_TOPIC` (documented: `NTFY_TOPIC=mytopic ntfy
publish "some message"`). When it is set, the topic comes from the environment
and **every positional argument becomes the message** — including the topic the
caller passed. The wrapper had chosen `NTFY_TOPIC` as the name of its own config
variable, so the value leaked into the tool's namespace and duplicated itself.

**Fix.** Name wrapper config after the wrapper, not after the tool:
`WATCH_TOPIC` / `WATCH_SERVER`. And `unset NTFY_TOPIC NTFY_TITLE NTFY_TAGS ...`
before invoking the CLI, so a stray exported value cannot silently rewrite the
title, tags or priority that the code just built.

**Why the test missed it.** The first test publish did not export the variable,
so the message was clean; only the tagged path, run with the variable in the
environment, reproduced it. **A publish path is not verified by the publish that
does not use the same environment as production.** Send the real message once
with the real env, then read it back from the server
(`curl "https://ntfy.sh/<topic>/json?poll=1"`) instead of trusting exit 0 — an
exit code says the RPC arrived, not that the payload is right.

