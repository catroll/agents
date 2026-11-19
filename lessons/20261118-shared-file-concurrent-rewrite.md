# A shared index file edited by two sessions can gain duplicate rows; a global replace then deletes all of them

**Signal.** `~/.agents/todo/_INDEX.md` showed the same project twice after one
insert — the project row had been added by another session between the read and
the write. The cleanup used `s.replace(row_with_newline, "")`, which removes
**every** matching line, so both rows vanished and the index briefly had none:

```text
| Winnie | ... |
| WoodyCoder | ... |
| Staticize | ... |          <- Homepage row gone entirely
```

**Check.** For any file shared across sessions (`_INDEX.md`, a weekly note, a
release list):

```sh
grep -c '^| <Project> |' path     # must be exactly 1 after the edit
```

and re-read the file immediately before the write instead of reusing the copy
read at the start of the turn.

**Fix pattern.** Insert with a unique anchor (the table header line) and
replace with a single, targeted `str.replace(..., 1)`; when removing a
duplicate, remove the *specific* occurrence (line index or `splitlines()`), not
by value with a global replace. If the file gained a row you did not add, keep
theirs and only correct the count.

**Negative result.** `make <target>` reporting `Nothing to be done` right after
adding a recipe to the Makefile also means the edit did not land (the file had
no trailing newline, so the anchored replace was a no-op); `make help` is the
cheap confirmation.
