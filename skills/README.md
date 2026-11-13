# Skills

Human index of the agent skills in this directory. Each skill is a folder whose `SKILL.md` description is what an agent matches against. This file is not loaded as a skill.

Catalogued 2026-11-13. 137 directories.

## Inventory

| Source | Skills | Role |
| --- | ---: | --- |
| [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | 49 | Marketing, SEO, lifecycle, sales |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 42 | Specs, tickets, review, writing |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 24 | General engineering lifecycle |
| [ibelick/ui-skills](https://github.com/ibelick/ui-skills) | 7 | UI audit and fixes |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 7 | Design systems and visual production |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) | 1 | Finding skills to install |
| agent.qq.com | 1 | Mail via agently-cli |
| Local, not in `.skill-lock.json` | 6 | Notes, schedule, news, logos, repos |

131 entries are pinned in `.skill-lock.json`. These six are on disk only: `local-knowledge`, `raster-to-arcs`, `repotracker`, `tencent-news`, `winnie-schedule`, `wlb-work-notes`. A reinstall from the lock does not restore them. `repotracker` is a symlink to `~/Projects/Mine/WLB/tools/repotracker`.

## Review

Do not remove a source. No upstream pack is a subset of another. Marketing, UI audit, UI production, the general engineering lifecycle, and the issue-tracker workflow are five different jobs. Deleting `addyosmani/agent-skills` would drop security, observability, performance, CI, API design, browser testing, and migration, which the Matt Pocock pack does not contain. Deleting `mattpocock/skills` would drop the writing pipeline, handoff, research, triage, and domain docs, which the Addy pack does not contain.

The real overlap is a handful of skills whose descriptions both match a broad prompt ("add tests", "debug this", "review the branch"). About half of the Matt Pocock pack sets `disable-model-invocation: true`, so those entries are manual aliases and do not compete for automatic selection. `grill-me` and `grill-with-docs` only say "run `grilling`". `to-tickets` is the manual successor of `to-issues`; only `to-issues` is automatic. `design` is a router: it sends brand, tokens, and shadcn work to `brand`, `design-system`, and `ui-styling`, and keeps logo, CIP, and icon work itself. Removing those siblings breaks the router.

One pair is the same document installed twice. `diagnosing-bugs` (updated 2026-08-15) is `diagnose` (2026-05-09) plus secret redaction and a tighter phase-1 gate. Remove `diagnose` and keep `diagnosing-bugs`.

These jobs are implemented twice and both copies are automatic. They are not the same text, so this is a choice, not a dedupe. The Addy copy is a long standalone procedure. The Matt copy is short and assumes `CONTEXT.md`, ADRs, and `setup-matt-pocock-skills`. No `docs/agents/issue-tracker.md` exists under `~/Projects` (checked 2026-11-13), so that setup has not been recorded. The Addy copy works without it. Keep both until that setup exists; if the double match gets in the way, remove the Matt name in the right-hand column, not the whole source.

| Job | Keep (works without the issue tracker) | Also installed, automatic |
| --- | --- | --- |
| Test-first | `test-driven-development` | `tdd` |
| Hard bug | `debugging-and-error-recovery`, and `diagnosing-bugs` for the tight loop | `diagnose` (delete; older copy of `diagnosing-bugs`) |
| Review a diff | `code-review-and-quality` | `code-review` |
| Spec before code | `spec-driven-development` | `to-prd` |
| Split into tasks | `planning-and-task-breakdown` | `to-issues` |
| Stress-test a plan | `interview-me`, `idea-refine` | `grilling` |

UI, pick by what the task is allowed to touch:

| Task | Skill |
| --- | --- |
| Choose styles, palettes, type, and stack-specific UI from local data | `ui-ux-pro-max` |
| Build with shadcn/ui, Radix, and Tailwind | `ui-styling` |
| Production UI rule (accessibility, layout, state) | `frontend-ui-engineering` |
| Edit spacing, type, and hierarchy directly | `baseline-ui` |
| Read-only audit, then a plan for another agent | `improve-ui` |
| Write `DESIGN.md` from the current product, without changing it | `create-design-md` |

Routers, when the task is "which skill?": `ask-matt` (Matt Pocock set), `using-agent-skills` (this directory), `ui-skills-root` (UI pack), `find-skills` (install one that is not here).

## Local tools

Tied to this machine. Six of these are outside the lock file; `agently-mail` is pinned.

| Skill | What it does |
| --- | --- |
| [agently-mail](agently-mail/SKILL.md) | Send, reply, search, and manage mail through agently-cli. |
| [local-knowledge](local-knowledge/SKILL.md) | Search the owner's Markdown notes through the local-knowledge index. |
| [raster-to-arcs](raster-to-arcs/SKILL.md) | Rebuild a raster logo or icon as an SVG of arcs and straight lines, scored by IoU. |
| [repotracker](repotracker/SKILL.md) | Git status and plan progress for every repo under `~/Projects`. |
| [tencent-news](tencent-news/SKILL.md) | News, fact-check, weather, sports fixtures, and gaokao admission data. |
| [winnie-schedule](winnie-schedule/SKILL.md) | Read and edit the weekly schedule files in the WLB work tree. |
| [wlb-work-notes](wlb-work-notes/SKILL.md) | Name and place work notes and reports under WLB `work/`. |

## Discovery

| Skill | What it does |
| --- | --- |
| [find-skills](find-skills/SKILL.md) | Find and install a skill that is not already in this directory. |

## Engineering practice

Source: addyosmani/agent-skills. General lifecycle, no issue-tracker setup required.

| Skill | What it does |
| --- | --- |
| [api-and-interface-design](api-and-interface-design/SKILL.md) | Design stable APIs and the boundaries between modules. |
| [browser-testing-with-devtools](browser-testing-with-devtools/SKILL.md) | Test a page in a real browser through Chrome DevTools. |
| [ci-cd-and-automation](ci-cd-and-automation/SKILL.md) | Set up build, test, and deploy pipelines. |
| [code-review-and-quality](code-review-and-quality/SKILL.md) | Multi-axis review before a change reaches the main branch. |
| [code-simplification](code-simplification/SKILL.md) | Refactor for clarity while leaving behavior unchanged. |
| [context-engineering](context-engineering/SKILL.md) | Set up rules and context for a session or a project. |
| [debugging-and-error-recovery](debugging-and-error-recovery/SKILL.md) | Find the root cause when a test, build, or behavior fails. |
| [deprecation-and-migration](deprecation-and-migration/SKILL.md) | Sunset or migrate an API, feature, or system. |
| [documentation-and-adrs](documentation-and-adrs/SKILL.md) | Record decisions and the context later readers need. |
| [doubt-driven-development](doubt-driven-development/SKILL.md) | Send a non-trivial decision to a fresh-context adversarial review. |
| [frontend-ui-engineering](frontend-ui-engineering/SKILL.md) | Build accessible, production-quality interface code. |
| [git-workflow-and-versioning](git-workflow-and-versioning/SKILL.md) | Branch, commit, version, tag, and write a changelog. |
| [idea-refine](idea-refine/SKILL.md) | Turn a vague idea into a sharp concept before planning. |
| [incremental-implementation](incremental-implementation/SKILL.md) | Land a multi-file change in small steps. |
| [interview-me](interview-me/SKILL.md) | Interview one question at a time until the real intent is clear. |
| [observability-and-instrumentation](observability-and-instrumentation/SKILL.md) | Add logs, metrics, traces, and alerts. |
| [performance-optimization](performance-optimization/SKILL.md) | Fix frontend, backend, query, and database bottlenecks. |
| [planning-and-task-breakdown](planning-and-task-breakdown/SKILL.md) | Break a spec into ordered tasks, including parallel work. |
| [security-and-hardening](security-and-hardening/SKILL.md) | Harden input handling, auth, storage, and third-party calls. |
| [shipping-and-launch](shipping-and-launch/SKILL.md) | Pre-launch checklist, staged rollout, monitoring, and rollback. |
| [source-driven-development](source-driven-development/SKILL.md) | Implement from current official documentation. |
| [spec-driven-development](spec-driven-development/SKILL.md) | Write a spec and a capability map before coding. |
| [test-driven-development](test-driven-development/SKILL.md) | Drive every behavior change with tests. |
| [using-agent-skills](using-agent-skills/SKILL.md) | Decide which installed skill applies to the current task. |

## Specs, tickets, and review

Source: mattpocock/skills. These expect the one-time setup in `setup-matt-pocock-skills` (issue tracker, triage labels, domain docs).

| Skill | What it does |
| --- | --- |
| [ask-matt](ask-matt/SKILL.md) | Router over the skills in this pack. |
| [grill-me](grill-me/SKILL.md) | Interview a plan or design until the weak spots are explicit. |
| [grill-with-docs](grill-with-docs/SKILL.md) | Same interview, writing ADRs and a glossary along the way. |
| [grilling](grilling/SKILL.md) | Stress-test a plan when the user asks to be grilled. |
| [implement](implement/SKILL.md) | Implement from a spec or a set of tickets. |
| [loop-me](loop-me/SKILL.md) | Grill the specs for workflows to build in this workspace. |
| [setup-matt-pocock-skills](setup-matt-pocock-skills/SKILL.md) | One-time setup of the issue tracker, labels, and domain docs. |
| [to-issues](to-issues/SKILL.md) | Split a plan into independently grabable tracer-bullet issues. |
| [to-prd](to-prd/SKILL.md) | Turn the current conversation into a PRD on the issue tracker. |
| [to-questionnaire](to-questionnaire/SKILL.md) | Turn a decision you cannot answer into a questionnaire. |
| [to-spec](to-spec/SKILL.md) | Synthesize the conversation into a spec, with no further interview. |
| [to-tickets](to-tickets/SKILL.md) | Split work into tickets that declare what they block and what blocks them. |
| [triage](triage/SKILL.md) | Move issues and external PRs through triage roles into an agent-ready brief. |
| [wayfinder](wayfinder/SKILL.md) | Map a multi-session effort as decision tickets and resolve them one by one. |

| Skill | What it does |
| --- | --- |
| [code-review](code-review/SKILL.md) | Review a diff on repo standards and on the originating spec, in parallel. |
| [codebase-design](codebase-design/SKILL.md) | Vocabulary for deep modules, seams, and testability. |
| [diagnose](diagnose/SKILL.md) | Reproduce, minimise, hypothesise, instrument, fix, regression-test. |
| [diagnosing-bugs](diagnosing-bugs/SKILL.md) | Same diagnosis loop as `diagnose`. |
| [domain-modeling](domain-modeling/SKILL.md) | Sharpen terminology, `CONTEXT.md`, and ADRs. |
| [git-guardrails-claude-code](git-guardrails-claude-code/SKILL.md) | Claude Code hooks that block destructive git commands. |
| [improve-codebase-architecture](improve-codebase-architecture/SKILL.md) | HTML report of deepening opportunities, then a grill on the one you pick. |
| [migrate-to-shoehorn](migrate-to-shoehorn/SKILL.md) | Replace `as` assertions in tests with `@total-typescript/shoehorn`. |
| [prototype](prototype/SKILL.md) | Throwaway prototype to check a state model or a UI. |
| [resolving-merge-conflicts](resolving-merge-conflicts/SKILL.md) | Finish an in-progress merge or rebase conflict. |
| [setup-pre-commit](setup-pre-commit/SKILL.md) | Husky, lint-staged, typecheck, and tests on commit. |
| [setup-ts-deep-modules](setup-ts-deep-modules/SKILL.md) | dependency-cruiser so each package is reached only through its entry points. |
| [tdd](tdd/SKILL.md) | Test-first features and fixes: red, green, refactor. |
| [zoom-out](zoom-out/SKILL.md) | Step back to how this code fits the larger system. |

## Writing and session handoff

Source: mattpocock/skills. The three `writing-*` skills are stages: fragments (explore), then beats, then shape (exploit).

| Skill | What it does |
| --- | --- |
| [caveman](caveman/SKILL.md) | Compressed replies that drop filler and keep the technical content. |
| [claude-handoff](claude-handoff/SKILL.md) | Hand the conversation to a fresh background agent that continues immediately. |
| [edit-article](edit-article/SKILL.md) | Restructure and tighten an article draft. |
| [handoff](handoff/SKILL.md) | Compact the conversation into a handoff document for another agent. |
| [research](research/SKILL.md) | Investigate a question from primary sources and write the findings into the repo. |
| [scaffold-exercises](scaffold-exercises/SKILL.md) | Scaffold a course section with problems, solutions, and explainers. |
| [teach](teach/SKILL.md) | Teach a concept inside this workspace. |
| [wait-what](wait-what/SKILL.md) | Re-pitch the last message when it did not land. |
| [wizard](wizard/SKILL.md) | Generate a bash wizard for steps only a human can perform. |
| [write-a-skill](write-a-skill/SKILL.md) | Create a new skill with progressive disclosure and bundled resources. |
| [writing-beats](writing-beats/SKILL.md) | Assemble raw material into a journey of beats. |
| [writing-for-agents](writing-for-agents/SKILL.md) | Write skills, `AGENTS.md`, and `CLAUDE.md` so an agent follows them. |
| [writing-fragments](writing-fragments/SKILL.md) | Mine raw fragments before imposing a structure. |
| [writing-shape](writing-shape/SKILL.md) | Shape raw material into an article, paragraph by paragraph. |

## Interface

### Audit and repair

Source: ibelick/ui-skills. `improve-ui` and `create-design-md` do not modify product source.

| Skill | What it does |
| --- | --- |
| [baseline-ui](baseline-ui/SKILL.md) | Clean up spacing, hierarchy, typography, and small layout issues. |
| [create-design-md](create-design-md/SKILL.md) | Write `DESIGN.md` from a repo or a live site. |
| [fixing-accessibility](fixing-accessibility/SKILL.md) | Fix ARIA, keyboard, focus, contrast, and form errors. |
| [fixing-metadata](fixing-metadata/SKILL.md) | Fix titles, canonical URLs, Open Graph, Twitter cards, JSON-LD, and robots. |
| [fixing-motion-performance](fixing-motion-performance/SKILL.md) | Fix animation jank: layout thrash, compositor properties, scroll-linked motion. |
| [improve-ui](improve-ui/SKILL.md) | Read-only audit against the product's own design evidence, then an implementation plan. |
| [ui-skills-root](ui-skills-root/SKILL.md) | Router: pick the smallest UI-skills context before UI work. |

### Design production

Source: nextlevelbuilder/ui-ux-pro-max-skill. `design` overlaps the narrower skills below it.

| Skill | What it does |
| --- | --- |
| [banner-design](banner-design/SKILL.md) | Banners for social, ads, website heroes, and print. |
| [brand](brand/SKILL.md) | Voice, visual identity, messaging, and asset consistency. |
| [design](design/SKILL.md) | Broad pack: identity, tokens, logo, corporate identity, banners, icons, social images. |
| [design-system](design-system/SKILL.md) | Token layers, component specs, and brand-compliant slides. |
| [slides](slides/SKILL.md) | Strategic HTML decks with Chart.js and design tokens. |
| [ui-styling](ui-styling/SKILL.md) | Build UI with shadcn/ui, Radix, and Tailwind, including theme and dark mode. |
| [ui-ux-pro-max](ui-ux-pro-max/SKILL.md) | Searchable local data for styles, palettes, type, charts, and stack-specific UI. |

## Marketing

Source: coreyhaines31/marketingskills. All 49.

### Acquisition and distribution

| Skill | What it does |
| --- | --- |
| [ad-creative](ad-creative/SKILL.md) | Generate and iterate ad headlines, descriptions, and variations. |
| [ads](ads/SKILL.md) | Plan paid campaigns on Google, Meta, LinkedIn, and similar platforms. |
| [ai-seo](ai-seo/SKILL.md) | Optimize content so AI answer engines cite it. |
| [aso](aso/SKILL.md) | Audit and optimize an App Store or Google Play listing. |
| [co-marketing](co-marketing/SKILL.md) | Find partners and plan joint campaigns. |
| [community-marketing](community-marketing/SKILL.md) | Build a community (Discord, Slack, forum) that drives growth. |
| [content-strategy](content-strategy/SKILL.md) | Decide topics, clusters, and an editorial calendar. |
| [directory-submissions](directory-submissions/SKILL.md) | Submit a product to startup, SaaS, and review directories. |
| [influencer-marketing](influencer-marketing/SKILL.md) | Find creators, structure deals, brief them, and measure the return. |
| [programmatic-seo](programmatic-seo/SKILL.md) | Generate many SEO pages from templates and data. |
| [public-relations](public-relations/SKILL.md) | Earned media: press, journalist outreach, and newsjacking. |
| [schema](schema/SKILL.md) | Add and fix schema.org structured data and rich results. |
| [seo-audit](seo-audit/SKILL.md) | Diagnose technical, on-page, and ranking problems. |
| [site-architecture](site-architecture/SKILL.md) | Plan page hierarchy, URLs, navigation, and internal links. |
| [social](social/SKILL.md) | Write, schedule, and triage social content across platforms. |

### Copy and conversion

| Skill | What it does |
| --- | --- |
| [ab-testing](ab-testing/SKILL.md) | Design an experiment: hypothesis, variants, sample size, and duration. |
| [copy-editing](copy-editing/SKILL.md) | Edit or refresh existing marketing copy. |
| [copywriting](copywriting/SKILL.md) | Write marketing copy for landing, pricing, feature, and product pages. |
| [cro](cro/SKILL.md) | Raise conversion on a page or a form. |
| [launch](launch/SKILL.md) | Plan a product or feature launch and the announcement. |
| [offers](offers/SKILL.md) | Design the offer: value stack, guarantee, scarcity, and payment structure. |
| [onboarding](onboarding/SKILL.md) | Improve activation, first-run, and time-to-value after signup. |
| [paywalls](paywalls/SKILL.md) | Design upgrade screens, upsells, and feature gates. |
| [popups](popups/SKILL.md) | Optimize popups, overlays, and exit-intent capture. |
| [pricing](pricing/SKILL.md) | Decide tiers, packaging, trials, and the value metric. |
| [product-marketing](product-marketing/SKILL.md) | Write the product marketing context: audience, positioning, ICP. |
| [signup](signup/SKILL.md) | Reduce friction in registration and trial activation. |

### Pipeline, retention, and measurement

| Skill | What it does |
| --- | --- |
| [analytics](analytics/SKILL.md) | Set up or audit tracking, events, and UTMs. |
| [attribution](attribution/SKILL.md) | Choose an attribution model and reconcile disagreeing dashboards. |
| [churn-prevention](churn-prevention/SKILL.md) | Cancellation flows, save offers, dunning, and win-back. |
| [cold-email](cold-email/SKILL.md) | Write B2B cold email and follow-up sequences. |
| [competitor-profiling](competitor-profiling/SKILL.md) | Research competitors from their URLs into a dossier. |
| [competitors](competitors/SKILL.md) | Write comparison, alternative, and "vs" pages. |
| [customer-research](customer-research/SKILL.md) | Synthesize interviews, tickets, surveys, and jobs-to-be-done. |
| [emails](emails/SKILL.md) | Design lifecycle and drip email sequences. |
| [free-tools](free-tools/SKILL.md) | Plan a free tool used as a marketing asset. |
| [lead-magnets](lead-magnets/SKILL.md) | Plan a gated asset for email capture. |
| [prospecting](prospecting/SKILL.md) | Build a qualified list of accounts to contact. |
| [referrals](referrals/SKILL.md) | Design a referral, affiliate, or ambassador program. |
| [revops](revops/SKILL.md) | Lead scoring, routing, and the marketing-to-sales handoff. |
| [sales-enablement](sales-enablement/SKILL.md) | Pitch decks, one-pagers, objection handling, and demo scripts. |
| [sms](sms/SKILL.md) | Plan SMS and MMS flows, including compliance constraints. |

### Planning and creative production

| Skill | What it does |
| --- | --- |
| [image](image/SKILL.md) | Generate or optimize marketing images and mockups. |
| [marketing-council](marketing-council/SKILL.md) | Answer a marketing question from several named expert perspectives. |
| [marketing-ideas](marketing-ideas/SKILL.md) | Starting list of growth tactics for a software product. |
| [marketing-loops](marketing-loops/SKILL.md) | Define a recurring marketing workflow an agent can run on a cadence. |
| [marketing-plan](marketing-plan/SKILL.md) | Write a full marketing plan structured by AARRR. |
| [marketing-psychology](marketing-psychology/SKILL.md) | Apply behavioral science to a marketing decision. |
| [video](video/SKILL.md) | Produce video with AI generators or programmatic frameworks. |
