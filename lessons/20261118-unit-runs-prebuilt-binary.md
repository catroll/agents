# Restarting a unit that runs a prebuilt binary does not deploy the code change

Symptom: the Go service was edited (a new proxy-identity middleware), its YAML
config was updated, `systemctl --user restart tinyapi` succeeded, and the new
behaviour was simply absent — requests still took the old path (303 to /login
instead of 200 from Remote-User). No error, no log line about the feature.

Cause: `ExecStart` points at a build artifact (`.../tinyapi`), not `go run`.
Restart re-executes the same old file; `go build ./...` during development only
compiles into the build cache, it does not replace the binary the unit runs.

Checks: read `systemctl show <unit> -p ExecStart` and compare the artifact's
mtime with the edited source; rebuild explicitly (`go build -trimpath -o
<artifact> .`, or the project's `make build`) and restart. Verify by behaviour
(the new request path returning what only the new code can return), not by
"the unit is active".

The same trap applies to any embedded or generated artifact: templates with
`go:embed`, frontend bundles, vendored scripts. Restart only re-runs what is on
disk at the path the unit names.
