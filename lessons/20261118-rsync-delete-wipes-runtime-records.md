# rsync --delete of a tool directory wipes its runtime records

## Signal

After deploying with

```bash
rsync -a --delete harden/ root@host:/opt/ubuntu-harden/
```

`/opt/ubuntu-harden/harden.sh report` prints `ERROR: no run found`, and the
`records/` directory on the host is empty. The previous apply's `backup_*`
files and `changes.tsv` are gone — exactly what `rollback` needs.

## Cause

The tool writes per-run state (records + backups) under `<tool>/records/`.
The local source tree did not contain that directory (the records had been
copied back into the repo's work directory), so `--delete` removed the host's
copy.

## Fix and check

```bash
rsync -a --delete --exclude 'records/' harden/ root@host:/opt/ubuntu-harden/
```

Keep a second copy of `records/` outside the deployed tool directory, and when
restoring, push it back before running `report` or `rollback`:

```bash
rsync -a work/.../records/ root@host:/opt/ubuntu-harden/records/
```

Rule: any `rsync --delete` of a tool/application directory must list its
runtime state directories (`records/`, `data/`, `var/`) in `--exclude`,
because those exist only on the target.
