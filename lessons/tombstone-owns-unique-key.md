# A unique key that includes tombstones is not insert-only

**Signal.** A build that had worked for weeks dies with
`IntegrityError: UNIQUE constraint failed: docs.root_id, docs.rel_path`
right after a file was deleted and something reappeared at its path.

**Cause.** The table soft-deletes (`state='deleted'` tombstones) but the unique
index does not exclude them. The sweep's "existing rows" query filtered
`state != 'deleted'`, so its diff saw no row at that path and took the `INSERT`
branch — while the tombstone still owned the key. The same filter made a
**rename**'s `UPDATE ... SET rel_path=?` collide when it moved a live row onto a
tombstoned path. Both failures abort the whole build, so one delete-then-restore
made the index permanently unbuildable.

**Check.** Ask the catalog before touching the code: "is there a row for this
exact key in *any* state?"

```sql
SELECT id, state FROM docs WHERE root_id = ? AND rel_path = ?;
SELECT rel_path FROM docs WHERE state = 'deleted';  -- compare with the disk
```

A tombstone whose file exists again is the whole diagnosis.

**Fix.** Load every row for the key, tombstones included, and give the tombstone
a resurrection path that resets the state and redoes the derived work (here:
clear `state` so the "text unchanged, skip re-chunk" shortcut cannot fire, then
rebuild chunks that were purged on delete). Constrain renames to keys that are
provably free. Skip already-deleted rows in the deletion pass, or every sweep
re-counts and re-stamps the same tombstones.

**Do not** paper over it with `INSERT ... ON CONFLICT DO UPDATE`: the row it
overwrites has lost its derived rows, and any state-keyed shortcut will happily
leave it marked "indexed" with nothing behind it.

**Generalisable.** A soft-delete is an ownership claim on the uniqueness key.
Every writer must treat the tombstone as the incumbent and update it in place;
"absent from the live diff" does not mean "the key is free".

