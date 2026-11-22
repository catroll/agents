# WoodyCoder (woody) — TODO

> Project: ~/Projects/Mine/WLB/tools/woody (coder service + constraint matrix)
> Docs: docs/coder/coverage-roadmap.md, docs/coder/constraint-matrix.md
> Prefix: W
> Next ID: W-021
> Updated: 2026-11-21

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

### Batch B20261202-coverage — auth axis and relational mutators (target 2026-12-02, ON HOLD)

> Hold 2026-11-20 (user decision): do not start W-012/W-013 until the online
> matrix execution shipped 2026-11-19 is observed clean. Resume criteria:
> three daily batches (00:10/02:10/04:10) with zero matrix failures, the
> 11-23 weekly run + 08:00 report clean, and `matrix-manifest` 0 issues.

- [ ] **W-012** [P1][B20261202-coverage] Auth axis: credential constraints and
  `auth_identity` comply cases
  - Step 0 (pilot, 11-20..11-22): prove the engine semantics — a step
    `params.apiUser` overrides config (ASC/SC), `api_auth: none` yields a real
    missing credential, ENG needs an explicit invalid `Authorization` header.
    Then 30–40 candidates: required-present, required-missing, short/invalid.
  - Full pass only if the violate pilot rejects; credentials only via env
    references, never literals. Gate: probe→emit→run twice green, secret gate
    clean, measured core delta recorded.
- [ ] **W-013** [P1][B20261202-coverage] Array/relational mutators
  - Operator table first (where the array is, what the separator is, which id
    is a reference), then one unit check per mutator against a real base:
    `separator`, `ref_exists`, `uniqueItems`, `maxItems`, `items.format`,
    `items.maxLength`. Gate: unit check per mutator passes and generated cases
    run green twice.
- [ ] **W-014** [P2][B20261202-coverage][dep:W-012,W-013] Coverage checkpoint
  - Done when: core is re-measured after both levers; if ASC is under 50%, the
    60/60/35 target is renegotiated in `coverage-roadmap.md` §5 with the reason.
- [ ] **W-015** [P3][B20261202-coverage] `pem` sample or permanent skip record
  - Done when: a disposable valid PEM fixture is accepted, or the skip is written
    down as permanent (currently skipped).

- [ ] **W-016** [P2][B20261202-coverage] Value-axis reachability audit
  - Why: the value bucket shows +189 ASC "both" potential but most single-side
    rows are unpursuable (`minLength=1` empty==omitted, create-violate has no
    id to clean by, no base, accepted observations).
  - Done when: each class is counted with evidence and either a documented
    exclusion or a renegotiation decision is recorded in `coverage-roadmap.md`.
- [ ] **W-017** [P3][B20261202-coverage] Paid-send expansion (optional)
  - Scope: raise the opt-in send subset toward the ≤20/run cap; metadata-only
    violations; quota preflight must pass; abort on the first successful send
    and record it as an observation.
  - Done when: a capped run adds send-op codes without a successful delivery
    beyond the recorded one, or the lever is rejected with the reason written.

### Batch B20261120-engagelab-fixes — product SSRF feedback + 256 title limit (done 2026-11-20)

- [x] **W-018** [P1][B20261120-engagelab-fixes] Fix the Engagelab webhook
  fixtures and the calendar-title boundary after the product team confirmed the
  webhook `30710` is intentional SSRF protection.
  - Done 2026-11-20: 20 `generated/Engagelab/*webhook*.yaml` files moved from
    `.testhook.local` / `*.local` to
    `https://nexus.d3v.cn/woodyhook/webhook/eng-*` (long-URL cases padded to stay
    < 1024); case 1240 now sends a 257-char title (docs say max 256). Notes record
    that the fix report was wrong about 15910-15912 asserting 200 (they assert
    400) and about 8306 needing a status change (it already asserts 401).
  - Ev: `python -m dslcheck references|field-order|descriptions` on the 21 edited
    YAML files (`done: all ... OK`); `grep -rn '\.local' generated/Engagelab`
    empty; commit 3b5995e21.
- [x] **W-019** [P2][B20261120-engagelab-fixes] Rebuild the update-webhook URL
  matrix cases on the measured 1023/1024 boundary
  - Why: `61de25daa` deleted `update-webhook_Exception_Url_ExceedsMaxLengthMatrix`
    (15911) and `..._InvalidFormatMatrix` (15912) when the base still used
    `testhook.local`; the base is fixed now, but 15911's sample is 2049 `a`
    chars with no scheme, so it only proves `30706` (format), not a length limit.
  - Measured 2026-11-20 (details in `notes/create-webhook.md`): max accepted
    1023; 1024 rejected with create `30710` / update `30712`; >1024 -> `30716`.
    The ledger still says 2048. The 256-char title boundary is also confirmed
    (256 accepted, 257 -> `30835`; sandbox does validate).
  - Progress 2026-11-20: `constraint_matrix.mutate()` now emits a scheme-bearing
    URL for `url`/`newurl` maxLength; the ledger cap is 1024 for create/update
    webhook; `update-webhook_Exception_Url_ExceedsMaxLengthMatrix` (15911,
    1025 -> 30716) and `..._InvalidFormatMatrix` (15912) are restored; new
    `..._Url_ExceedsMaxLengthAt1024` (15914, 1024 -> 30712; 15913 is the
    orphaned first name) and
    `send-calendar-email_Boundary_TitleLength_Max256` (1241, 256 -> 200) are
    added; the success boundary in the long-URL case is 1023. Offline checks,
    case numbers and `matrix-manifest` (0 issues) pass.
  - Done 2026-11-21: batch `20261121_041000_87844dc5_batch` ran 1414/1414
    green (0 failed) with the deployed files matching `07bee6b34`; 15911 ->
    400/30716, 15912 -> 400/30706, 15914 -> 400/30712, 1241 -> 200 sandbox,
    1240 -> 400/30835. The remaining create-webhook length case moved to W-020.
- [ ] **W-020** [P3][B20261120-engagelab-fixes] Add a create-webhook URL
  length violation case
  - Why: create accepts 1023 and rejects 1024 with `30710`, >1024 with `30716`;
    `CREATE_WEBHOOK_URL_MAXLENGTH.tested.violate` is still false.
  - Done when: a create case asserts 1024 -> `30710` (or 1025 -> `30716`), runs
    green, and the ledger marks the side tested.
