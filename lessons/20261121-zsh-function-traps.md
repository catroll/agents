# zsh traps inside sourced shell functions

## Signals

- `local path=/some/file` in a zsh function makes `path` the array form of
  `PATH`; `git`, `python3` and everything else vanish inside that function.
- `local status=...` aborts with `read-only variable: status` (zsh ties
  `status` to `$?`).
- A function defined in an interactive zsh after `alias mv='mv -vi'` has the
  alias baked into its body: a bare `mv` inside the function prompts for
  overwrite (`mv: 是否覆盖 ...？`).
- `jobs` / `jobs -p` inside `$(...)` or a pipeline see an empty job table in
  zsh, and zsh's `jobs -p` prints the full listing, not plain PIDs.
- `git switch --track <branch> <remote>/<branch>` is rejected with
  `fatal: 缺少分支名`; use `git branch --track <branch> <remote>/<branch>`.

## Procedure

- Do not use `path`, `status`, `history`, `commands` or `options` as local
  names; use `target`, `st`, etc.
- Use `command mv` / `command cp` inside functions, or unalias before the
  definition, when the alias changes behaviour.
- Dump the job list to a file in the current shell (`jobs -l >"$tmp"`), parse
  the PID column for zsh, then kill/wait each PID.
- Test every new helper in both `zsh -f -c 'source …'` and
  `bash --norc -c 'source …'`; aliases created by the sourced file cannot be
  called in the same `-c` string (it is parsed first) — wrap the call in
  `eval`.

## Negative results

`grep -rnE 'local +(path|status|commands|options|history)=' --include='*.sh'`
after the fix found no remaining occurrences in this repository.
