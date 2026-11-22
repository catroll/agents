# Commit at the task boundary, before editing shared files again

## What happened

Plan: T4 (vocabulary UI) then T5 (SRS review). T4 passed its browser
check, but instead of committing I started T5 in the same files
(app.js, index.html, style.css). The next commit, intended for T4,
silently carried T5 too; history no longer matched the plan's
one-commit-per-task rule.

Recovery was `git reset --mixed HEAD~1`, strip the T5 blocks to rebuild
the T4 working tree, commit T4, copy the saved T5 files back, commit T5.
It worked, but it is work that a single `git status` would have avoided.

## Check

When a task's acceptance test passes, run `git status --short` before
opening the next task. If the next task touches any of the files still
showing as modified, commit first — the task boundary is the commit
boundary. Starting feature B while feature A is uncommitted guarantees
the next commit mixes them.

## Related

- `~/.dsh/AGENTS.md` Git hygiene: one coherent change per commit,
  inspect first, stage explicit paths.
- When tasks genuinely cannot be split by file (shared refactor), say so
  in the plan and commit them together on purpose instead of by accident.
