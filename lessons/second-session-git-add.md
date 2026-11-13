# A second agent session in the same working tree can commit your files

**Signal.** Files you edited minutes ago show up inside another commit's diff;
`git status` flips between two unrelated change sets; commits describing a
different feature carry your hunks. A shared CSS or i18n file is the usual
victim.

**Cause.** Two agent sessions share one checkout. When either runs
`git add -A` / `git add .`, it sweeps in whatever the other session has in
flight — including unfinished edits and deletions.

**Fix.** In a shared worktree, stage explicit paths only (`git add <paths>`),
never `git add -A`; review `git diff --cached --name-only` against your own file
list before committing; commit small, verified slices early instead of leaving a
large dirty tree; for a long independent task, work in a separate worktree or
branch (`create_worktree`). Put what belongs to the change set in the commit
body, because the file list may later prove incomplete.
