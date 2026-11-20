# Go service conventions

Reached from `~/.agents/AGENTS.md` (section "Go services"), loaded on
demand. Update here, not in AGENTS.md.

## HTTP framework: Gin

- Use `github.com/gin-gonic/gin` for HTTP services.
- Prefer `gin.New()` over `gin.Default()` so middleware is explicit; add
  `gin.Recovery()` plus a structured request logger yourself.
- Register routes on explicit groups; session/auth middleware before anything
  that reads the session.

## Configuration: YAML

Config lives in a YAML file, not flags alone; ship an annotated
`<app>.example.yaml` with every key and its default. Precedence, low to high:
built-in defaults < YAML file < environment variables < CLI flags.

- `-config` flag plus an environment-variable equivalent, defaulting to a
  conventional path (e.g. `pocketadmin.yaml`). Missing at the default path is
  fine; missing at an explicitly requested path is an error.
- `KnownFields(true)`, so a typo fails at startup.
- Pointer fields, so absent differs from `false`/`0`.
- No hard-coded secrets: generate-and-persist (`0600`) or require them from the
  environment.

## Logging: log/slog with JSON on stdout

- Standard library `log/slog` only — no `log`, no `fmt.Println` for operational
  output, no third-party logger.
- `slog.NewJSONHandler(os.Stdout, ...)`: one JSON object per line;
  `slog.SetDefault` before anything else runs, so startup failures are JSON too.
- One request-log middleware entry per request (method, path, status, latency,
  client IP, bytes): 5xx → `error`, 4xx → `warn`, else `info`.
- Level (`debug|info|warn|error`) and format (`json|text`) configurable; JSON
  default.

