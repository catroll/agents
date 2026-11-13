# A backup function that receives the new payload is not a backup

**Signal.** The rollback artifact exists, has a plausible size, and its contents are
indistinguishable from the live data — because they *are* the live data.

**Cause.** A one-word mistake in the call site: the migration built
`payload = {**old, **{k: v for new values}}`, then passed that same `payload` to
`backup()` and to `write()`. Every test that checked "a file was created" passed.

**Check.** Two rules, both cheap:
1. The backup call takes the **pre-change** value, by name (`backup(original)`), never a
   variable that is also going to be written.
2. A backup is only verified when it has been **restored once**. Here the restore source
   ended up being a real `mysqldump` from an earlier step — parse the dump and compare one
   known key (`qwen3.7-plus` coefficient `0.219178`) against the file you plan to restore.

**Recovery.** `mysqldump --databases` output is a full pre-image: the old option row was
still inside a dump taken 25 minutes earlier. Parsing it needs a quote-aware scanner, not
a regex — `INSERT ... VALUES (...)` contains `;` and `),(` inside string literals, so a
non-greedy `.*?;` silently matches nothing. Walk characters, track the string state, and
stop at the first `;` **outside** quotes.

**And.** SQLite accepts DDL that MySQL rejects (`PRIMARY KEY` inline *and* table-level →
`ERROR 1068 Multiple primary key defined`). A local SQLite rehearsal cannot validate a
MySQL `CREATE TABLE`; run the DDL against the target engine once, in a scratch database,
before the maintenance window.

