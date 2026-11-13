# Global Agent Preferences

User-level technical preferences that apply to every project. Treat these as
defaults unless a project's own `AGENTS.md` explicitly overrides them.

## How this file is organised

This file is loaded on every turn.

- A rule that should change behaviour on every turn is a new section above Lessons.
- A diagnostic note about this machine or any project is a file in
  `~/.agents/lessons/` plus one bullet under Lessons. Read that file when its
  bullet matches. A note about one project's code or schema goes in that
  project's `docs/lessons/`, not in this file.

## Language

- Write **everything in English**: code comments, doc comments, log messages,
  error strings, user-facing responses, API payloads, commit messages, test
  names, README and other documentation.
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
- Before vendoring or importing a dependency, check the upstream release
  channel (`npm view <pkg> dist-tags`, `go list -m -versions`, the project's
  releases page) and use what that check returns.
- If a newer major exists, adopt it or write down the concrete blocker: it is
  still pre-release (alpha/beta/rc); it has an unresolved regression affecting
  us; it dropped a feature we depend on; it has no stable release; or it is
  unmaintained while the older line is still patched.
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
- Override only when the framework has no mechanism for what is needed, or
  there is an accessibility defect, a security problem, or a documented
  regression. Keep that override additive — a variable, a class, or a config
  option the framework already exposes — and say in a comment why it could not.

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

- Once a change is complete and verified, commit it in the same turn. One
  coherent change per commit. If something is deliberately left out, say so.
- The message explains **why**, not just what. A future reader should not have
  to reconstruct the reasoning from the diff.
- **Never run `git push`.** After committing, state what is unpushed and how
  far ahead the branch is.
- Inspect before committing: `git status` and `git diff --stat`.
  - Stage explicit paths (`git add <paths>`).
  - Confirm the index contains exactly the intended change set.
  - Confirm nothing sensitive is staged (data directories, generated keys,
    machine-local config).
  - Confirm nothing intended was forgotten (unstaged or untracked files).
- When work depends on a rebuild — embedded assets, generated files, vendored
  bundles — rebuild and re-verify before committing.
- Do not rewrite published history, and do not commit over a failing build.

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

- During testing, keep what was produced until the results are written into
  the report. Use a cache or temp directory (`$PWD/.cache/...`, `~/.cache/...`,
  or `/tmp/<topic>/<run-label>/` on the test host).
- For every request, keep the exchange: request and response headers and body,
  timestamps, endpoint, model and params, attempt number, first-byte time,
  total time, HTTP status, usage or token counts, stop reason, and the exact
  error text. Redact secrets (`Authorization`, cookies, API keys); keep the
  status, the error strings, and the response shape.
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
  file. A meeting record follows the same rule. A project note such as
  `00-meeting.md` does not become the home for that record.

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

Read a public URL (`curl`, `web_search`, `web_fetch`) without asking, and state
the URL and the fetch time in the answer.

Writes to third-party services, purchases, and sending mail still need a direct
request.

## A lookup repeated across sessions needs an on-disk cache, not memory

A value that lives only in the conversation is gone when the session ends. When
a repo ships a cache helper, call it instead of the vendor API.

The helper returns the payload and its age. Say when the data was fetched. A
hit does no network call. When the entry is stale, the refresh failed — say so
and retry.

Key a new cache on the question's identity (coordinates rounded, window, local
date, timezone), not on the raw question text. Store an explicit TTL per data
shape, prune on write, and store `fetched_at` with the payload. A "today" cache
keyed without the date serves yesterday.

## Update a todo list before the reply

If a turn opened a plan, mark each item completed when its work lands. The last
update before the reply has nothing `in_progress` or `pending`.

## Close the turn with what went wrong

Confirmed by the user on 2026-11-13.

End every turn with a short account of the problems this turn actually hit and
the lesson each one produced. A turn that hit nothing says so in one line and
writes no file.

Write a file only when a later run would do the wrong thing without it, and no
existing lesson already covers the same signal. Search `~/.agents/lessons/` and
the project's `docs/lessons/` for the error string before adding one. The file
name and the opening line are the signal. Do not keep a second index that
copies them.

- **Global** (this machine, a tool, the sandbox, a protocol, or a way of
  working that applies to any project): `~/.agents/lessons/<slug>.md` plus one
  bullet under [Lessons](#lessons). That pair is the global memory.
- **Project** (this code, this schema, this domain): `docs/lessons/<slug>.md`
  at the repository root. Create the directory on first use. If the project
  already keeps lessons in one named file, append there instead of opening a
  second home.
- Both, when a general lesson was learned from a specific incident. The global
  file keeps the reusable check. The project file keeps the paths, ids, and
  schema. Each links to the other.
- A lesson does not replace the weekly work note. The note records that the
  work happened. The lesson records the check that prevents a repeat.
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
- In the reply, name the file written. When nothing was written, say whether the
  turn hit nothing or an existing lesson already covers it, and name that lesson.

## Lessons

When a failure matches a bullet, read the named file before changing code,
config, or the diagnosis. The bullet is the action. The file is the procedure,
the commands, and the negative results.

Append one bullet here, and put the body in `lessons/<slug>.md`. Lead the
bullet with the exact error string or command. Delete a lesson by removing the
bullet and the file together.

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
- Files just edited show up in another commit's diff, or `git status` flips between two change sets — the other session ran `git add -A`. Stage explicit paths. `lessons/second-session-git-add.md`
- The task panel still lists work in progress after the turn finished — the plan was never updated. Close every item before the reply. `lessons/todo-list-stale.md`
