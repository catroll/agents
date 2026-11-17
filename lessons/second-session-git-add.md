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

**Staging explicit paths is not enough.** `git commit` commits the whole
index, so a concurrent session's `git add -A` (or `git rm`) that lands between
your `git status` and your `git commit` rides along unseen — 2026-11-17 a commit
whose message described one doc change also deleted another session's six
`20261117-traffic-report/*` files, and the `--stat` output was the only tell.
Before committing in a shared tree, read `git diff --cached --name-status` and
compare it with your own list; if a foreign path is staged, leave it staged but
commit with `git commit -- <your paths>` (pathspec commit) or reset it out of
the index first. Verify after: `git show --name-status --format= HEAD` must list
exactly your files. To repair such a commit, `git reset --mixed HEAD~1` keeps
every worktree edit, so the other session's deletions stay deleted and only
need re-staging; do not `git checkout` their files back.
