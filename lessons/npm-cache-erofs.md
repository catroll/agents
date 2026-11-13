# npm needs a workspace cache on this machine

**Signal.** `npm view`, `npm install` or `npm pack` fails before doing network
work, with a path under `$HOME`:

```
npm ERR! code EROFS
npm ERR! syscall open
npm ERR! path /home/catroll/.npm/_cacache/tmp/94b7f0d3
npm ERR! errno -30
```

**Cause.** `$HOME` is read-only in this environment (the same reason the uv
cache lives in the checkout). npm's default cache is `~/.npm`, and it fails on
the first temp-file write, so an empty `npm view` result is not a registry or
network failure.

**Fix.** Point the cache inside the checkout for that command, or export it for
the shell:

```bash
export npm_config_cache="$PWD/.cache/npm"
npm install --no-audit --no-fund
npm config get cache        # confirms the override
```

Keep the directory gitignored (`/.cache/`). Do not change `$HOME` permissions;
it is not yours to change and the sandbox will refuse.

