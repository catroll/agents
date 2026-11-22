# A doc-edit script that writes at the end loses every edit when one anchor misses

**Signal.** A chained edit script printed `scope row: 0` after several successful
`sub()` calls; none of that file's edits landed, while a separate `write_text`
earlier in the same script (the defect-page deletion) was already on disk.

**Cause.** Each `sub` mutates an in-memory string and only the final
`write_text` persists. One wrong anchor — the text drifted in an earlier round —
aborts the whole script. Edits to other files written before the failure are
already committed to disk, so the tree is half-edited.

**Check and fix.** Grep the exact current line before scripting
(`grep -n "<first words>" file`), update the anchor, and re-run the remaining
edits. Prefer one script per file, or write each file immediately after its own
edits. After a failed run, inspect `git status`/`git diff`: do not assume the
script changed nothing.
