# Two runs of the same analysis disagree (989 vs 967) with no code change

**Signal.** A selection/report script is run twice in the same session and
prints different totals; the diff of the script is empty. Numbers already
written into a design doc no longer reproduce. In this case the candidate count
went 989 → 967 and one target's "blocked by name" count halved between runs.

**Cause.** The input was a **generated** file and something regenerated it
between the runs. Here `apis/{Target}/constraints.yaml` is produced by
`python -m constraints pipeline`, which recomputes the `tested` flags from the
current DSL directory; another session ran the pipeline at 09:44, flipping rows
from `comply: false` to `true`, so those rows stopped being candidates. `git
status` stayed clean because the regenerated content happened to be identical to
HEAD — mtime changed, content did not, so the diff was invisible.

**Check.** Fingerprint the input as part of the report, not as an afterthought:

```python
raw = path.read_bytes()
{"path": path, "sha256": hashlib.sha256(raw).hexdigest()[:16],
 "mtime": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")}
```

`stat` alone is not enough — mtime moved while content did not, and the reverse
(identical mtime, different content) breaks coarse-resolution filesystems. Keep
the hash. Print both next to the counts, and when comparing two reports, compare
the fingerprints first: different fingerprint means the numbers are not
comparable, full stop.

**Generalisable.** An analysis over a generated artifact is only valid for the
artifact version it read. Any number quoted in a doc, a review, or a decision
must carry the input identity, or the next reader will "reproduce" it against a
different file and conclude the analysis was wrong. Prefer the generator's own
metadata (`meta.dsl_coverage`, `generated_at`) when it exists; when it does not,
hash the file.

**Also recorded here.** A file another session is editing shows up as ` M` in
`git status` without being yours. Adding your own hunk to it makes the later
commit impossible to stage cleanly (`git add <file>` would take their work too).
Check `git status --porcelain <file>` before editing a shared doc; if it is
already dirty, put your content in a new file and link it, or wait for their
commit. See `second-session-git-add.md` for the staging side of the same
situation.

Seen 2026-11-16 while designing the constraint-matrix generator
(`scripts/coder/constraint_matrix.py`).
