# `COMPOSE_PROJECT_NAME` in a shared `.env` overrides the compose file's `name:`

**Signal.** After deploying an unrelated stack, a container is gone or a
different container answers on its port. `docker inspect` shows
`com.docker.compose.project=woody` even though the compose file declares
`name: authd`; `docker compose -f infra.yml up -d --remove-orphans` is what
removed it.

**Cause.** `COMPOSE_PROJECT_NAME` in the shared `.env` takes precedence over the
top-level `name:`. Both compose files therefore belong to one project, so
`--remove-orphans` on the infra file treats the auth service as an orphan and
deletes it. The container had previously been created from a compose file with a
different project, which hid the collision.

**Check.**

- Resolve the effective project, not the YAML: `docker inspect <c> --format
  '{{index .Config.Labels "com.docker.compose.project"}}'`, or `docker compose ls`.
- Pin each stack explicitly at every call site (`docker compose -p <project> -f …`),
  including the remote/deploy wrapper; a top-level `name:` is not enough when a
  shared `.env` sets `COMPOSE_PROJECT_NAME`.
- Before running `up --remove-orphans`, list what it would consider orphaned
  (`docker compose -f <file> ps --orphans` where supported, or compare the
  project's containers with the file's services first).
