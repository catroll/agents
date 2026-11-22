# A read-only review left `__pycache__/` in the reviewed repo

## Signal

After delegating a read-only review of a shell repository, `git status` showed
`?? __pycache__/email-ipv6.cpython-314.pyc`. The child had imported/compiled a
tracked `.py` file to inspect it, and the repository's `.gitignore` did not
cover Python caches.

## Why it matters

The turn was supposed to leave the worktree untouched. A later `git add -A` would
sweep the artifact into an unrelated commit, and a diff review would mistake it
for user work.

## Procedure

- Start review subagents with `PYTHONDONTWRITEBYTECODE=1` (or tell them to use
  `python3 -B`) whenever they may execute a repository's Python files.
- After any delegated review, run `git status --porcelain` and check the
  worktree yourself before reporting; remove only freshly created, untracked
  artifacts, after confirming their mtime and that they were not there before
  the session.
- When the reviewed repo ships Python, add `__pycache__/` and `*.pyc` to its
  `.gitignore` as part of the findings.

## Negative results

`grep -ril 'PYTHONDONTWRITEBYTECODE\|__pycache__' ~/.agents/lessons` matched only
`20261116-grep-over-cache-dumps.md`, which is unrelated (excluding cache dirs
from grep). No existing lesson covered delegation hygiene.

Date learned: 2026-11-21.
