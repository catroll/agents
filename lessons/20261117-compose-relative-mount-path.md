# A compose file's relative volumes change meaning when the file moves

**Signal.** A freshly recreated container crash-loops with

```text
panic: read /init_data.json: is a directory
```

while `ls` on the host path in the repo looks correct.

**Cause.** The compose file mounted `./config/casdoor/init_data.json`, but the
deployed tree has `conf/casdoor/init_data.json`. Docker bind mounts create a
**directory** when the source path is missing, so the container received a
directory where a file was expected. This went unnoticed because the stack had
been created from an older compose file in a subdirectory
(`compose/auth/docker-compose.yml` with `../../conf/...`), and the deploy had
switched to the root-level `auth.yml` since.

**Check.**

- Before recreating a container from a different compose file, diff the volume
  sources against the deploy root: `docker compose -f <file> config | grep -A1 source`,
  then `test -f` every source.
- After `up`, assert the real mounts instead of trusting the YAML:
  `docker inspect <c> --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}'`
  and read the first 20 log lines; a panic on a file read is the tell.
- A missing bind-mount source is not an error to Docker. Treat an empty
  directory appearing at a config path as a mount bug, not as an app bug.
