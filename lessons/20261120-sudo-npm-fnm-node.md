# `sudo npm install -g` ignores fnm and installs under the system Node

**Signature.** An upgrade of a global npm package that needs a newer Node than
the distro's prints

```
npm WARN EBADENGINE   package: '@deepseek-ai/dsh@0.2.2-rc.5',
npm WARN EBADENGINE   required: { node: '>=24.9.0' },
npm WARN EBADENGINE   current: { node: 'v22.22.1', npm: '9.2.0' }
```

and then says `added N packages` — the install "succeeds". The user runs
`fnm` with node v26 as their default, so `node -v` in an interactive shell shows
v26.

**Cause.** `sudo` resets `PATH` to its `secure_path`
(`/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:...`), so the `npm` that
runs is `/usr/bin/npm` with `/usr/bin/node`, not the fnm-managed pair. npm's
global prefix then resolves to `/usr/local`, so two things happen:

- the package lands in `/usr/local/lib/node_modules/...` and runs under the old
  Node (EBADENGINE only warns; failures surface later);
- a service whose `ExecStart` names the fnm installation's binary keeps the old
  version — the upgrade did nothing for it.

**Check before installing.**

```sh
node -v                 # the version you intend
which -a npm            # first hit must be the fnm installation
npm prefix -g           # must be the fnm version dir, not /usr
```

If `npm prefix -g` prints `/usr`, npm was invoked through its shebang with the
system Node (`#!/usr/bin/env node` plus a PATH without fnm). Put the target
Node's `bin` first, or call npm's CLI with that node explicitly:

```sh
FNM="$HOME/.local/share/fnm/node-versions/v26.13.1/installation"
PATH="$FNM/bin:$PATH" npm install -g @deepseek-ai/dsh@0.2.2-rc.5
```

**Safer swap.** Install to a staging prefix, verify, then move the package
directory into place so the live tree is never half-written:

```sh
STAGE=$(mktemp -d)
PATH="$FNM/bin:$PATH" npm install -g --prefix "$STAGE" @deepseek-ai/dsh@0.2.2-rc.5
"$FNM/bin/node" "$STAGE/lib/node_modules/@deepseek-ai/dsh/lib/bin.js" --version
NM="$FNM/lib/node_modules/@deepseek-ai"
mv "$NM/dsh" "$NM/dsh-previous.bak"
mv "$STAGE/lib/node_modules/@deepseek-ai/dsh" "$NM/dsh"
```

The `bin/<name>` symlink uses a relative target, so it keeps working after the
move.

**Also.** Remove the root-owned duplicate afterwards with
`sudo npm uninstall -g <pkg>` (the same system npm that installed it), otherwise
`sudo <pkg>` and shells without fnm still pick up the old-Node copy. A restart of
the consuming service is required: a running process keeps the previous code in
memory, and `--version` from a fresh process proves only the on-disk copy.

Negative result: `npm view` worked through `/usr/bin/node` v22 too, so a
successful metadata query does not prove the right Node is in effect.