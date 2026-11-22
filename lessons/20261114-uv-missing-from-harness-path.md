# `uv: 未找到命令` in the agent shell — PATH lacks `~/.local/bin`

The DSH `bash` tool runs with
`PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin`
— no `~/.local/bin`. `uv` on this machine is a pipx symlink at
`~/.local/bin/uv` → `~/.local/share/pipx/venvs/uv/bin/uv`, so any repo whose
Makefile does `UV ?= uv` (staticize, others) fails with `uv: 未找到命令` from
the agent shell even though the user's interactive shell works.

Check, don't reinstall:

```sh
command -v uv || ls -l ~/.local/bin/uv
```

For a one-shot build, bypass `make` or prepend the directory for that command
only:

```sh
cd /home/catroll/Projects/Mine/staticize
.venv/bin/python main.py generate          # project venv already exists
PATH="$HOME/.local/bin:$PATH" make generate
```

Do not `pip install uv` into another location and do not move the binary: the
missing PATH entry belongs to the tool environment, and the installed one is
already correct.

## Same class: `bun: 未找到命令` (2026-11-21)

The agent shell also lacks `~/.bun/bin`, so `bun` from the harness PATH reports
`bun: 未找到命令` although `~/.bun/bin/bun` is installed. The repo's installed
bun is 1.4.2, which has no `bun check`; `web/package.json`'s `typecheck`
(`bun check -b`) needs 1.4.4, the version CI pins.

```sh
export PATH="$HOME/.bun/bin:$PATH"           # 1.4.2: scripts, tests, i18n:sync work
/tmp/bun144/node_modules/.bin/bun check -b   # 1.4.4: only for typecheck
# install once:
mkdir -p /tmp/bun144 && cd /tmp/bun144 && npm init -y &&
  npm install --registry=https://registry.npmmirror.com bun@1.4.4
```

Do not `bun upgrade` the user's install to get `bun check`; a temporary 1.4.4
under `/tmp` is enough and leaves the machine's 1.4.2 untouched.
