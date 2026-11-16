# An overseas host timing out from the agent shell is a missing proxy, not a dead mirror

**Signal.** A fetch or dependency install that goes to a foreign host stalls and
ends in one of:

- `curl: (28) Operation timed out after N milliseconds` with exit code 28
- `dial tcp [2404:6800:4012:2::2011]:443: connect: connection timed out`
  (Go, to `proxy.golang.org`)
- `npm`/`pip` sitting with no progress output

and `env | grep -i proxy` in the harness shell prints nothing (`exit=1`). Every
`bash` tool call is a fresh shell, so a proxy exported in one call is gone in
the next.

**Rule.** Before reaching for a mirror or concluding the host is down, put the
proxy into the *same* command that needs it:

```bash
bash -c 'source ~/.proxyrc; <command>'
```

`~/.proxyrc` exports `http_proxy`/`https_proxy`/`HTTP_PROXY`/`HTTPS_PROXY` as
`http://127.0.0.1:10809/` (xray HTTP inbound) and
`ftp_proxy`/`all_proxy` as `socks5h://127.0.0.1:10808/` (SOCKS inbound). Confirm
the listeners are up with `ss -ltnp | grep -E ':(10808|10809)\b'`; both are
owned by `xray`.

Prefixing one command (`https_proxy=… cmd`) works too, but sourcing is simpler
and picks up `all_proxy` for tools that only read that.

**Measured on this host, 2026-11-15.**

| Target | Direct | Via proxy |
| --- | --- | --- |
| `codeload.github.com/git/git/tar.gz` (11.4 MB) | 628 KB/s, cut off at 8 s with 5.0 MB | 5.2 MB/s, complete in ~2 s |
| `https://developer.android.com/` | `curl` exit 28 at 8 s | 200 in 2.1 s |
| `https://proxy.golang.org/…/@v/list` | `curl` exit 28 | 200 |
| `go mod download github.com/gin-gonic/gin@v1.11.0` | fails, IPv6 to 2404:6800… times out | exit 0, module cached |
| `https://pypi.org/simple/` | 2.9 MB/s, reachable | not needed |
| `npm view express version` | works (registry reachable) | not needed |

So the proxy is not a blanket requirement: `registry.npmjs.org` and `pypi.org`
answer directly from here. Reach for it when a *specific* host times out, and
say which host it was.

**Related.** A slow-but-working GitHub download is
`lessons/github-release-slow-truncated.md`; the proxy is the fix there too —
retry the same asset through it before declaring a 25 KB/s ceiling.

**Caveats found while verifying.**

- The `no_proxy=localhost,127.0.0.0/8,…` line in `~/.proxyrc` is a plain
  assignment, not an `export`, so child processes never receive it. `env` inside
  `bash -c 'source ~/.proxyrc; …'` shows no `no_proxy`. Loopback and
  `192.168.1.38` stayed reachable through the HTTP inbound anyway in this test,
  but if a LAN URL ever breaks when the proxy is sourced, add
  `export no_proxy=…` in the same command.
- Go honours `HTTPS_PROXY` directly. If npm ignores the exported variables, add
  `npm_config_proxy`/`npm_config_https_proxy` set to the same URL.
- Nothing here is persistent: do not add the exports to `~/.bashrc` as a fix;
  source per command so a broken xray does not break every shell.
