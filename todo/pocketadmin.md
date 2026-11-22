# PocketAdmin (pocketadmin) — TODO

> Project: ~/Projects/Mine/pocketadmin
> Docs: docs/README.md, docs/admin-platform/90-porting/remediation-plan.md, docs/decisions.md
> Prefix: PA
> Next ID: PA-014
> Updated: 2026-11-21

Development is complete by decision D-079 follow-up: the contract was written,
the divergences were fixed, and the delivery plan is closed. State on 2026-11-21:
the 74-entry plan and every open question are done, the defect page is empty,
`make test`, `make build` and `make vet` are green, and the binary has been served live
through the deployment drill. New work starts from a new item ID.

On 2026-11-20 the open defects were numbered into an execution order:
`docs/admin-platform/90-porting/remediation-plan.md` § Per-entry work list,
#1–#69, followed by the five operational findings #70–#74. The order was
confirmed on 2026-11-20 and is being executed from #1 (D-41 closed in commit
c1ad00b). Each unit is one commit that closes the ids it names.

## Theme: defect convergence

### Batch B20261120-remediation — resume the remediation plan (target TBD, open)

- [x] **PA-001** [P1][B20261120-remediation] Phase A remainder: false assurance and
  fail-open authority (D-39; D-14, D-22, D-25, D-26, D-41 and D-46 closed
  2026-11-20; D-72 is Phase F) -> done 2026-11-20 (Phase A empty; commits c1ad00b,
  8364cc0, 9c32800, 4fe4457, 1ac19f0, 1e2ff92, 7b673d5; D-1/D-2/D-27 closed
  earlier)
  - Done when: the named entries are deleted from `known-defects.md` and the
    Phase A table in `remediation-plan.md` is empty
  - Ev: docs/admin-platform/90-porting/remediation-plan.md § Phase A
  - D-41 done 2026-11-20: per-request forced-enrolment gate, MFA disable refused
    while required, two inert keys removed (D-083); commit c1ad00b
  - D-25 done 2026-11-20: absent data scope denies, role form refuses a missing or
    unknown scope; commit 8364cc0
  - D-26 done 2026-11-20: rbac.CheckCatalogue runs in server.New and names the
    drift; commit 9c32800
  - D-14 done 2026-11-20: "actor" joins the scope owner fields, so a self scope
    narrows security_audit_logs; commit 4fe4457
  - D-22 done 2026-11-20: authenticated downloads send Cache-Control: no-store;
    commit 1ac19f0
  - D-46 done 2026-11-20: provider save split into create (/save) and update
    (/save/:id) routes, id read from the path only; commit 1e2ff92
  - D-39 done 2026-11-20: preferences are self-service; the unused point is gone
    and migration 1700000220 prunes it from old databases; commit 7b673d5
- [x] **PA-002** [P1][B20261120-remediation] Phase B: money under concurrency
  (D-66, D-67, D-48, D-50, D-49, D-51, D-42, D-68) -> done 2026-11-21 (all eight
  closed; commits 04cbf1c, 1456d63, 71ebd79, f962652, f92eed5, f917955, 85e8f19,
  2e1f071, b13441b, 679a2dd, 360ac78)
  - D-66 part 1/3 done 2026-11-20: idempotency keys on 8 money routes (order
    create, manual payment, intent, reconcile, refund request/execute,
    subscription, coupon issue); commit 04cbf1c
  - D-66 part 2/3 done 2026-11-20: orders/refunds/subscriptions apply the data
    scope, refunds key on requestedBy, subscriptions paginate; commit 1456d63
  - D-66 part 3a done 2026-11-20: record version (428/412) on lifecycle actions,
    generic resource edits and provider edits; commit 71ebd79
  - D-66 done 2026-11-20: settings group, coupon and membership versions added;
    the entry is closed (commits 04cbf1c, 1456d63, 71ebd79, f962652). Next in
    PA-002: D-67.
  - D-67 done 2026-11-21: CreateIntent reads the order and refuses an amount above
    the outstanding balance inside the transaction; manual payments inherit it;
    commit f92eed5.
  - D-48 done 2026-11-21: order creation evaluates and redeems coupon grants
    through the promotion engine in one transaction; commit f917955.
  - D-50 done 2026-11-21: evaluation refuses a coupon whose campaign is not
    active or outside its window; commit 85e8f19.
  - D-49 done 2026-11-21: issuance limits and the insert are one transaction;
    10 concurrent claims against a 5-grant coupon issue 5; commit 2e1f071.
  - D-51 done 2026-11-21: public code is the first grant's claim token, later
    grants mint `<code>-<random>`; order resolution claims/reuses; commit b13441b.
  - D-42 done 2026-11-21: MakeDefault is one transaction; migration 240 adds a
    partial unique index on (type) where isDefault = true; commit 679a2dd.
  - D-68 done 2026-11-21: ApplyResult.Duplicate distinguishes a first failure
    (recorded) from a replay (duplicate); commit 360ac78.
  - Done when: idempotency key, balance check, one discount evaluator and the
    default-provider transaction are in place and driven live
  - Ev: docs/admin-platform/90-porting/remediation-plan.md § Phase B
- [x] **PA-003** [P1][B20261120-remediation] Phase C: subscription and membership
  lifecycle (D-60, D-61, D-62, D-65, D-69, D-70, D-71, D-64)
  - D-60 part 1/3 done 2026-11-21: every cycle raises one order (Start/Renew in one
    transaction); commit 572ee16.
  - D-60 part 2/3 done 2026-11-21: a paid order settles the cycle paid/active; a
    closed unpaid order moves it failed/past_due with a retry; commit 058ebbc.
  - D-60/61/62 done 2026-11-21: dunning retries past_due against the existing
    order, the order-expiry task skips subscription orders, cancellation at
    period end opens no cycle, paused cancellations are ended; commit ceae576.
  - D-65 done 2026-11-21: Resume refuses an expired subscription without touching
    the row; commit ccc60c1.
  - D-69 done 2026-11-21: Extend refuses a non-positive duration and a perpetual
    membership, leaving the row untouched; commit d7fd43f.
  - D-70 done 2026-11-21: a paid order grants its membership-plan lines and records
    the order; commit e8ef927.
  - D-71 done 2026-11-21: tier deletion counts every membership, not only active;
    commit aa8b309. Phase C complete: D-64 closed with the Phase F guard (commit c4ed603).
  - Done when: one order per billing cycle is raised, dunning retries
    `past_due`, and cancellation at period end is honoured
  - Ev: docs/admin-platform/90-porting/remediation-plan.md § Phase C
- [x] **PA-004** [P2][B20261120-remediation] Phase D: scheduler (D-33, D-32,
  D-34, D-31, D-35) -> done 2026-11-21 (all five closed; commits b3bb9ac,
  75b2372, 0c45c56, aa4de5b, c6b13f2)
  - D-33 done 2026-11-21: task panics are contained and startup reconciles dead
    runs; commit b3bb9ac.
  - D-32 done 2026-11-21: store evaluates cron in site.timezone (UTC fallback) and
    the console renders in that zone; commit 75b2372.
  - D-34 done 2026-11-21: ValidatePolicy plus runtime clamping; absent form fields
    keep stored policy; commit 0c45c56.
  - D-31 done 2026-11-21: failed/timeout/cancelled runs notify active admins once
    via workbench; commit aa4de5b.
  - D-35 done 2026-11-21: RetryRun removed; trigger enum narrowed to cron/manual;
    commit c6b13f2.
  - Done when: a panicking run is recovered and reconciled, cron is evaluated in
    the configured zone, and retry/trigger values are enforced or removed
  - Ev: docs/admin-platform/90-porting/remediation-plan.md § Phase D
- [x] **PA-005** [P2][B20261120-remediation] Phase E: audit layer (D-11, D-12,
  D-13, D-15, D-23, D-52, D-53, D-63, D-9) -> done 2026-11-21 (all nine closed;
  commits e5ab474, 2a4dad7, 3f5f569, 551c48c, 6904a27, ce198f6, a0927cf,
  7414121, 05bb04f)
  - D-11 done 2026-11-21: operation log writes isSuperuser/impersonator/target;
    exception resolution fields removed with decision D-086; commit e5ab474.
  - D-12 done 2026-11-21: every 5xx is recorded once at the recovery boundary, with
    the handler's detail; commit 2a4dad7.
  - D-13 done 2026-11-21: both guards write permission_denied; export_generated
    removed from catalogue and stored enum; commit 3f5f569.
  - D-15 done 2026-11-21: result success/failed/refused, severity low/medium/high,
    surface console/product, login requestId; migration 280; commit 551c48c.
  - D-23 done 2026-11-21: operation action is `<resource>.<action>` derived from
    the route pattern; commit 6904a27.
  - D-52 done 2026-11-21: coupon void records voidedBy/voidedAt and emits
    coupon_voided; coupon/announcement deletes write only the operation entry;
    commit ce198f6.
  - D-53 done 2026-11-21: machine purge emits data_purged, not data_exported;
    commit a0927cf.
  - D-63 done 2026-11-21: subscription lifecycle transitions write no security
    event; plan save keeps settings_changed; plan delete only operation log;
    commit 7414121.
  - D-9 done 2026-11-21: export refuses above 50k, applies the data scope and
    writes data_exported; commit 05bb04f.
  - Done when: record fields are populated or removed, every unhandled failure is
    recorded, and one attribute vocabulary is in force
  - Ev: docs/admin-platform/90-porting/remediation-plan.md § Phase E
- [x] **PA-006** [P2][B20261120-remediation] Phase F: shared mechanisms — reference
  guard, generic resource layer, settings engine, stored-object reclamation
  -> done 2026-11-21 (D-72 closed; commits d40d4d3, 342dbfd, d84c941, e20cd12,
  0e5ed6a, 365fc75, c4ed603, fd43f6b, 3a07e29, 3af6850, 746e121, 32a6fcb,
  528557f, fc9b9ee, 074ff5e, e912245, 1505e61, 05b9171, 9862832)
  - D-3, D-19, D-64 done 2026-11-21: schema-derived reference guard covers every
    relation (multi through `.id ?=`); commit d40d4d3.
  - D-38 done 2026-11-21: attach operation writes an attachment, recomputes the
    count, references screen has the form; commit 528557f.
  - D-43 done 2026-11-21: provider delete refuses while a setting, file or payment
    names it; commit fc9b9ee.
  - D-4 done 2026-11-21: generic delete soft-deletes collections with deletedAt;
    commit 342dbfd.
  - D-6 done 2026-11-21: a supplied derived/managed field is refused with 400;
    commit d84c941.
  - D-10 done 2026-11-21: an unknown sort field or direction answers 400, no
    silent fallback; commit e20cd12.
  - D-17 done 2026-11-21: releasing unique fields (dept/position/employee/role
    code, user email/phone, profile account) scoped to live rows; commit 0e5ed6a.
  - D-58 done 2026-11-21: slugs/SKUs deliberately reserved; decision D-087 and a
    regression test; commit 365fc75.
  - D-5 done 2026-11-21: undeclared settings keys refused by Engine.Save and the
    console handler before any write; commit c4ed603.
  - D-7 done 2026-11-21: settings group validated fully then written in one
    transaction; audit detail carries old/new; commit fd43f6b.
  - D-8 done 2026-11-21: settings reads fail closed (error/500, getters panic);
    no default fallback; commit 3a07e29.
  - D-29 done 2026-11-21: a product write splitting site.currency and
    commerce.defaultCurrency is refused; commit 3af6850.
  - D-30 done 2026-11-21: refundWindowDays description states zero closes the
    window; commit 746e121.
  - D-36 done 2026-11-21: null clears nullable keys (row deleted, default read) and
    is refused on numbers/booleans; commit 32a6fcb.
  - D-37 done 2026-11-21: sign-in method set declared ["password"]; unknown, empty,
    duplicate and non-array values refused; commit 7a2b695.
  - D-44 done 2026-11-21: null clears a provider credential; console clear checkbox;
    commit e94400e.
  - Startup fixes 2026-11-21: migration 310 prunes undeclared permissions; jobStore
    recursion fixed; live run served on 127.0.0.1:8090; commit b774bf9.
  - D-72 done 2026-11-21: console branding/banner wired, notification removed,
    refund window enforced, logo/favicon and feature/maintenance groups removed
    (commits 6ba39b5, 074ff5e, e912245, 1505e61). D-20 (05b9171) and D-21 (9862832)
    close Phase F.
  - Done when: each shared cause in the plan's cluster table is closed and its
    instance entries are deleted
  - Ev: docs/admin-platform/90-porting/remediation-plan.md § Phase F
- [x] **PA-007** [P3][B20261120-remediation] Phase G: remaining consistency entries
  -> done 2026-11-21 (D-16/18/24/28/40/45/47/54/55/56/57/59 closed; commits 7d7cfa3, fbc1f70, a1d94f0, 7818de4, ba53bbd, 53d5937, 445975a, a9efd8f, b5393d1, 69688f4, c4a9ef8, f4f4732)
## Theme: documentation and delivery surface

### Batch B20261120-docs-run — make the docs match the build, then decide deployment (target TBD, open)

- [x] **PA-008** [P1][B20261120-docs-run] Top-level README and `docs/README.md` are
  -> done 2026-11-21 (implemented surface listed, Go 1.27, contract review closed; commit 48c1504)
- [x] **PA-009** [P2][B20261120-docs-run] `docs/operations.md` is stale: it says
  -> done 2026-11-21 (endpoints, layout, security, verification; commit ee27e2e)
- [x] **PA-010** [P2][B20261120-docs-run] Deployment is not landed: the repository
  -> done 2026-11-21 (unit/proxy/config, backup+restore scripts, runbook; live drill served /healthz and /login on 18090/18091; commit 3acc5b9)
- [x] **PA-011** [P3][B20261120-docs-run] Settle the open questions that change the
  -> done 2026-11-21 (D-090..D-093; commit 9764fb6)
- [x] **PA-012** [P2][B20261120-docs-run] The concurrency model is undocumented:
  -> done 2026-11-21 (operations.md "Concurrency and the single writer"; commit 64c7c51)
- [x] **PA-013** [P1][B20261120-docs-run] The single-process model is assumed but
  -> done 2026-11-21 (exclusive flock on <dataDir>/pocketadmin.lock; second instance and subcommands refused; commit f946007)
