# WoodyCoder (woody) — TODO

> Project: ~/Projects/Mine/WLB/tools/woody (coder service + constraint matrix)
> Docs: docs/coder/coverage-roadmap.md, docs/coder/constraint-matrix.md
> Prefix: W
> Next ID: W-016
> Updated: 2026-11-19

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
  - 2026-11-19 preview: the mail now goes only to kwicoo, with a distinct
    `[Matrix]` subject, amber header and a "matrix only" banner (commits
    `45202434b`, `5e4c5f874`). Sent one real case
    (`matrix_preview_20261119_2155`, subject
    `[Matrix] AuroraSendCloud weekly constraint matrix — 2026-11-19: 1/1 passed
    (100.0%)`) to kwicoo; the scheduler was restarted and task definitions
    validate. The full 11-23 08:00 mail is still the acceptance check.
  - Done when: the 08:00 mail for the 11-23 run lists the same totals and has no
    failed-case section; if the format is wrong, fix `send_latest_batch_report`.
  - Ev: report dir under `.cache/reports-matrix`.

### Batch B20261125-w2c2 — close the remaining coverage gap (target 2026-11-25, open)

- [x] **W-004** [P1][B20261125-w2c2] W2c-2: id-based create cleanup
  - Done 2026-11-19: id families keep the base extract + teardown with the
    documented `skip_if_empty` guard (comply sides only; a violated create never
    extracts). Also fixed dynamic pinned messages (dates → `exists`) and skipped
    `testhook.local` bases. Suite ran twice green (181/133/70) and the resource
    snapshot is identical before/after both runs. Commit `61de25daa`.
- [x] **W-005** [P1][B20261125-w2c2][dep:W-004] Re-measure coverage and decide the
  acceptance target
  - Done 2026-11-19: measured 42.1/41.8/21.2 and decided **continue** with the
    auth axis + array/relational mutators (batch B20261202), with a 50% checkpoint
    before renegotiating 60/60/35. Recorded in `coverage-roadmap.md` (W-005 record).
- [x] **W-006** [P2][B20261125-w2c2] Extend the pattern/format sample tables
  - Done 2026-11-19: counterexamples for the lookahead-domain, `^[A-Za-z0-9_]+$`
    and email patterns; accepted-invalid pattern sides recorded as observations.
    Remaining unsampled form is `pem` only (W-008 → deferred, W-015).
- [x] **W-007** [P2][B20261125-w2c2] Add the W4 send-subset quota preflight
  - Done 2026-11-19: `remaining_send_quota()` reads ASC/SC get-account-info and
    ENG get-account-quota; emit aborts fail-closed below `send_limit + 50`.
    Evidence: ASC 2000 / SC 4117 / ENG 5897; abort path exits with need=9050.
    (`woody` commit `coder: check remaining send quota before an opt-in send run`).
- [-] **W-008** [P3][B20261125-w2c2] `pem` format comply sample
  - Deferred 2026-11-19: no disposable valid PEM fixture exists; an invalid PEM
    cannot be trusted to be accepted. Fold into W-015 if a fixture appears.
- [x] **W-009** [P2][B-backlog] Re-probe the accepted-violation observations
  - Done 2026-11-19: `--recheck-observations` re-probes recorded sides and drops
    the ones now rejected (ASC 2, SC 1, ENG 0); new cases emitted and green.
    Commit `ce1b932b5`.
- [x] **W-010** [P3][B-backlog] Decide the ignore rule for
  `scripts/coder/check/work/` run artifacts
  - Done 2026-11-19: README already promised gitignore, but 88 files stayed
    tracked; they were untracked (kept on disk) and the path is in `.gitignore`.
    Evidence: `git status` clean for woody; commit `chore(coder): untrack
    scripts/coder/check/work run artifacts`.
- [ ] **W-011** [P2][B-backlog][user] Push `dev` (4 commits ahead of
  `origin/dev` as of 2026-11-19 22:15)
  - Why: the agent never pushes; the commits include W2b/W2c and the lessons.
  - Done when: `git status -sb` shows `dev...origin/dev` level.

### Batch B20261202-coverage — auth axis and relational mutators (target 2026-12-02, open)

- [ ] **W-012** [P1][B20261202-coverage] Auth axis: credential constraints and
  `auth_identity` comply cases
  - Scope: `apiUser`/`apiKey` required/minLength/maxLength/pattern (present,
    short, invalid) and `auth_identity` valid-credential cases; check whether
    `tls_required` has a reliable http/https distinction.
  - Done when: probe→emit→run twice green, the secret gate stays clean, and the
    core delta is recorded.
- [ ] **W-013** [P1][B20261202-coverage] Array/relational mutators
  - Scope: `separator` (wrong separator / missing separator), `ref_exists`
    (dangling id), `uniqueItems` (duplicate items), `maxItems` (over limit),
    `items.format` / `items.maxLength`.
  - Done when: each mutator has a unit check against a base and the generated
    cases run green.
- [ ] **W-014** [P2][B20261202-coverage][dep:W-012,W-013] Coverage checkpoint
  - Done when: core is re-measured after both levers; if ASC is under 50%, the
    60/60/35 target is renegotiated in `coverage-roadmap.md` §5 with the reason.
- [ ] **W-015** [P3][B20261202-coverage] `pem` sample or permanent skip record
  - Done when: a disposable valid PEM fixture is accepted, or the skip is written
    down as permanent (currently skipped).
