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
