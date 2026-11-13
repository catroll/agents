# Global Agent Preferences

User-level technical preferences that apply to every project. Treat these as
defaults unless a project's own `AGENTS.md` explicitly overrides them.

Confirmed by the user on 2026-10-12; extended on 2026-10-13, 2026-11-05,
2026-11-08, 2026-11-11, 2026-11-12 and 2026-11-13.

## How this file is organised

This file is loaded on every turn. Additions go in one of two places:

- A rule that should change behaviour on every turn (a stack default, a
  commit habit, a standing permission) is a new section above Lessons.
- A diagnostic note — one signal, one cause, one check — is a new file
  `~/.agents/lessons/<slug>.md` plus one bullet under Lessons. The bullet
  leads with the exact error string or command. Read that file before
  changing code, config, or the diagnosis. Do not paste the note in here.

On 2026-11-13 the notes that had been appended to this file were moved into
`lessons/`. Their wording was left as written.

## Language

- Write **everything in English**: code comments, doc comments, log messages,
  error strings, user-facing responses, API payloads, commit messages, test
  names, README and other documentation.
- This holds regardless of the language the user writes in. A Chinese prompt
  still produces English artifacts.
- Conversational replies to the user may be in the user's language.

## Security and cost are design gates

- Every feature design and implementation must include an explicit security-risk
  review and an explicit cost review. These are release gates, not follow-ups;
  a feature with either one unresolved is not done.
- Security review: trust boundaries, authentication and authorization, input
  validation, abuse and enumeration paths, CSRF and cross-site reachability,
  secret handling, data exposure, fail-open vs fail-closed behavior, and
  auditability.
- Cost review: every paid or finite resource (third-party API calls, SMS and
  email, LLM tokens, storage, egress, compute), worst-case volume and spend,
  retries and refunds, default quotas and rate limits, operator-visible
  counters, and alerts. Name the unit cost and the daily/monthly ceiling.
- Treat any user-triggerable paid side effect as hostile input: gate it behind
  policy checks, per-user/per-IP/global budgets, cooldowns, and a kill switch;
  count only what is actually delivered where possible, and refund reservations
  when delivery fails.
- If a number is unknown, state the assumption and ship a conservative default
  plus a way to change it without a redeploy. Do not leave a cap unbounded just
  because traffic is unknown.
- Record the conclusion (risks, mitigations, limits, residual risk) in the
  feature's plan/README or the relevant work note. "Looks fine" is not a review.

## Tech stack selection: newest well-maintained option wins

- **Default to the newest stable, actively maintained version of every
  dependency**, not the version you recognise. Age is a smell, not a virtue.
- **Verify, do not recall.** Before vendoring or importing a dependency, check
  the upstream release channel (`npm view <pkg> dist-tags`, `go list -m -versions`,
  the project's releases page). Distinguish clearly between *I know this version*
  and *this is the current version* — they are different claims and only the
  second one matters.
- If a newer major exists, either adopt it or write down the **concrete**
  blocker. "The older one is more familiar", "it is the well-known stable line",
  or "the docs I remember use it" are **not** blockers.
- A legitimate reason looks like: the newer major is still pre-release
  (alpha/beta/rc); it has an unresolved regression affecting us; it dropped a
  feature we depend on; it has no stable release at all; or it is unmaintained
  while the older line is still patched.
- Check maintenance health, not just the version number: last release date,
  commit recency, open-issue trend, whether the old line still receives security
  fixes, and whether the project is archived or in maintenance mode.
- Record the reason **at the point of decision** (a comment, an ADR, or the PR
  description), not retrospectively. If no reason is written down, the default
  assumption is that the newest stable version should have been used.
- Prefer fewer, better-maintained dependencies. A framework that pulls in 60
  transitive packages should lose to one that pulls in 1, all else equal.
- When a dependency is already vendored or pinned to an old major, treat it as
  **technical debt to be raised**, not as an established convention to follow.

## Build on the framework, do not override it

- **The framework's own behaviour is the specification.** If a vendored library
  has a way of doing something — a theme, a layout, a component, a state — use
  it, and accept what it produces. Do not write CSS, JS or a parallel
  implementation that re-does it differently on top.
- Before writing anything of your own, **verify what the framework already
  provides**. Read the vendored file. `grep` for the selector, the class, the
  attribute, the option. A surprising amount of "we need to build this" is
  already there and undocumented in the place you were reading.
- When the framework's result looks wrong, the order of investigation is:
  1. Am I using it correctly — the documented attribute value, class, or
     initialisation the library actually accepts?
  2. Is the value I am passing one it recognises? A library that accepts
     `light` and `dark` does nothing with `auto`; the option silently falls
     through to the default. **Check the accepted set, do not assume it.**
  3. Is something of mine overriding it — a later stylesheet, an inline style, a
     wrapper element?
  Only after all three is "the framework cannot do this" a real conclusion, and
  it has to be written down with the evidence.
- **A custom layer is a last resort, not a first instinct.** Overriding a
  framework means owning that behaviour for ever: every upstream upgrade has to
  be re-checked against your override, and the override is the thing that will
  be wrong. Prefer the framework's imperfection to your own maintenance burden.
- This applies to visual style specifically. If a library's dark theme is
  greyer or flatter than you would have designed, that is the library's
  decision: **take it as given**. Consistency with the framework beats a
  locally nicer screen that diverges from everything else.
- Legitimate reasons to override, and they are narrow: the framework has no
  mechanism at all for what is needed; a genuine accessibility defect; a
  security problem; or a documented regression. "I prefer it this way" is not
  one of them.
- When a customisation is genuinely justified, keep it **as small and as
  additive as possible** — a variable, a class on top of the framework's own, a
  config option it already exposes — rather than a replacement, and say in a
  comment why the framework could not do it.

## HTTP framework: Gin

- Use `github.com/gin-gonic/gin` for HTTP services.
- Prefer `gin.New()` over `gin.Default()` so middleware is explicit; add
  `gin.Recovery()` plus a structured request logger yourself.
- Register routes on explicit groups, and keep middleware ordering deliberate:
  session/auth middleware must be installed before middleware that reads the
  session.

## Configuration: YAML

- Configuration lives in a YAML file, not in flags alone.
- Ship an annotated `<app>.example.yaml` with every key documented and showing
  the built-in default.
- Resolve in this precedence, lowest to highest:
  `built-in defaults < YAML file < environment variables < CLI flags`.
- Select the file with a `-config` flag that also has an environment-variable
  equivalent, defaulting to a conventional path (e.g. `pocketadmin.yaml`).
  A missing file at the default path is **not** an error; a missing file at an
  explicitly requested path **is**.
- Reject unknown keys (`yaml.Decoder.KnownFields(true)`) so a typo fails at
  startup instead of being silently ignored.
- Prefer pointer fields in the unmarshalled struct so an absent key is
  distinguishable from a deliberate `false`/`0`.
- Never hard-code secrets. Generate-and-persist (mode `0600`) or require them
  from the environment.

## Logging: log/slog with JSON on stdout

- Use the standard library `log/slog`. No `log`, no `fmt.Println` for
  operational output, no third-party logging framework.
- Handler: `slog.NewJSONHandler(os.Stdout, ...)` — one JSON object per line on
  stdout, so output can be collected and queried without a parsing layer.
- Install it with `slog.SetDefault` before anything else runs, so even startup
  and configuration failures are emitted as JSON.
- Provide a request-logging middleware that emits exactly one structured entry
  per request (method, path, status, latency, client IP, bytes) and levels by
  response status: 5xx → `error`, 4xx → `warn`, otherwise `info`.
- Make the level (`debug|info|warn|error`) and format (`json|text`)
  configurable, with JSON as the default.

## README.md content

- A `README.md` states **what the project is**, not how it is built. The
  audience is someone deciding whether this project is worth their time.
- Keep: project goal and the problem it solves, key features, tech stack,
  quick start, links to deeper docs, license.
- Keep **out**: source-code layout and file trees, configuration reference
  (YAML keys, flags, environment variables, precedence), logging format and
  samples, internal architecture diagrams, verification transcripts, CI details.
- That material belongs in a separate document (`docs/operations.md` or
  equivalent); link it from the README rather than inlining it.
- Prefer tables and short lists over prose. If a section runs past roughly a
  screen, it belongs in the linked document.
- State plainly which features are implemented and which are planned. Never let
  a roadmap read as shipped functionality.

## Git hygiene

- **Committing to git is part of finishing the work, not an afterthought.** The
  user called this out explicitly as a habit to keep: once a change is complete
  and verified, commit it in the same turn.
- Never leave verified work uncommitted at the end of a turn, and never leave
  it uncommitted silently — if something is deliberately left out, say so.
- Commit in logical units. One coherent change per commit, not one commit per
  file and not everything in a single dump.
- The message explains **why**, not just what. A future reader should not have
  to reconstruct the reasoning from the diff.
- Record decisions **at the point of decision**: dependency and version choices,
  what was deliberately *not* done, and any blocker that justified the choice.
  If no reason is written down, the default assumption is that the newest
  maintained option should have been used.
- **Never run `git push`.** Not "only when asked" — never. The user pushes
  themselves. Commit locally and stop there.
- After committing, state plainly what is unpushed and how far ahead the branch
  is, so the user can push deliberately. Do not offer to push, and do not treat
  pushing as the natural next step.
- Inspect before committing: `git status` and `git diff --stat`.
  - Confirm the index contains exactly the intended change set.
  - Confirm nothing sensitive is staged (data directories, generated keys,
    machine-local config).
  - Confirm nothing intended was forgotten (unstaged or untracked files).
- When work depends on a rebuild — embedded assets, generated files, vendored
  bundles — rebuild and re-verify before committing, not after.
- Do not rewrite published history, and do not commit over a failing build.

## A second agent session in the same working tree can commit your files

**Signal.** Files you edited minutes ago show up inside another commit's diff;
`git status` flips between two unrelated change sets; commits describing a
different feature carry your hunks. A shared CSS or i18n file is the usual
victim.

**Cause.** Two agent sessions share one checkout. When either runs
`git add -A` / `git add .`, it sweeps in whatever the other session has in
flight — including unfinished edits and deletions.

**Fix.** In a shared worktree, stage explicit paths only (`git add <paths>`),
never `git add -A`; review `git diff --cached --name-only` against your own file
list before committing; commit small, verified slices early instead of leaving a
large dirty tree; for a long independent task, work in a separate worktree or
branch (`create_worktree`). Put what belongs to the change set in the commit
body, because the file list may later prove incomplete.

## Every software project ships a Makefile with `make help`

Confirmed by the user on 2026-11-13. Applies to every software project, new or
existing, whatever the language.

- A top-level `Makefile` is mandatory and is committed with the project.
- `make` with no arguments (set `.DEFAULT_GOAL := help`) and `make help` both
  print the available targets, one line of description each. Order or group
  them so build / test / run / check / clean are obvious.
- Keep it self-documenting and dependency-free: append `## description` after
  each target line and extract those lines with awk/grep over
  `$(MAKEFILE_LIST)`; do not require Python, jq or an extra help tool.
- Cover at least: help, build, test, format, format-check (or lint), vet (or
  the stack's equivalent), run/dev, clean. Add project-specific targets
  (config bootstrap, migrations, code generation) only where they earn their
  place; do not invent targets that are not real commands.
- Use `?=` for overrides (`BIN`, `CONFIG`, `GO`, ...), never hard-code absolute
  paths, and make bootstrap/config targets idempotent and non-destructive:
  create missing files from examples, never overwrite a live config.
- Test the targets themselves — `make`, `make help`, `make check`/`make test`,
  and a bootstrap target on a clean checkout — not just the commands they wrap.
  If a target is documented in `make help`, it must have been run at least once.

## Verification expectations

- Prefer proving behaviour end-to-end — build the binary, run it, drive it over
  HTTP, assert on real responses — over asserting that code "should" work.
- Report the exact commands run and the observed results, including failures.

## Test runs must keep their artifacts

Confirmed by the user on 2026-11-12.

- During testing, never throw away what was produced because it is
  "temporary". Keep the response body, the request payload and the logs in a
  cache or temp directory (`$PWD/.cache/...`, `~/.cache/...`, or
  `/tmp/<topic>/<run-label>/` on the test host) until the results are written
  into the report; only then may they be cleaned up.
- Keep the full HTTP exchange for every request: request headers and body,
  response headers and body. Redact secrets (`Authorization`, cookies, API
  keys) but keep the status, the error strings and the response shape, so a
  later diagnosis does not depend on re-running a paid or hours-long request.
- Log in detail: timestamps, endpoint, model and params, attempt number,
  first-byte time, total time, HTTP status, usage/token counts, stop reason,
  and the exact error text.
- On a remote test host, write artifacts into a per-run directory and copy
  them back (scp/rsync); do not leave the only copy on the ephemeral host.

## Work records belong in the weekly WLB file

Confirmed by the user on 2026-11-11. This covers schedule items, work content,
meeting records, decisions — anything worth writing down about a day or a week.

- The single home is the weekly work-and-life file
  `~/Projects/Mine/WLB/work/<yyyy>/Q<q>/<mm>/<yyyymm>-<dd>-<dd>.md` (one file
  per week, named and placed by that week's Monday).
- If the content is long or detailed, create a separate file (or directory) in
  the same month directory and keep a short summary plus a link in the week
  file. Never write the detail only into a project document.
- Meeting records follow the same rule: the summary goes in the current week's
  file. Do not treat a project meeting note (e.g. `00-meeting.md`) as the new
  home for a meeting record.

## The project directory is the source of truth for anything installed outside it

Confirmed by the user on 2026-11-08.

- Any artifact this project installs or edits outside its tree — systemd units,
  user-level config files, cron entries, desktop entries, shell profiles, global
  git config, and similar — must also exist as a tracked copy in the project,
  and the install/sync step must be a script in the project (`scripts/…`), not a
  manual edit of the outside copy.
- When a generated copy is not possible, back the outside file up into the
  project and commit it, so git tracks what changed.
- Order matters: update the project copy first, then sync outward. Never edit
  the installed copy first and back-port it.
- Before a later change to such an artifact, compare both sides (the script
  should offer a `diff`/check mode) and report drift explicitly. Do not
  silently overwrite an installed copy that differs.
- Record the install command and the check command in the project's docs so the
  next session can re-verify without guessing.

## Reading the public internet needs no confirmation

**Standing permission.** Running `curl` (or any read-only HTTP fetch, including
the `web_search` / `web_fetch` tools) against public data is whitelisted: do not
ask before it, do not add an "if you want me to" hedge, and do not present it as
a risk. State the URL and the fetch time in the answer.

This covers reads. It does not authorise writes to third-party services,
purchases, or sending mail — those still need a direct request.

## A lookup repeated across sessions needs an on-disk cache, not memory

Model context dies with the session, so "you asked this an hour ago" is not
available in the next conversation unless the value was written down. When a
repo ships a cache helper, use it rather than the vendor API:

```sh
python3 scripts/weather-cache.py --place 武汉 --days 3   # winnie
```

The helper must return the payload **and** its age (`cache.note`), so the reply
can say "数据取自 12:03，8 分钟前" instead of implying live data. A hit means no
network call; `cache.stale: true` means the entry expired and the fetch failed —
say so and retry.

**Design rule for a new cache** (this is the part worth copying): key on the
question's identity (coordinates rounded, window, local date, timezone — never on
the raw question text), store an explicit TTL per data shape, prune on write, and
never cache a payload without its `fetched_at`. A "today" cache keyed without the
date will serve yesterday's forecast, which is worse than no cache at all.

## A todo list nobody updates is a false progress report

**Signal.** The owner asks why the task panel still says "1 进行中，6 待处理"
after the turn that created it finished, tested and committed everything. The
entries were all real; only the panel was stale, because `todo_write` was called
once at the start of the turn and never again.

**Why it matters more than it looks.** The panel is the only progress signal the
owner sees while the turn runs. A list frozen at its opening snapshot claims work
is unstarted that has already shipped, and it sends them looking for a stuck job
that does not exist — in this case the first hypothesis was a wedged app queue
(no Redis listener, no such counter in the console: it was the agent's own list).

**Check.** Treat `todo_write` as paired calls: one to open the plan, and one final
call before the closing reply in which **nothing** is `in_progress` or `pending`.
If the turn used a plan at all, the last state must describe the turn as it
actually ended. Flip each item to `completed` when its work lands, not in one
batch at the end, so the panel stays true while it is being watched.

**Distinguish it from a real queue before investigating.** Asked about "进行中"
counts, confirm whose counter it is: an app-side job queue has a listener, a
table or a log behind it, and the number can be reproduced from one of them; a
stale plan has neither, and its counts match the number of items the agent wrote
down. One `grep` for the exact label and one `ss -ltn` settle which is which
before any debugging starts.

## Every diagnosis ends with a written lesson

A troubleshooting session is not finished until the lesson is written down.
The user asked for this explicitly: it is part of the work, not an optional extra.

- **Global** (this machine, a tool, the sandbox, a protocol, or a way of
  working that applies to any project): add `~/.agents/lessons/<slug>.md` and
  one bullet under [Lessons](#lessons). The bullet starts with the exact error
  string or command. The file holds the signal, the cause, the check, and the
  fix. Do not paste that file into this document.
- **Project** (`docs/decisions.md`, or the project's own memory file) when the
  lesson is about this code, this schema, or this domain.
- Both, when a general lesson was learned from a specific incident.
- **Write the generalisable part, not the incident.** "The `demo` migration used
  the wrong collection name" is a bug report. "A guard that returns nil on a
  missing name turns a typo into a silent no-op; a migration whose subject is that
  collection must fail loudly" is a lesson.
- **Never write "be more careful".** It changes nothing. Write the concrete signal
  that was missed and the concrete check that catches it next time. If the check
  can be a test, make it a test — a lesson with a guard behind it is worth ten
  without.
- **Record the negative result too.** "X does not work because Y" saves the next
  attempt. A dead end that is written down is a finding.
- **Include the exact command, path or error string** that identifies the problem.
  The next reader is usually a machine, and a paraphrase is not searchable.
- Before finishing a turn in which something was diagnosed, ask: *what did I learn
  that I did not know when I started, and where will that be read again?* If the
  answer is nowhere, the diagnosis is not finished.

## Lessons

A diagnostic note grows this list by one bullet. A rule that applies on
every turn is a new section above, not a bullet here. When a failure
matches a bullet, read the named file before changing code, config, or the
diagnosis. The bullet is the action. The file is the procedure, the
commands, and the negative results.

Add a global lesson by creating `lessons/<slug>.md` and appending one bullet
here. Lead the bullet with the exact error string or command. Do not paste
the lesson body into this file. Delete a lesson by removing the bullet and
the file together.

- `connect to host <ip> port 22: Connection timed out` for `47.237.217.143` (`sctest.hosts.d3v.cn`), `106.75.145.225` (`newapi-cn-201.hosts.d3v.cn`), or `52.9.253.68` (`newapi-us-101.hosts.d3v.cn`) — whitelist kept by 孔俊, not sshd. Confirm IPv4 with `curl -4 -s https://myip.ipip.net`, report it, and stop retrying. `lessons/company-ip-whitelist.md`
- `Bad owner or permissions on /etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf` — `ssh -F ~/.ssh/config`. `lessons/ssh-config-owner.md`
- `npm ERR! code EROFS` under `/home/catroll/.npm` — `export npm_config_cache="$PWD/.cache/npm"`. `lessons/npm-cache-erofs.md`
- `Node.js is not compiled with TypeScript support` — the workflow tool cannot run; use a subagent, at most 8 at a time. `lessons/workflow-tool-no-typescript.md`
- `[killed by signal: SIGTERM]` from `pkill -f` / `pgrep -f` — the pattern matched the shell running it. Kill by pid in a separate call. `lessons/pkill-matches-shell.md`
- Cron entry present, log says `make: uv: 没有那个文件或目录`, or a `%` in the crontab command produces no output — cron's PATH and `%` handling. `lessons/cron-path-and-percent.md`
- GitHub Release `curl` exits 28 and leaves a short archive (~25 KB/s here) — compare the file size with `assets[].size` before extracting. `lessons/github-release-slow-truncated.md`
- ImageMagick SVG exits 0 but strokes are gone (`rsvg-convert` is not installed) — rasterise with headless Firefox. `lessons/svg-imagemagick-stroke.md`
- Driving a browser, taking a screenshot, or concluding that no browser is available — read `lessons/browser-firefox.md` before deciding. `Failed to decode request as JSON`, or a `window.confirm` that vanishes: `lessons/webdriver-empty-body.md`. CDN assets with `responseStatus: 0`, or two unrelated files sharing one SRI hash: `lessons/firefox-cannot-fetch-cdn.md`.
- "The page is slow" — measure which file, then payload versus path, before editing nginx. `lessons/slow-page-payload-vs-path.md`
- Webhook wait ends with `seen events=[]` and the store has no row for that id — ask the platform about that exact id before blaming delay. `lessons/webhook-id-mismatch.md`
- Vendor `HTTP 403` with `requested resource not granted`, while a bogus key returns `401` — entitlement, not a bad credential. `lessons/vendor-403-entitlement.md`
- `[UFW BLOCK]` in `/var/log/ufw.log` — compare the block time with the rule file's mtime; a rule is proven by a packet that arrives after it. `lessons/firewall-rule-needs-a-packet.md`
- `API key is missing` while `.env` contains the key — the process kept the environment from when it started. `lessons/env-var-is-process-not-file.md`
- Port is open, `curl` gets no bytes, uvicorn parent is alive — look for a `<defunct>` reload child. `lessons/uvicorn-reload-dead-child.md`
- `ImportError: cannot import name` for a name that is in the file — the process is older than the source. `lessons/importerror-stale-process.md`
- ddns-go reports `failed` while egress works — read the provider body (`InvalidAccessKeyId.Inactive` is a disabled key). `lessons/ddns-provider-verdict.md`
- Repo nginx config has the header, `curl -sD-` does not — the vhost on the machine was never installed. `lessons/vhost-repo-is-not-live.md`
- SPA deep link returns a short `200` placeholder — a prefix `location` swallowed the route, or `auto_redirect` is looping. `lessons/nginx-prefix-swallows-spa.md`
- Logged-in app at `/app` loses the session after a visit to `/` — cookie `Path` plus a flash wrote over it. `lessons/cookie-path-clobber.md`
- Notification topic is glued to the front of the message — the wrapper exported the tool's own variable (`NTFY_TOPIC`). `lessons/wrapper-env-collides-with-tool.md`
- Backup file matches the live data — `backup()` was handed the new payload. Pass the pre-image and restore it once. `lessons/backup-must-be-preimage.md`
- A rewrite of a user's text file is not byte-identical — split on `\n`, not `splitlines()`. `lessons/split-on-newline-not-splitlines.md`
- `UNIQUE constraint failed` after a delete and a restore — the tombstone still owns the key. `lessons/tombstone-owns-unique-key.md`
- Mic turn ends in about a second with "no valid speech", or a vendor HTTP 200 is treated as success — opening the device is not silence, and HTTP 200 is not the verdict. `lessons/capture-open-transient.md`
- Capture RMS looks fine but the 300–3000 Hz band does not move — the input gain is up around +60 dB; measure the speech band. `lessons/mic-gain-speech-band.md`
- A documented option is set and nothing happens — grep the library for reads of that name, not the assignment. `lessons/documented-option-unread.md`
- A failed form save redirects and the typed values are gone — re-render with the submitted non-secret fields. `lessons/redirect-on-validation-loses-input.md`
