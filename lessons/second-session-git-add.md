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

## 2026-11-18: staging synthetic content is twice as fragile

When the shared files already carry another session's WIP, the clean way to
commit only your own work is to stage a **synthetic blob** — `git show
HEAD:path` plus your edits — with `git update-index --cacheinfo`, leaving their
hunks in the worktree. A concurrent `git add` (theirs) replaces that index
entry with their worktree file wholesale: the commit keeps their WIP and drops
your staged content.

The `--cached --stat` immediately before the commit is not enough, because the
replacement can land in the gap. Check the **staged content** and do the commit
in the same shell command:

```sh
git show :path/to/file | grep -c 'renderTraffic'      # your marker > 0
git show :path/to/file | grep -c 'renderMappingAudit' # theirs == 0
git commit -F - <<'MSG'
...
MSG
```

Tell: the pre-commit stat said `252 insertions(+), 2 deletions(-)` but the
resulting commit reported `253 insertions(+), 42 deletions(-)`; afterwards
`git show HEAD:path | grep -c renderTraffic` was 0 while their marker was 95.
Verify `HEAD:path` after every shared-tree commit, not just the file list.

Repair without losing anyone's work: `git reset --mixed HEAD^` (index back to
the previous commit, worktree untouched), then restage the synthetic blobs and
commit again. The other session's changes return to unstaged and stay in the
worktree; never `git checkout` them away. The orphaned commit stays in reflog
only — do not push it.

## 2026-11-18: a path-filtered index check hides the foreign paths

Ran `git diff --cached --stat -- homepage`, saw only my three files, and then
`git commit -F -` **without a pathspec**. The commit carried 10 files: the three
mine plus another session's already-staged `castle/` work (`M `, `MM`, `A`).

The filter answers "are my files staged", not "what is staged". Before a
shared-tree commit, run `git diff --cached --name-status` with **no pathspec**
(or read `git status --porcelain` as a whole: a leading `M `/`A ` means staged).

Then commit by pathspec: `git commit -F - -- <your paths>` records only those
worktree files and leaves the rest of the index untouched — no unstage and
re-stage, so a foreign `MM` entry keeps its staged half exactly as it was.

Repair a commit that already swept foreign staged files without disturbing the
other session:

```sh
git reset --soft HEAD~1                    # HEAD back; index preserved as committed
git restore --staged <your paths>          # only if yours were staged
git commit -F - -- <your paths>            # pathspec commit
```

`git reset --mixed HEAD~1` also works but discards the whole index, so the other
session's `M ` / `A ` staged state is lost; prefer `--soft` here.

## 2026-11-18: replaying a cutover against a tree another session already changed

A rewrite script that asserts the pre-image (`assert s.count(old) == 1`) aborts
when someone already applied the same change. That abort is the guard working,
not a failure: before retrying, check whether the change is already in place —
`grep` the target line and `git log -<n> -- <path>` in the owning repo. If a
concurrent commit already carries the edit, report "already applied" and verify
the result; never force the write or reconstruct the old content to satisfy the
assert.

The same session may also add items/IDs to a shared list (a todo file, an index)
between your read and your write: a duplicate `H-010` appeared because the tail
was not re-read before appending. Re-read the file, insert against a unique
anchor, and grep the ID list (and the `_INDEX` count) afterwards.

If a doc cites a commit hash you did not make, check it before committing the
reference: `git cat-file -t <hash>` can find an object while
`git branch --contains <hash>` is empty — an amended/rebased duplicate. Fix the
reference to the commit that actually holds the work; a dangling hash in a work
record is not searchable later.

## `git commit --amend` targets whoever writes HEAD, not you

Same turn, second form: after committing my change, another session committed
twice to the same repo. My follow-up edit was staged and `git commit --amend
--no-edit` folded it into *their* latest commit, rewriting their message and
history. The tell is `git log -1` right after: the subject is not yours.

Recover: `git reflog -3` gives the pre-amend commit; `git reset --soft <that
sha>` restores their commit with your change still staged, then commit it on top
with your own message. Do not `--hard` (the other session's working tree may be
mid-edit).

Before any `--amend`, run `git log -1 --format='%h %an %s'` and confirm it is
your commit; if another session may be active in the repo, prefer a new commit
over `--amend` entirely.
