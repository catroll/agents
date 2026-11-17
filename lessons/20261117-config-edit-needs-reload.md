# A config edit is not live until the daemon reloads it

**Signal.** I added `exclude: [Sync]` to `~/.config/winnie-index/config.yaml`, ran
`winnie-index scan` by hand, and it reported `"deleted": 63`. Minutes later the
catalog still showed those 63 documents as `state='indexed'`, and the sensitive
file I had just purged was back. The scan was correct; the systemd daemon had
been running since before the edit, held the old config in memory, and its own
5-minute sweep resurrected every tombstone with the excluded tree still in scope.

**Rule.** After editing a file a long-running process reads at startup, restart
that process and assert the new behaviour on the *data*, not on the command that
reads the file:

```bash
systemctl --user restart winnie-index
# assert the policy, not the config text:
sqlite3 ~/.local/share/winnie-index/catalog.sqlite \
  "select state, count(*) from docs where rel_path like 'Sync/%' group by state;"
```

Never conclude "the config is applied" from `load_config()` in a one-shot CLI or
from `cat` of the file. Both see the new value; only the process that matters may
not.

**Which path reloads and which does not.** In winnie-index the console's
`PUT /admin/config` reloads in place; a hand edit takes effect on the next
restart (`systemctl --user restart winnie-index`). Check the daemon's own docs
before assuming either behaviour.

**Negative result worth keeping.** A sweep that reports `deleted: N` proves the
walk skipped those paths *for that process*. If another process (or the same one
under an older config) still walks them, the rows come back. Verify the end
state, not the report.

**Same trap.** `env-var-is-process-not-file` (environment at start), and any
edit to a unit file needs `systemctl daemon-reload` plus a restart to take
effect.