# A history rewrite drops untracked files that the old commits still contain

2026-11-20, `git-filter-repo` a40bce548d2c, repo `~/Projects/StdEnv/scripts`
(557 commits, two branches).

## Signal

Before rewriting, `otp_backup.json` and `otp_backup.txt` had been removed from
the index in a commit and added to `.gitignore`; the files stayed on disk and
`git status` was clean. After

    git filter-repo --force --invert-paths \
      --path freeotp/otp_backup.json --path freeotp/otp_backup.txt \
      --replace-text expressions.txt

both files were gone from the working tree. Recovering them from the old
commit failed too:

    $ git show 03049e4:freeotp/otp_backup.json
    fatal: 无效的对象名 '03049e4'。

filter-repo had already repacked and pruned every object the rewrite no longer
references, so the old blob was unreachable both locally and through refs.

## Why

A rewrite checks out the filtered commit set. A path that exists in the old
history but not in any new commit is removed from the index and, as part of
resetting the working tree, from disk - even when it was untracked at the
moment the rewrite started. The same run then garbage-collects the old
objects, so "I still have it in the object store" is false by the time you
notice.

## Action

Before any history rewrite:

1. `git bundle create <dir>/<repo>-before.bundle --all` (the bundle is the
   rollback and the only remaining copy of the old objects).
2. Copy every working-tree file that must survive outside the repository.
3. Prove the copy: `git cat-file -p <old-commit>:<path> | cmp - <copy>` before
   starting, since after the rewrite that command no longer works.

Restore with a plain `cp` afterwards, and re-check the copy against the bundle:
`git -C <tmp> fetch <bundle> <ref>` then `git cat-file -p <commit>:<path>`.

## Negative results

- `git reset --hard` / untracked status do not protect the file; it was already
  untracked and ignored.
- Keeping the old commit hash in a variable is useless: the hash itself stops
  resolving after filter-repo's cleanup.
- The pre-rewrite bundle from step 1 was the only successful recovery path; the
  freshly dumped copy matched `otp_backup.json` byte for byte, which is how the
  restore was verified.
