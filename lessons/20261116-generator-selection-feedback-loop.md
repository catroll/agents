# A generator deletes its own output because annotating feeds back into selection

**Signal.** A generator that selects work from a derived ledger writes 113 files,
a later annotate step marks those rows covered, and the *next* run writes only 93
and **deletes the 20 files it wrote last time**. Nothing errors; the file count
just shrinks. In this case `services/coder/generated/AuroraSendCloud/*Matrix*.yaml`
went 102 → 93 after an annotate, and the ledger rows those cases had covered
flipped back to uncovered, so a re-annotate reverted them.

**Cause.** The selection predicate read `tested.{comply,violate}` from
`constraints.yaml`, and `python -m constraints annotate` recomputes those flags
from the DSL directory the generator writes into. Output → ledger → selection →
output is a loop with no fixed point: every run removes what the previous run
proved. The deletion was correct behaviour of "remove files no longer selected";
the predicate was wrong.

**Check.** Two rules, both cheap:

1. A generator's selection must **exclude evidence produced by the generator
   itself**. Here the annotator tags generated evidence (`file [declared]`), and
   the selector ignores a side whose `tested_by` list consists only of those
   markers. In general: mark generated artifacts at the boundary and filter them
   out when reading the derived state they feed.
2. Prove stability: run `--emit` twice in a row and assert
   `written₂ == written₁ and removed₂ == []`. A single run cannot show this;
   only the second run can. A regeneration pipeline that is not idempotent is
   not safe to schedule.

**Also recorded (same class of mistake).** The generated cleanup steps inherited
the base case's teardown assertions, which assert deletion of a resource the
mutated (rejected) request never created — three failed assertions per case,
non-blocking but noisy. Rule: a teardown for an operation whose side effect did
not happen must not assert the effect. Keep the step, strip the assertions, and
run it best-effort.

Seen 2026-11-16 while adding the constraint-matrix emitter
(`scripts/coder/constraint_matrix.py`).
