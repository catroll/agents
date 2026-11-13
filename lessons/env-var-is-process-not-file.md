# A missing env var blames the process, not the `.env` file

**Signal.** A service fails with `RuntimeError: ... API key is missing; set FOO`,
even though `FOO=...` is present in the `.env` you just edited.

**Cause.** Environment variables are captured when the process is exec'd. A
running server keeps the old environment; `uvicorn --reload` watches `*.py`, not
`.env`, so a reload never happens for a config-only edit. `make api` sources
`.env` in the shell that starts uvicorn — editing the file afterwards changes
nothing until that shell runs again.

**Check.** Ask the process directly, without printing the value:

```bash
grep -c '^FOO=' apps/api/.env          # 0 means the file has no key
pid=$(pgrep -f 'uvicorn.*8000' | head -1)
tr '\0' '\n' < /proc/$pid/environ | grep -c '^FOO='   # 0 means the process has no key
```

**Fix.** Add the key, then restart the process (a `--reload` will not do it), and
retry the exact operation. Confirm in the service log that the provider call now
runs, rather than assuming a restart fixed it.

**Also.** A `403` from a vendor after a correct key is an entitlement problem
(`code=45000030`), not a missing or wrong key — do not conflate the two.

