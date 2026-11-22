# `sqlite3 live.db ".restore backup.db"` exits 0 and leaves an empty database

## Symptom

A backup script produced `backup/data.db` (1.8 MB, tables present). A restore
script ran `sqlite3 backup/data.db ".restore target/data.db"`, exited 0, and
`target/data.db` was 4 KB with no tables. A later `sqlite3 target/data.db "select
count(*) from users"` failed with `Error: in prepare, no such table: users`. The
same run had also **truncated the backup source**, so rerunning the restore could
not recover it.

## Cause

The sqlite3 CLI's `.restore` expects a different image format from a plain
database file; given a database it does not copy it, and it opens the argument
read-write. The exit status is 0, so `set -e` does not catch it.

## Fix

The `.backup` output is already a consistent database image. Restore it by
copying the file (`install -m 0644 "$SRC/data.db" "$DATA_DIR/data.db"`) and then
verify with `PRAGMA integrity_check` **and** a table read
(`sqlite3 "$DATA_DIR/data.db" "select count(*) from users"`). Never point
`.restore` at the only copy of a backup.

## Check

Any restore drill must assert on real rows, not just the exit status:
`sqlite3 restored/data.db "select count(*) from users"` returning a number. A
drill that only checks the command exited 0 will pass on an empty database.
