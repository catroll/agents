# WoodyCoder (woody) — TODO

> Project: ~/Projects/Mine/WLB/tools/woody (coder service + constraint matrix)
> Docs: docs/coder/coverage-roadmap.md, docs/coder/constraint-matrix.md
> Prefix: W
> Next ID: W-012
> Updated: 2026-11-18

## Theme: constraint matrix (docs/coder/coverage-roadmap.md)

### Batch B20261123-scheduled-run — verify the weekly automation (target 2026-11-23, open)

- [ ] **W-001** [P0][B20261123-scheduled-run][due:2026-11-23] Verify the first
  scheduled matrix run on sctest
  - Done when: `/opt/woodycoder/.cache/reports-matrix/matrix_<ts>/report.json`
    exists after 2026-11-23 06:05, the per-target totals match the file counts
    (182/126/69; batch 173/119/68), the 08:00 report mail arrives, and the
    08:30 jobs digest is `matrix-manifest ok`.
  - Ev: `ssh sctest "ls -dt /opt/woodycoder/.cache/reports-matrix/matrix_* | head -3"`
    and the run's `meta.json`.
- [ ] **W-002** [P0][B20261123-scheduled-run][due:2026-11-30] Close Step 0's
  two-Monday acceptance gate
  - Done when: the 11-23 and 11-30 scheduled runs are both green; the roadmap
    Step 0 record is marked done with the two run ids.
- [ ] **W-003** [P2][B20261123-scheduled-run] Smoke the weekly matrix report mail
  - Done when: the 08:00 mail for the 11-23 run lists the same totals and has no
    failed-case section; if the format is wrong, fix `send_latest_batch_report`.
  - Ev: report dir under `.cache/reports-matrix`.

### Batch B20261125-w2c2 — close the remaining coverage gap (target 2026-11-25, open)

- [ ] **W-004** [P1][B20261125-w2c2] W2c-2: id-based create cleanup
  - Scope: label, tracking-domain, address-list, api-user, inbound-route and
    ENG template/webhook; extract the created id from the create response
    (`extract` path from the response), delete by it in teardown, add the family
    to `CLEANUP_MAP`/`CLEANUP_TARGETS`.
  - Done when: the family runs twice in a row with no leaked resource and no
    state-dependent failure; `matrix_manifest` still 0 issues.
- [ ] **W-005** [P1][B20261125-w2c2][dep:W-004] Re-measure coverage and decide the
  acceptance target
  - Done when: core shape/validation is re-measured (currently 41.4/40.6/21.0 vs
    the 60/60/35 gate); either continue with a concrete next lever, or
    renegotiate the target in `coverage-roadmap.md` §5 with the reason recorded.
- [ ] **W-006** [P2][B20261125-w2c2] Extend the pattern/format sample tables
  - Done when: a dry-run shows the remaining unsampled forms; new samples are
    regex-validated and the `no-sample` count is <10 per target (or each
    remaining one has a written reason).
- [ ] **W-007** [P2][B20261125-w2c2] Add the W4 send-subset quota preflight
  - Done when: `--allow-send` checks remaining daily quota before the run and
    aborts with a clear reason below the threshold (today it is manual).
- [ ] **W-008** [P3][B20261125-w2c2] `pem` format comply sample
  - Done when: either a disposable valid PEM fixture exists and is accepted, or
    the skip is documented as permanent (current state: skipped).

### Batch B-backlog — unplanned (open)

- [ ] **W-009** [P2][B-backlog] Re-probe the accepted-violation observations
  - Why: the platform may start enforcing a constraint recorded as accepted.
    Current observation counts are 39/27/41 (ASC/SC/ENG).
  - Done when: a probe pass re-checks them and the observations file is updated
    (drop entries that now reject, keep the rest).
- [ ] **W-010** [P3][B-backlog] Decide the ignore rule for
  `scripts/coder/check/work/` run artifacts
  - Why: every case-number check leaves an untracked run directory, so
    `git status` is never clean.
  - Done when: `check/work/` is either gitignored or the checker writes under
    `.cache/`.
- [ ] **W-011** [P2][B-backlog][user] Push `dev` (6 commits ahead of
  `origin/dev` as of 2026-11-18)
  - Why: the agent never pushes; the commits include W2b/W2c and the lessons.
  - Done when: `git status -sb` shows `dev...origin/dev` level.
