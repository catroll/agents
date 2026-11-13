# Global Agent Preferences

User-level technical preferences that apply to every project. Treat these as
defaults unless a project's own `AGENTS.md` explicitly overrides them.

Confirmed by the user on 2026-10-12; extended on 2026-10-13, 2026-11-05,
2026-11-08, 2026-11-11 and 2026-11-12.

## Company server access needs an IP whitelist request to 孔俊

Confirmed by the user on 2026-11-12.

- The user is on a labour contract (劳务合同), not an employee account, so
  there is no default intranet access. Reaching company servers from the
  public internet requires the source IP on a whitelist maintained by
  colleague 孔俊.
- After a public-IP change, `ssh <user>@<ip>` fails with
  `connect to host <ip> port 22: Connection timed out` while DNS resolves
  fine. That is the whitelist, not sshd, the key or the route — do not debug
  the server or the client config; report the new IP and wait.
- Three machines need the whitelist:
  - `sctest.hosts.d3v.cn` = 47.237.217.143
  - `newapi-cn-201.hosts.d3v.cn` = 106.75.145.225
  - `newapi-us-101.hosts.d3v.cn` = 52.9.253.68
- A local cron job watches the public IP and pushes a WeChat message when it
  changes: `0 * * * * /usr/bin/python3 /home/catroll/Projects/Mine/WLB/tools/scripts/publicipchk.py >> /tmp/public_ip.err 2>&1`.
- On an alert, the user messages 孔俊 with the new public IP and the three
  machine IPs, e.g.:
  `我这里的公网 IP 又变了：117.152.220.97 还是那三台机器帮忙配置一下：47.237.217.143 106.75.145.225 52.9.253.68`
- Confirm the current **IPv4** egress before reporting it — this host is
  dual-stack, and `ifconfig.me` answers the IPv6 address, which is not what the
  whitelist takes:
  `curl -4 -s https://myip.ipip.net` (2026-11-12: `117.152.220.97`, 湖北武汉移动;
  `-4` against ifconfig.me, api.ipify.org and ip.sb all returned empty).
- Until the whitelist is updated, anything that needs those machines (deploys,
  log reads, config changes) is blocked; say so instead of retrying ssh.

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

## Language

- Write **everything in English**: code comments, doc comments, log messages,
  error strings, user-facing responses, API payloads, commit messages, test
  names, README and other documentation.
- This holds regardless of the language the user writes in. A Chinese prompt
  still produces English artifacts.
- Conversational replies to the user may be in the user's language.

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

## Verification expectations

- Prefer proving behaviour end-to-end — build the binary, run it, drive it over
  HTTP, assert on real responses — over asserting that code "should" work.
- Report the exact commands run and the observed results, including failures.

## Driving a real browser

A browser is available on this machine. Do not conclude otherwise without trying
these steps, and do not report a visual or layout finding from static analysis
alone when a browser could settle it.

- **Both are snaps, and a snap needs paths outside the workspace.** Firefox wants
  `/run/user/1000/snap.firefox` and `$HOME/snap/firefox`. The file sandbox refuses
  those, and the failure reads as a broken browser rather than a policy denial:
  `cannot create XDG_RUNTIME_DIR folder ... read-only file system`. Launch with
  `sandbox_permissions: danger-full-access`, and say why in the justification.
- **The profile must be inside the workspace.** `/tmp` is refused with
  `Could not find profile folder`. Use e.g. `$PWD/.cache/ff/prof`.
- **Use the real binary, not the wrapper.** `/snap/bin/firefox` is a symlink to
  `/usr/bin/snap` and geckodriver rejects it with
  `binary is not a Firefox executable`. The binary is
  `/snap/firefox/current/usr/lib/firefox/firefox`.
- **`geckodriver` is installed** at `/snap/bin/geckodriver`, but the snap
  wrapper can fail before it listens:
  `cannot create transient scope: DBus error "org.freedesktop.DBus.Error.InvalidArgs":
  [Process 4 is a kernel thread, refusing.]`. That is an environment failure (the
  wrapper is `/usr/bin/snap`), not a Firefox or WebDriver problem. Fall back to
  Firefox's own WebDriver BiDi remote agent, which needs no geckodriver —
  `/snap/firefox/current/usr/lib/firefox/firefox --headless --no-remote
  --profile "$PWD/.tmp/ff/prof" --remote-debugging-port 9222 about:blank` logs
  `WebDriver BiDi listening on ws://127.0.0.1:9222`. Connect to
  `ws://127.0.0.1:9222/session` (a plain `GET /json/version` is 404). Node 22's
  global `WebSocket` is enough; the minimal sequence is `session.new` →
  `browsingContext.getTree` → `browsingContext.navigate` → `script.evaluate`
  (return `JSON.stringify(...)`, then parse the string from `result.value`) →
  `browsingContext.captureScreenshot` (base64 in `data`) → `session.end`. Use
  `browsingContext.setViewport` for desktop/mobile widths and click
  `[data-bs-theme-value="dark"]` to exercise AdminLTE's colour control.
- **`browsingContext.setViewport` takes `context`, not `contexts`.** Firefox 157
  rejects `contexts: [id]` with `At least one of "context" or "userContexts"
  arguments should be provided`; pass
  `{ context, viewport: { width, height }, devicePixelRatio: 1 }`. `navigate`
  and `captureScreenshot` also use the singular `context`.
- **WebDriver is a plain HTTP protocol**, so `curl` is enough when geckodriver
  does work — Selenium, Playwright and jsdom are not needed and installing them
  usually fails offline.
- **Do the whole run in one bash call.** Background processes do not survive
  across calls, so start the app, start geckodriver, create the session, drive the
  page, read the result and clean up in a single command.
- **Read `getComputedStyle`, do not squint at a screenshot.** For any factual
  question — which colour, which font, is it hidden, what is the size — a
  `execute/sync` returning the computed value is decisive where an image is an
  opinion. Keep the screenshot for layout and for anything you would only notice
  by looking.
- **Form fields may have no `id`.** Select with `querySelector('input[name=...]')`.
  A missing element throws, the script returns nothing, and if the result was
  discarded the whole step fails silently. Always print what the script returned.
- **Screenshot what a user sees, in their language, in each theme.** Static
  analysis cannot see a value the server supplies at render time. A page can pass
  every template test and still show `pending_payment` where a label belongs.
- **A page behind a login you do not have: mirror its DOM, do not skip the
  measurement.** When the component is only reachable with a session and no
  credential exists in the checkout, copy its markup class for class into a
  temporary page that loads the app's own CSS bundles (plus whatever layout
  classes the framework puts on `<body>`), serve it from the app's dev server,
  and measure before and after the change with `getBoundingClientRect()`. Keep
  the class list identical to the source — a harness that drifts proves nothing —
  delete the page afterwards, and say plainly that it verifies the CSS and the
  classes, not the page.
- **One BiDi session at a time, and `session.end` in a `finally`.** A probe that
  throws between `session.new` and `session.end` leaves the session open, and the
  next run dies with `session not created: Maximum number of active sessions`
  before it navigates anywhere. `GET /` on the port still answers `200`, and a
  bare `session.end` on a stale connection returns `invalid session id`, so the
  recoverable move is to kill that Firefox (by the pid you started) and relaunch;
  the durable one is to end the session in `finally`.

## Every diagnosis ends with a written lesson

- **A troubleshooting session is not finished until the lesson is written down.**
  The user asked for this explicitly: it is part of the work, not an optional
  extra.
- Write it where it will be read again:
  - **Global** (`~/.agents/AGENTS.md`) when the lesson is about the environment,
    a tool, the sandbox, a protocol, or a way of working that would apply to any
    project.
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

## The `workflow` tool does not run on this machine

**Signal.** Every call fails immediately, before the script does anything:

```
workflow run failed: workflow execution failed (exception):
Node.js is not compiled with TypeScript support
```

A one-line body (`return { ok: true };`) fails the same way, so it is the runtime,
not the script. Do not debug the script — there is nothing in it to fix.

**Cause.** The harness evaluates the workflow script as TypeScript, which needs
Node's type stripping. This machine runs Node `v22.22.1`, where stripping is
opt-in and off:

```bash
node --version                              # v22.22.1
node -e "console.log(process.features.typescript)"   # false
```

Type stripping is enabled by default only from Node 23.6, or by passing
`--experimental-strip-types` (22.6+). Nothing a caller passes to the tool changes
this.

**Workaround.** Use the `subagent` tool instead of `workflow`, and run the fan-out
yourself. The concurrency cap is **8 active children**; a ninth call returns
`Error: subagent limit reached (active child limit: 8)`. Launch in waves of eight,
and launch the next as each child finishes — the completion notice is the signal.
A long fan-out (20 modules, say) is three or four waves.

**What is lost.** `workflow` gives per-item pipelines with a barrier and a
schema-validated result; `subagent` gives only a text result. When the phases
depend on each other, either write the intermediate state to files the children
read, or accept a second wave.

**Lesson for the next tool that fails on its first call.** A failure on a
one-line input is an environment failure. Report it, find the check
(`process.features.typescript` here), and record the exact string — do not spend
turns re-authoring the payload.

## Rendering SVG on this machine: use headless Firefox, not ImageMagick

**Signal.** ImageMagick accepts an SVG and exits 0, but the output is silently
wrong. Circles and lines that use `stroke` simply vanish; only filled paths
survive. `magick -list delegate | grep svg` advertises
`svg => 'rsvg-convert' ...`, but `rsvg-convert` is **not installed**, so IM
falls back to its own `MSVG` renderer, which does not implement stroke on
`<circle>`/`<line>`. Nested `<svg>` elements are ignored too — a contact sheet
built from nested viewports renders only the first panel.

**Consequence.** Any visual verification done through ImageMagick is worthless
for stroked artwork: a correct logo looks like it is missing its frame, and you
will "fix" a bug that does not exist. Check the renderer before trusting it:

```bash
magick -list delegate | grep -i svg     # advertises rsvg-convert
command -v rsvg-convert                 # ...which is MISSING
```

**What works.** Headless Firefox screenshots a real SVG (or a local HTML page)
exactly, including strokes, arcs, `fill-rule` and text. One call, no WebDriver,
no Selenium:

```bash
export MOZ_HEADLESS=1 XDG_RUNTIME_DIR=/run/user/1000
/snap/firefox/current/usr/lib/firefox/firefox --headless --no-remote \
  --profile "$PWD/.cache/ff/prof" \
  --window-size=1200,1200 --screenshot "$PWD/out.png" "file://$PWD/art.svg"
```

- `--screenshot` needs a *writable* profile directory and `XDG_RUNTIME_DIR`;
  both are outside a workspace-write sandbox, so this needs full access.
- The screenshot is the size of `--window-size`. To rasterise at 2x, copy the
  SVG with `width`/`height` rewritten to the target size (the `viewBox` keeps
  the geometry exact) rather than upscaling a 1x PNG.
- The snap needs `MOZ_HEADLESS=1` **and** `--headless`; without
  `XDG_RUNTIME_DIR` it reports a misleading read-only-filesystem error.

**Corollary for hand-written SVG.** Prefer a real renderer for verification, but
keep the deliverable idiomatic: emit the frame as a stroked `<circle>` and
verify it in the browser, rather than contorting the artwork into filled annuli
just to satisfy a broken rasteriser. Ship a fill-only build only as a separate
convenience asset.

## A webhook/IMAP timeout blames the platform only after you resolve the id there

**Signal.** A whole cohort of webhook-waiting cases times out with
`seen events=[]`, and the event store holds no record for the exact emailId the
case is waiting on.

**Check the platform's own API with that exact id before talking about delay or
load.** For ASC: `GET /api/data/emailStatus?emailIds=<id>$rcpt&days=3`
(the `$rcpt` suffix and the day window are both mandatory).
If the platform still answers `No corresponding record found` for an id it
handed back 19 hours earlier, while the same second/recipient has a record under
a *different* id ~29 ms away, that is a **platform-side id mismatch** — not push
delay, not load, not "the mail was never delivered".

**Trust the population, not the sample.** Diff the number of DSL cases that wait
on webhooks (`grep -rl webhook_check_request`) against the failure list: here
**all 204 executed sg cases failed** while the two hk/us region cases in the
same batch **passed**. "One scoped subset failed 100% while its sibling cases
were fine" beats any single log — it kills the flake/concurrency explanations in
one step and points at that one path.

**Trap.** A failed-only export **does not contain the passing sibling cases**, so
the control group is not in it. Sites usually expose
`GET /runs/<run_id>/logs/<case_name>/download` for any case, in any run —
that is how the healthy batch's send ids were obtained here. Do not stop at
"the export does not have it".

**Also.** "The id does not exist" and "the event arrived late" can both print
`seen events=[]`. And `delay > timeout` is not proof of push delay: the window
ends at *step start + timeout*, not at `event_time + timeout`. Separating these
requires going back to the platform for data.

## `ssh` fails on every host: pass `-F ~/.ssh/config`

**Signal.** Every `ssh` invocation dies immediately with exit 255, before opening
a connection, and the message names a *system* file, not your host or key:

```
Bad owner or permissions on /etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf
```

A valid `~/.ssh/config` entry and a working key change nothing — even a host you
reached five minutes ago now fails.

**Cause.** `/etc/ssh/ssh_config` line 19 is `Include /etc/ssh/ssh_config.d/*.conf`.
On this workstation that directory is owned `nobody:nogroup` mode `777` and holds
a symlink into `/usr/lib/systemd/ssh_config.d/`. ssh refuses a config file it
cannot attribute to root or the current user, and one bad include kills the whole
run. Check with:

```bash
stat -c '%n owner=%U group=%G mode=%a' /etc/ssh/ssh_config.d/*
```

**Fix.** Give `-F` explicitly. Per `man ssh_config`, a command-line `-F` makes ssh
ignore the system-wide file as well as the default per-user one:

```bash
ssh -F ~/.ssh/config -o BatchMode=yes <host> 'command'
```

Do not try to `chown`/`chmod` the system path: it is outside the workspace, the
sandbox denies it, and it is not yours to fix.

**Generalisable bit.** When ssh's error names a config file, the failure is
client-side and host-independent — reach for `-F ~/.ssh/config` before suspecting
the server, the key, or the network. Wrapping it as `SSH="ssh -F ~/.ssh/config"`
saves rediscovering this on every call.

## "The page is slow" is two questions: how big, and how fast

Never start with the nginx/application config. Split the delay into **payload** and
**transport** first; they have completely different fixes, and the config is
usually innocent.

1. **Ask the browser which file is slow.** WebDriver `execute/sync` on a real
   page, one row per resource — `duration` and `transferSize` identify the single
   critical-path file where static analysis would only produce a list:

   ```javascript
   performance.getEntriesByType("resource").map(e => ({
     n: e.name, t: Math.round(e.startTime),
     d: Math.round(e.duration), s: e.transferSize
   }));
   ```

   Real case: 51 s to a login form, of which `main.js` was 49 s / 903,792 B, while
   HTML TTFB was 267 ms and every API call was under 1.3 s. One number, no guessing.

2. **Measure both endpoints independently before blaming either.** From the client,
   a well-peered CDN (`speed.cloudflare.com`) or a domestic mirror. From the server,
   the same trick reversed — `__up` for egress, `__down` for ingress. Here the
   server did 37 MB/s to Cloudflare and the client 20 MB/s from a domestic mirror,
   yet 8 KB/s to each other: the **path**, not the host. An EIP/bandwidth cap would
   have capped the Cloudflare test too, so that measurement also clears the bill.

3. **Get the loss ratio from `ss -tin` on both ends.** `bytes_retrans / bytes_sent`
   is the number that settles it (19 % here), and `cwnd:2 ssthresh:2` shows the
   congestion window pinned at its floor. Prefer this over packet captures — no
   root needed.

4. **Distinguish loss from a rate limit with a 1-second rate profile.** Loss gives
   burst-and-nothing (`12K, 32K, 16K, 0, 0, 16K, …` — retransmission timeouts);
   `limit_rate`/token-bucket gives a steady floor. Parallel connections scaling
   linearly (~4 × 11 KB/s ≈ 44 KB/s) also means per-connection loss, not a total cap.

**Corollary.** A cross-border SPA that is fine warm can be a minute cold: check the
cache both ways. Here a warm reload was 2 s with `transferSize=0` while the cold
load was 51 s, so "slow for me" and "slow for everyone" are different reports.

**And.** Test more than one hour before writing "peak-hour congestion". This one
was 13.6 KB/s at 00:13 and 7.6 KB/s at 14:07 — bad at both ends of the day, which
makes it persistent peering damage rather than a busy hour, and that changes the
recommendation (accelerate the path; do not wait for off-peak).

**HTTP/2 is a pessimisation on a lossy path.** "Enable h2, it is faster" is the
default reflex and it is wrong here. HTTP/1.1 gives the browser six connections per
origin, each with its own congestion window, so throughput multiplies with
parallelism (measured on this path: 4 parallel connections ≈ 4× one connection,
~44 KB/s vs ~13 KB/s). HTTP/2 multiplexes every stream onto a single TCP connection,
which is exactly the wrong shape when that connection is losing 19 % of its packets.
Leave `http2 on;` out on a lossy vhost and say why in the config, or the next person
will helpfully "fix" it.

**Check the compression headroom before adding a compressor.** The instinct is to
switch on nginx gzip, but the app server may already be compressing. Compare the
bytes actually on the wire against `gzip -9` of the same file before claiming a win:
here the backend produced 903,492 B and `gzip -9` only reached 894,805 B (1 %), so
nginx-side compression was pointless. A whole class of "optimisations" evaporates
once you measure the number first.

## `pkill -f <pattern>` kills the shell you are typing it in

**Signal.** A bash call dies mid-script with `[killed by signal: SIGTERM]` and no
output from the rest of the command. Nothing is wrong with the target process.

**Cause.** `bash -c '<command>'` puts the whole command line in
`/proc/<pid>/cmdline`, so `pkill -f` matches the invoking shell whenever the
pattern appears anywhere in that command — including inside the pkill argument
itself, a heredoc, an echo, or a `python3 -c` snippet in the same call. The
bracket trick (`[/]tmp/x.py`) only defeats shells that exclude their own pid by
matching the literal text; it does not help when the *same literal string* is
elsewhere in the command line, which it usually is.

**What works.** Kill by pid (`pgrep -f pattern` in one call, `kill <pid>` in the
next), or make the pattern unable to appear in the command:
`P="fake_$(printf smtp)"; pkill -f "$P"`. Check with `ss -ltnp`/`ps -eo pid,args`
before assuming an orphan is still holding the port.

**The same trap reaches `pgrep` when the pipeline is in one call.** A cleanup
written as `pgrep -f 'remote-debugging-port 9222' | while read pid; do kill
"$pid"; done; rm -f preview.tsx` matched the shell running it (that shell's
argv *is* the pattern) and killed the shell, so the `rm` never ran: the call
reported `[killed by signal: SIGTERM]` and silently left two temporary files in
the tree. The "two calls" rule above is not optional, and the damaging part is
the abandoned work after the kill, not the signal.

A single-call form that does work excludes itself by a token only the target
lacks: `ps -eo pid,args | awk '/snap.firefox.*--headless/ && !/awk/ {print $1}'`.
The shell's own line contains `awk`, so the filter drops it. Either way, verify
the cleanup in a *separate* call — `test ! -e <file>` — rather than trusting a
step that follows a kill in the same command.

**Related trap.** A port can report `EADDRINUSE` from `bind()`
while `ss -ltn` shows no listener and only TIME-WAIT connections remain;
`SO_REUSEADDR` did not clear it here (`127.0.0.1:2526`), and the same bind
succeeded immediately on `2537`. Move to another port instead of debugging the
old one.

## A backup function that receives the new payload is not a backup

**Signal.** The rollback artifact exists, has a plausible size, and its contents are
indistinguishable from the live data — because they *are* the live data.

**Cause.** A one-word mistake in the call site: the migration built
`payload = {**old, **{k: v for new values}}`, then passed that same `payload` to
`backup()` and to `write()`. Every test that checked "a file was created" passed.

**Check.** Two rules, both cheap:
1. The backup call takes the **pre-change** value, by name (`backup(original)`), never a
   variable that is also going to be written.
2. A backup is only verified when it has been **restored once**. Here the restore source
   ended up being a real `mysqldump` from an earlier step — parse the dump and compare one
   known key (`qwen3.7-plus` coefficient `0.219178`) against the file you plan to restore.

**Recovery.** `mysqldump --databases` output is a full pre-image: the old option row was
still inside a dump taken 25 minutes earlier. Parsing it needs a quote-aware scanner, not
a regex — `INSERT ... VALUES (...)` contains `;` and `),(` inside string literals, so a
non-greedy `.*?;` silently matches nothing. Walk characters, track the string state, and
stop at the first `;` **outside** quotes.

**And.** SQLite accepts DDL that MySQL rejects (`PRIMARY KEY` inline *and* table-level →
`ERROR 1068 Multiple primary key defined`). A local SQLite rehearsal cannot validate a
MySQL `CREATE TABLE`; run the DDL against the target engine once, in a scratch database,
before the maintenance window.

## A cron line that has never run looks installed

**Signal.** A crontab entry has been in place for weeks and its log contains the
same one-line failure on every attempt:

```
make: uv: 没有那个文件或目录
make: *** [Makefile:80：deps] 错误 127
```

**Cause.** cron runs a job with `PATH=/usr/bin:/bin`, not your shell's `PATH`.
Anything installed per-user (`uv`, `cargo`, `pipx` shims in `~/.local/bin`) is
invisible there, so a job that shells out to `make`/`uv`/`node` dies before it
does any work — while the same command typed in a terminal succeeds.

**Check.** Run the job the way cron does before installing it, and again after:

```bash
env -i HOME="$HOME" PATH=/usr/bin:/bin SHELL=/bin/sh LOGNAME="$USER" \
  /path/to/job.sh; echo "exit=$?"
```

**Fix.** Set `PATH` (plus `LANG`, and any transport variable such as
`RSYNC_RSH` or `GIT_SSH_COMMAND`) inside the script, not in the crontab line, so
a manual run and a cron run behave identically. Then read the job's existing log
once: "it is in the crontab" is not evidence that it has ever worked.

**Also: `%` in a crontab command is not a literal.** cron turns an unescaped
`%` into a newline and feeds the rest to the command's stdin, so a probe written
as `* * * * * date "+%F %T" >> log` is executed as `date "+` and silently
produces nothing (journal shows `(catroll) CMD (date "+cron-alive )`). Use
`date -Is` in a crontab, or escape every percent sign as `\%`. A probe that
produces no output is more likely a quoting bug than a dead daemon — check
`journalctl -u cron -n 20` for the `CMD (...)` line, which shows the command
after cron has rewritten it.

## A vendor 403 naming a "resource" is an entitlement, not an auth, failure

**Signal.** A speech/ASR API call fails with `HTTP 403` and a body like
`code=45000030, message=[resource_id=volc.bigasr.auc] requested resource not granted`,
for every model line you try. It reads like "forbidden because the credential is
wrong", so the reflex is to add or change auth headers.

**Check.** Send the identical request twice, once with the real credential and
once with a deliberately invalid one, then compare the codes:

- bogus key: `HTTP 401, code=45000010, message=Invalid X-Api-Key`
- real key:  `HTTP 403, code=45000030, message=[resource_id=...] requested resource not granted`

Two *different* codes prove the credential was read and accepted; the account
simply has no entitlement for that resource. The fix is to enable/activate the
service for the key's project in the console, not to touch the code. This one
extra request also gives the user the single action they must take.

**Related, Volcengine Doubao speech.** The current console issues one API key,
sent as `X-Api-Key` alone ("在任意接口中，填入header即可，不用填写appid" —
`docs/doubao-voice/api-key-usage`). `X-Api-App-Key` + `X-Api-Access-Key` are the
old console's pair; a 403 mentioning the resource is not evidence they are
still needed.


## A firewall rule is not proven until a packet arrives after it

**Signal.** A LAN client times out to a service that works from the host, and
`/var/log/ufw.log` contains a line like:

```
[UFW BLOCK] IN=eno1 SRC=192.168.1.42 DST=192.168.1.38 PROTO=TCP DPT=8000 ... SYN
```

That log is decisive: DNS resolved, the LAN path works, and the host firewall
dropped the packet. Do not debug the app, the client URL or DNS first.

**Check the timestamps, not only whether the rule exists.** Compare the last
block with the rule file's mtime:

```bash
date -Is
stat -c '%y' /etc/ufw/user.rules
grep 'DPT=8000' /var/log/ufw.log | tail -1
```

Real case: last block `14:44:32`, `user.rules` modified `14:44:48`. The failed
attempt predated the rule, so "I allowed the port and it still fails" was not a
firewall bug — the client had not retried since the rule took effect. Retry
once, then judge.

**Fix and verify.** Prefer a scoped rule, and confirm success in the service log
rather than in `ufw status` alone:

```bash
sudo ufw insert 1 allow from 192.168.1.0/24 to any port 8000 proto tcp
sudo ufw reload
```

The first accepted request shows the client source, for example
`::ffff:192.168.1.42 - "GET /healthz HTTP/1.1" 200 OK`.

**A localhost curl proves nothing about the input chain.** It uses the loopback
path and never traverses the rules that decide whether another LAN host may
connect.

## A missing env var blames the process, not the `.env` file

**Signal.** A service fails with `RuntimeError: ... API key is missing; set FOO`,
even though `FOO=...` is present in the `.env` you just edited.

**Cause.** Environment variables are captured when the process is exec'd. A
running server keeps the old environment; `uvicorn --reload` watches `*.py`, not
`.env`, so a reload never happens for a config-only edit. `make api` sources
`.env` in the shell that starts uvicorn — editing the file afterwards changes
nothing until that shell runs again.

**Check.** Ask the process directly, without printing the value:

```bash
grep -c '^FOO=' apps/api/.env          # 0 means the file has no key
pid=$(pgrep -f 'uvicorn.*8000' | head -1)
tr '\0' '\n' < /proc/$pid/environ | grep -c '^FOO='   # 0 means the process has no key
```

**Fix.** Add the key, then restart the process (a `--reload` will not do it), and
retry the exact operation. Confirm in the service log that the provider call now
runs, rather than assuming a restart fixed it.

**Also.** A `403` from a vendor after a correct key is an entitlement problem
(`code=45000030`), not a missing or wrong key — do not conflate the two.

## npm needs a workspace cache on this machine

**Signal.** `npm view`, `npm install` or `npm pack` fails before doing network
work, with a path under `$HOME`:

```
npm ERR! code EROFS
npm ERR! syscall open
npm ERR! path /home/catroll/.npm/_cacache/tmp/94b7f0d3
npm ERR! errno -30
```

**Cause.** `$HOME` is read-only in this environment (the same reason the uv
cache lives in the checkout). npm's default cache is `~/.npm`, and it fails on
the first temp-file write, so an empty `npm view` result is not a registry or
network failure.

**Fix.** Point the cache inside the checkout for that command, or export it for
the shell:

```bash
export npm_config_cache="$PWD/.cache/npm"
npm install --no-audit --no-fund
npm config get cache        # confirms the override
```

Keep the directory gitignored (`/.cache/`). Do not change `$HOME` permissions;
it is not yours to change and the sandbox will refuse.

## WebDriver POSTs need `{}`, and native dialogs need a handler

**Signal 1.** `find element` works, but `element/click` or `element/clear`
returns HTTP 400:

```
{"value":{"error":"invalid argument","message":"Failed to decode request as JSON: ","stacktrace":"Syntax error at :1:0"}}
```

**Cause.** The W3C WebDriver POST endpoints expect a JSON body. A raw HTTP
client that sends `data=None` transmits no body, so geckodriver's JSON parser
fails. It is not an element or session problem.

**Fix.** Send `{}` for POST/PUT commands that carry no arguments.

**Signal 2.** A test clicks a button whose handler calls `window.confirm(...)`,
but `GET /session/{id}/alert/text` reports no dialog, the action never runs past
the prompt, and the page looks unchanged.

**Cause.** Firefox's default `unhandledPromptBehavior` is "dismiss and notify";
the prompt is auto-dismissed before the next command. This also makes a test
believe the flow executed when the user answered "no".

**Fix.** Set `"unhandledPromptBehavior": "ignore"` in the session capabilities,
then use `GET /session/{id}/alert/text` (the endpoint is GET, not POST) and
`POST /session/{id}/alert/accept`. A button click that opens the prompt returns
success; the prompt stays open until accepted.

**Screenshot trap.** AdminLTE headers and footers transition background colour
for 0.3 s. A screenshot taken immediately after switching light/dark catches a
half-transitioned grey header and looks like a broken theme. Wait for
`transitionend` or ~0.5 s, or read `getComputedStyle(...).backgroundColor` —
which reports the final value as soon as the class is applied.


## A uvicorn reloader can keep the port with a dead child

**Signal.** `ss -ltnp` still shows the port listening and `ps` still shows the
reloader, but `curl -m 5 http://127.0.0.1:8000/healthz` returns no bytes after
the timeout. There is no traceback in the service log because the process that
would print it is gone.

**Cause.** A reload child crashed while importing a newly added editable
package. The reloader did not replace it; the parent stayed in its sleep loop
and kept the listening socket. The port is open, so a supervisor or a naive
health check sees a listener, but no request is served.

**Check the process tree, not only the port:**

```bash
ps -eo pid,ppid,stat,wchan:20,args | grep -E 'uvicorn|<defunct>'
```

A `<defunct>` child under the uvicorn pid plus a listening parent means a dead
app. To separate "code is broken" from "reloader is stale", start the same app
with the same config in a one-off process on another port and read its stderr.
If that starts, the code is fine and the reloader is the problem.

**Fix.** Install the new package, stop the server, and start it again (without
`--reload` while recovering). Verify `/healthz` **and one real route**; a
listener is not evidence that the app works.

**The general bit.** A `--reload` wrapper is not the application. When a port
is open but nothing answers, inspect the child before debugging the framework,
the database or the network.

## Rewriting a user's text file: split on `\n`, and prove it with a round trip

**Signal.** A parser written to preserve formatting still rewrote a file:
`"\n".join(text.splitlines()) + "\n" != text` for
`~/Projects/Mine/WLB/work/2024/Q4/12/202412-16-22.md`, which contains a literal
`\x0b` (vertical tab) inside a paragraph. `str.splitlines()` also breaks on
`\x0c`, `\x1c`-`\x1e`, `\x85`, `\u2028` and `\u2029`, so any of them silently
becomes a line boundary and the "unchanged" bytes are lost.

**Fix.** `lines = text.split("\n")`, pop the trailing `""` when the text ended
with a newline, and keep that fact for the write. Then assert the invariant
against the real corpus: every file must parse and render back to its exact
bytes (`week.render() == path.read_text()`), and add-then-delete must return the
file unchanged. That single test caught the `\x0b` file, and it is what makes a
line-splicing editor safe to point at files a human also edits.

**And a silent grammar failure: a `^\[` anchor after a consumed token.**
Parsing ``- [ ] `10/05` [周一] [09:30~10:30] text`` with ``^`(\d+/\d+)` `` and
then `^\[([^\]]+)\]` matched nothing, because the date regex consumed the
backticks and left one space before the first `[`. Every tag became part of the
text and nothing raised: the listing "looked right" because it printed the line
verbatim. Strip whitespace between tokens (`^[ \t]*\[...`) and assert the
post-condition that matters, not the presence of a function — here,
`event.text` must not start with `[`, checked over all 10k events in the corpus.

## A unique key that includes tombstones is not insert-only

**Signal.** A build that had worked for weeks dies with
`IntegrityError: UNIQUE constraint failed: docs.root_id, docs.rel_path`
right after a file was deleted and something reappeared at its path.

**Cause.** The table soft-deletes (`state='deleted'` tombstones) but the unique
index does not exclude them. The sweep's "existing rows" query filtered
`state != 'deleted'`, so its diff saw no row at that path and took the `INSERT`
branch — while the tombstone still owned the key. The same filter made a
**rename**'s `UPDATE ... SET rel_path=?` collide when it moved a live row onto a
tombstoned path. Both failures abort the whole build, so one delete-then-restore
made the index permanently unbuildable.

**Check.** Ask the catalog before touching the code: "is there a row for this
exact key in *any* state?"

```sql
SELECT id, state FROM docs WHERE root_id = ? AND rel_path = ?;
SELECT rel_path FROM docs WHERE state = 'deleted';  -- compare with the disk
```

A tombstone whose file exists again is the whole diagnosis.

**Fix.** Load every row for the key, tombstones included, and give the tombstone
a resurrection path that resets the state and redoes the derived work (here:
clear `state` so the "text unchanged, skip re-chunk" shortcut cannot fire, then
rebuild chunks that were purged on delete). Constrain renames to keys that are
provably free. Skip already-deleted rows in the deletion pass, or every sweep
re-counts and re-stamps the same tombstones.

**Do not** paper over it with `INSERT ... ON CONFLICT DO UPDATE`: the row it
overwrites has lost its derived rows, and any state-keyed shortcut will happily
leave it marked "indexed" with nothing behind it.

**Generalisable.** A soft-delete is an ownership claim on the uniqueness key.
Every writer must treat the tombstone as the incumbent and update it in place;
"absent from the live diff" does not mean "the key is free".

## GitHub Releases are ~25 KB/s here, and a timed-out download leaves a plausible file

**Signal.** A `curl -m 300` of a 49 MB release asset ends with exit code 28
(timeout) and a 7 MB file; a `-m 600` retry of a 38 MB model reaches 15 MB.
`ls -l` shows a real file, so the next step (`unzip -l`, `tar xf`) runs on a
truncated archive. Sizes to expect: ~20–40 KB/s, i.e. a 38 MB tarball needs
~20 minutes and a 49 MB AAR much longer.

**Rule.** Before extracting an archive fetched from a release, compare its size
with the asset size from the GitHub API — `curl -s
https://api.github.com/repos/<owner>/<repo>/releases/latest` and check
`assets[].size`. A truncated `.bz2` fails loudly on `tar xf`; a truncated `.zip`/
`.aar` can partially list, which is worse.

**What works instead.** The Aliyun PyPI mirror moves at ~2.3 MB/s
(`--index-url https://mirrors.aliyun.com/pypi/simple/`), and `python3.13` has
sherpa-onnx cp313 wheels there. Hugging Face mirrors and ModelScope are
reachable, but check that the repo actually contains the weights: the
`sherpa-onnx-kws-*` copy on hf-mirror is a WASM build (`install/bin/wasm/...`),
not the `.onnx` files. For sherpa-onnx the GitHub Release is the only source,
so a 38–49 MB spike is not a one-turn operation on this host.

**And.** `developer.android.com` is unreachable from this machine (`curl` exit
28, `web_fetch` TypeError `fetch failed`), so Android platform rules cannot be
cited from the source page here. Read them from the installed SDK
(`$ANDROID_HOME/platforms/android-*/`) or the device, and label platform
behaviour as unverified rather than quoting numbers from memory.

## A capture device that just opened is not silent — and a vendor's 200 can be a failure

**Signal 1 (audio).** A browser microphone recorder ended its turn ~1.3 s after
the microphone opened, with `heardSpeech = true`, and uploaded ~42 KB that the
ASR vendor rejected as "no valid speech". Per 20 ms frame the recording was a
decaying thump and then nothing:

```
0.02s:-13.6  0.10s:-35.3  0.20s:-47.0 ... 1.28s:-64.3   (dBFS)
```

**Cause.** Opening a suspended capture stream resumes the analog input, and it
settles with a transient tens of dB above any sensible speech floor. An RMS gate
sees that as speech; the browser's `noiseSuppression`/`autoGainControl` then gate
the steady room noise to −80 dBFS, so the trailing-silence rule ends the turn
before the person has said anything. The same device reads −20 dBFS of sub-80 Hz
rumble through `parec`, because the browser's speech processing removes exactly
that. Check both sides before blaming the hardware:

```bash
parec --format=float32le --rate=16000 --channels=1 --latency-msec=50 > mic.raw
# and record one turn through the app itself, then print per-20 ms dBFS
```

**Fix.** Ignore the first ~400 ms when deciding whether speech started (keep the
samples in the upload), and never let the speech decision be made in the first
100 ms of a stream — that is a decision about the device, not the user.

**Signal 2 (mapping).** The same endpoint answered HTTP 500 for that recording.
The ASR adapter raised a bare `RuntimeError` for every vendor condition, while
the route caught only its own `AIProviderError`/`httpx`/`ValueError`; a vendor
answer of `X-Api-Status-Code: 20000003` ("Normal silence audio") therefore became
an unhandled exception.

**Check.** Two greps that should agree, because they are in different files and
nothing enforces the contract:

```bash
grep -n "raise " <adapter>.py
grep -n "except " <route>.py
```

Exercise the *successful-but-empty* answer in a test, not just a transport error:
mock `HTTP 200` with the vendor's status header and assert a 4xx.

**Generalisable.** "ASR failed" is three different facts — the audio had no
speech (4xx), the provider failed (5xx), the binding is unconfigured (503) — and
a status code that collapses them tells the next person nothing. Also: a vendor's
HTTP 200 means "the RPC arrived"; the verdict is in the body or a header.

## A microphone that reads loud may be an open input at +60 dB

**Signal.** A voice turn failed with "no valid speech in audio". The capture
device reported a healthy-looking `rms -23 dBFS`, yet the 300–3000 Hz band sat at
**-58.7 dBFS** and did not move at all while a full-scale speech clip was played
to the sink. All of the power (100%) was under 80 Hz.

**Cause.** Gain, not signal. `amixer -c 1 sget 'Rear Mic Boost'` showed boost 3
(+30 dB) and `Capture` 63 (+30 dB): **+60 dB into the ADC**. At that gain an open
or unpowered input's own DC drift and sub-sonic rumble read like a usable level,
while the audible band stays at the converter's noise floor. Jack-detect
`Rear Mic Jack: on` only says a plug is inserted — a cable to a device that is
off or unpowered closes the switch too.

**Check.** Measure the speech band, not broadband RMS, and make it rise:

```bash
make audio-check                                  # speak when prompted
make audio-check ARGS="--play clip.wav"           # speaker -> room -> mic
```

A broadband number with an empty 300–3000 Hz band means "nothing audible is
connected", not "the microphone is sensitive". `amixer -c <card> sget 'Capture'`
plus the same for `<Front|Rear> Mic Boost` gives the real gain; `alsamixer -c
<card>` shows it interactively. A correct capture at this gain would clip speech,
so the gain is wrong even once a microphone works.

**Do not conclude "the mic is deaf" from a playback test alone.** The monitor
source proves what the sink *received*, not what the speaker emitted: an amp that
is off and a microphone that hears nothing produce the same recording. Only the
person in the room can separate them — ask, or have them speak during the quiet
phase and read the band level.

**A control measurement on another pin separates "dead codec" from "dead
microphone".** Retask the same converter's other input and measure it with nothing
plugged in:

```bash
amixer -c 1 sset 'Input Source' 'Line'    # open jack: expect a quiet, flat floor
timeout 6 parec --format=s16le --rate=16000 --channels=1 --raw > line.raw
amixer -c 1 sset 'Input Source' 'Rear Mic' # restore, and read it back to be sure
```

Here the open line input read `rms -70.4 dBFS` with a flat spectrum (speech band
-75.0), while the rear-mic pin read `-20.5 dBFS` with 100% of its power under
80 Hz and a flat -58.7 dBFS speech band. That rules out the ADC, the mixer and the
port selection in one step: the mic pin has a device attached that shifts the DC
operating point and emits nothing audible. It is still not proof the *capsule* is
dead — a 4-pole (TRRS) headset in a 3-pole (TRS) mic jack lands its mic contact on
ground and looks identical — so the remaining tests are physical: unplug the
microphone and repeat (do the numbers collapse to the open-jack floor?), then
touch the plug tip with a finger (a working mic input roars with 50 Hz hum at this
gain; silence means the jack or cable does not reach the converter).

**Generalisable.** An RMS level is an absolute number with no reference; only a
*ratio between bands* or a *difference between two phases* tells you whether the
signal is a voice or the amplifier's own noise. When a speech pipeline fails,
measure the band the consumer uses (300–3000 Hz here) before touching thresholds.

## A prefix proxy location can swallow an SPA's routes, and `auto_redirect` can loop

**Signal.** A deep link (`https://token.shanedit.com/dashboard/overview`) renders a
bare placeholder page — 104 bytes saying `frontend is served by nginx` — while
clicking around inside the running app works and `/` is fine. The app is a history
routing SPA whose `basePath` is `/dashboard`, so the URL is a legitimate page, not an
API path.

**Cause.** `location /dashboard/ { proxy_pass ... }` had been added for the two
OpenAI billing-compat endpoints (`/dashboard/billing/subscription|usage`). A prefix
location is all-or-nothing: every refresh under `/dashboard` reached the Go backend,
which has no such route, so its `NoRoute` handler answered with the placeholder index
page **and HTTP 200**. In-app navigation is `pushState` and never touches nginx,
which is why only refreshes, direct opens and shared links showed it.

**Check.** Compare a deep link against the real shell, then ask the config who owns
the prefix:

```sh
curl -s -o /dev/null -w '%{http_code} %{size_download}\n' https://host/dashboard/overview  # 200 104  -> placeholder
curl -s -o /dev/null -w '%{http_code} %{size_download}\n' https://host/index.html           # 200 1683 -> real shell
nginx -T | grep -n 'location.*dashboard'
grep -rn 'GET("' /opt/app/router/*.go    # what the backend really serves
```

The bundle names the routes it owns: `grep -o 'path:"/[^"]*"' static/js/index.*.js | sort -u`.

**Fix.** Exact matches for the endpoints that are actually API; everything else falls
through `try_files $uri $uri/ /index.html`.

**Second failure mode in the same config, worth recognising separately.** A prefix
location ending in `/` that contains `proxy_pass` makes nginx redirect `/x` → `/x/`
(`auto_redirect`); if the upstream also canonicalises the slash (gin's
`RedirectTrailingSlash` answers `/x/` with `301 -> /x`), the two bounce forever and
`curl -L` dies with `Maximum (50) redirects followed`. Both directions disappear when
the prefix location is removed — never "fix" it by adding `location = /dashboard`,
which just pages the loop's first hop.

**Lesson for the smoke test.** A routing regression that only shows on refresh is
invisible to a `/`-only probe. Request one deep link the SPA owns and assert a shell
marker (`id="root"`), not the status code — the wrong answer here is 200 with the
right content type.

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

## A wrapper's own config name that matches the tool's env var is not namespaced

**Signal.** The notification arrived with the topic name glued to the front of
the body:

```
title:   New API 新版本 v1.0.0-rc.99
message: woodynotice-selftest 上游新发布 1 个版本 tag：\nv1.0.0-rc.99
```

The shell called `ntfy publish --title T --tags ... "$target" "$body"`, and the
same run exported `NTFY_TOPIC=woodynotice-selftest` for the wrapper script.

**Cause.** The ntfy CLI reads `NTFY_TOPIC` (documented: `NTFY_TOPIC=mytopic ntfy
publish "some message"`). When it is set, the topic comes from the environment
and **every positional argument becomes the message** — including the topic the
caller passed. The wrapper had chosen `NTFY_TOPIC` as the name of its own config
variable, so the value leaked into the tool's namespace and duplicated itself.

**Fix.** Name wrapper config after the wrapper, not after the tool:
`WATCH_TOPIC` / `WATCH_SERVER`. And `unset NTFY_TOPIC NTFY_TITLE NTFY_TAGS ...`
before invoking the CLI, so a stray exported value cannot silently rewrite the
title, tags or priority that the code just built.

**Why the test missed it.** The first test publish did not export the variable,
so the message was clean; only the tagged path, run with the variable in the
environment, reproduced it. **A publish path is not verified by the publish that
does not use the same environment as production.** Send the real message once
with the real env, then read it back from the server
(`curl "https://ntfy.sh/<topic>/json?poll=1"`) instead of trusting exit 0 — an
exit code says the RPC arrived, not that the payload is right.

## An `ImportError` for a name that is in the file means the process is older than its source

**Signal.** A long-running Python service answers a request with a bare 500, and
the traceback ends:

```
ImportError: cannot import name 'article_source_url' from
'markjour.utils.article' (/path/markjour/utils/article.py)
```

The import is at the top of a file pulled in **lazily inside the request**
(`from markjour.scripts.articles import do_new`). The name *is* in the target
file, and a fresh interpreter imports it without error.

**Cause.** The service was started before the file changed (here: process
start `12:00:27`, refactor written `12:13`), and it has no reloader
(`ADMIN_DEBUG=0`, gunicorn/uwsgi without `--reload`). Interpreter module objects
are frozen at import, but a lazy import still reads the **new** file off disk.
That mixes a fresh module with old in-memory dependencies: the *file* has the
re-export, the *loaded* module does not.

**Two checks that are decisive and cheap.**

```bash
ps -eo pid,lstart,args | grep '<service invocation>'   # start time
find admin markjour -name '*.py' -newer <the pid's start time>   # edited after start
```

and re-run the failing import in a fresh interpreter (same venv, same
`sys.path`). If that succeeds, the code is fine and the process is stale —
restart and re-test the real HTTP request. Do not "fix" the module.

**Fix without sudo.** When the service is owned by a root supervisor and
`supervisorctl` needs an unreachable password, the child usually runs as the
normal user: `kill -TERM <pid>` and `autorestart=true` brings up a fresh process.
Confirm with a new start time in the log, not just a listening port.

**Why a banner beats a note.** This recurs (three incidents in this repo:
2026-10-14, 2026-10-30, 2026-11-03), because the reminder lives in docs nobody
reads while operating the panel. Make the process compare the newest source
mtime with its own start time and say so **where the operator is looking** —
a page banner plus a startup log line with `pid=… started=… newest_source=…`,
which is also what a later diagnosis greps for.

**Generalisable.** "The file says X but the object does not have X" is a
statement about process age, not about code. A lazy import makes the discovery
happen at request time and disguises it as a 500.

## A "DDNS failed" alert is the provider's verdict, not the network's

**Signal.** ddns-go posts `- IPv6 (<addr>): failed` (or an ntfy message with a
unix timestamp) while the host's IPv6 egress works and the router is healthy.
The provider's record still holds an address the host no longer has.

**Read the provider's error body first.** ddns-go logs it verbatim:

```
Failed to query domain info! Response body: {"Message":"Specified access key is disabled.",
"Code":"InvalidAccessKeyId.Inactive"} ,Response status code: 400
```

`InvalidAccessKeyId.Inactive` = the credential exists but is disabled: not a
network error, not a missing record, not a firewall problem. Compare the two
sides instead of guessing:

```bash
dig +short AAAA eqr.hosts.d3v.cn @223.5.5.5   # what the world resolves
ip -6 -o addr show scope global               # what the host actually owns
```

A record value absent from the second list is dead, whatever else looks fine.

**One alert can cover days of failure.** ddns-go fires its webhook once, on the
third consecutive failure after start (`current failure times: 407`), then stays
quiet until the next restart. Count before calling it a one-off:

```bash
journalctl -u ddns-go --no-pager | grep -c InvalidAccessKeyId.Inactive
```

**Look for a working credential before minting one.** acme.sh stores
`SAVED_Ali_Key`/`SACED_Ali_Secret` in `~/.acme.sh/account.conf`, and a read-only
`DescribeDomainRecords` proves them without touching DNS. Here acme.sh's key
answered 200 while ddns-go's returned `Inactive` — two consumers of one Aliyun
account drifting apart, most likely a key rotation that updated one and not the
other.

**Then fix the address selection too.** With `net.ipv6.conf.<if>.use_tempaddr=2`
ddns-go publishes the *temporary* privacy address, which is regenerated on every
reboot and prefix change. Pin the IPv6 with ddns-go's regex (e.g. the DHCPv6
`::4`, or the `mngtmpaddr` address) or the record goes stale again at the next
boot even with a healthy key.

**Negative result.** ddns-go v6's config API is not `/api/config` (that serves
index.html); the session cookie comes from `POST /loginFunc` with a JSON body,
and the config is pushed to the page rather than fetched by a known REST path.
The web UI password lives in the install dir (`admin_password.txt`).

**A no-match regex is not a failure, and ddns-go never exits on an IP error.**
I told the owner a prefix change would make it "报错停下". The source says
otherwise (v6.17.1, `config/config.go` `getIpv6AddrFromInterface`): an unmatched
`Ipv6Reg` logs `没有匹配到任何一个IPv6地址, 将使用第一个地址` and returns
`Address[0]`; and `RunOnce` errors only clear that round's cache, the timer
loop keeps firing (the 491-failure morning is the proof — the process never
left). So the risk of pinning is a *silently wrong* address, never a dead
service. When asked what a tool does at an edge, open its twenty lines before
answering: "it will stop" is a claim about code, and a plausible failure mode is
worth less than one `grep`.

## A vhost rule in the repo is not a live header

**Signal.** A sidebar fed by `/meta.json` stops updating while the article pages
stay fresh; the repo's `nginx.conf` has the `no-cache` rule and the docs say so,
yet the response carries no header:

```bash
curl -sD- -o /dev/null https://host/meta.json | grep -i cache-control   # nothing
```

**Cause.** The vhost on the server was four months old; three blocks added to
the repo file since (the cache rule among them) had never been installed,
because the publish job only rsyncs the generated site. Without an explicit
policy the browser guesses freshness from `Last-Modified` (~10% of the file's
age), so the one JSON behind every non-HTML widget keeps a cached copy for
hours. The access log settles it: non-bot HTML views against `/meta.json`
requests and the 200/304 split — 5,699 vs 550, 549 of them unconditional 200s.

**Check.** Verify the response, not the file: stage with a timestamped backup,
`nginx -t`, restore on failure, reload, then assert the observable header. A
reload is graceful and returns before the old workers drain, so a probe started
right after it can still hit the previous config — retry instead of reporting a
false failure. A reader holding the old copy needs one hard reload; prefer a
cache-buster in the caller when a widget must never lag.

## A cookie's `Path` is a routing rule, and a "please log in" flash overwrites the session

**Signal.** A panel mounted at `/app` asks for a password on every visit even
though a session already exists: `/app/` keeps working in the tab that is logged
in, but opening the bare `http://host:port/` shows the login form — and
afterwards `/app/` is logged out too. The access log shows an unauthenticated
request to the app's own root immediately before each login.

**Cause.** The session cookie is written with `Path=/app`. A browser never sends
that cookie to `/`, so the root request was anonymous by construction — and
`login_required` answered with `flash('please log in')`, which is a session
**write**. Flask therefore returned, on the redirect,

```
Set-Cookie: session=eyJfZmxhc2hlcyI6...; Path=/app
```

whose payload is `{"_flashes":[...]}` — the same cookie name and path as the
real session, minus `user`. The browser replaced the authenticated cookie with
the anonymous one. The root URL did not just demand a login; it deleted the
session.

**Check.** Diff two headers: the `Set-Cookie` from a successful login and the
one from the unauthenticated request. Same name and path with different content
is a clobber, not an expiry and not a signature failure (a rotated secret would
fail to decode the *old* value instead). Server side reproduces with two curls
sharing one Cookie header; browser side shows as a single `storage.getCookies`
entry whose value no longer decodes to a user.

**Fix.** Scope the cookie to the origin (`Path=/`) and give it an app-specific
name so another app on the same host cannot collide, then set `SCRIPT_NAME` for
*every* request so pages rendered at the bare root still emit prefixed links.
The narrow path is the wider bug: it makes the app serve a page it can never
authenticate. A redirect from `/` to `/app/` also removes the bounce, but it
loops behind a proxy that strips the prefix — the cookie fix does not.

**Generalisable.** Authentication failures are usually read as "the session is
gone"; here the session was fine and a *different* request rewrote it. When a
login does not stick, compare the cookie the browser ends up with, not the one
the login response set.

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

## Headless Firefox in this environment cannot fetch external CDNs — vendor local assets

**Signal.** A page loaded over `127.0.0.1` has local assets but every
`https://cdn.*` resource fails: resource timing shows `responseStatus: 0` and
`transferSize: 0`, page `fetch()` rejects with
`TypeError: NetworkError when attempting to fetch resource`, and an SRI-enabled
`<script>` reports:

```
None of the “sha384” hashes in the integrity attribute match ... The computed hash is “OLBgp1GsljhM2TJ+sbHjaiH9txEUvgdDTAzHv2P24donTt6/529l+9Ua0vFImLlb”.
```

The decisive tell: the **same** "computed hash" appears for two unrelated files
(e.g. easymde and bootstrap.bundle). Two files cannot share a hash — the response
is an interception/error body, not the asset, so the integrity value is not the
bug. Do not "fix" SRI, and do not conclude the library or typings are wrong.

**Check.** In the browser context, not with `curl` (curl works; this is
browser/network policy):

```js
performance.getEntriesByType('resource')
  .map(e => ({n: e.name, status: e.responseStatus, bytes: e.transferSize}));
await fetch(url, {mode: 'cors'}).then(r => r.status).catch(e => String(e));
```

`responseStatus: 0` + `NetworkError` means the asset never reached the page.
Note the existing page may look "styled enough" to hide it: an admin whose
Bootstrap CSS is CDN-hosted will render unstyled in this browser, so a layout
or colour finding measured here is about missing CSS, not about your change.

**Fix.** For locally served tools (admin panels, internal dashboards) vendor the
runtime asset under the app's own static directory and reference it with a local
URL; then there is no SRI, no CDN outage, no runtime network request, and the
page is verifiable and usable offline. Keep the upstream `LICENSE` beside it and
record the version. This is the second reason vendoring beats a pinned CDN URL
for a local tool; the first is that the tool must work when the network doesn't.

## A documented library option can be dead code — grep for its read site

**Signal.** Setting a documented option has no effect, and the library has no
error to show for it. Example: EasyMDE 2.21.0's `iconClassMap` is accepted and
stored (`options.iconClassMap = extend({}, iconClassMap, options.iconClassMap || {})`,
`src/js/easymde.js:1873`) but never read again — built-in toolbar buttons got
their classes from the module-level `iconClassMap` at load time, so the option
cannot change them. The README lists it; the typings do not; the behaviour is
absent.

**Check.** Search the source for *reads*, not the assignment:

```sh
grep -n "iconClassMap" node_modules/<pkg>/src/js/*.js   # one assignment, zero reads
```

If the only hit is where it is set, the option is a no-op for that code path.
Then choose the narrow workaround (`post-init DOM class swap`, custom toolbar with
the documented `icon` markup, etc.) and write the evidence next to it, so the
next reader does not re-trust the option.

## A rejected form save that redirects is a data-loss bug

**Signal.** "I submitted, it said failure, and everything I typed was gone." The
save handler calls `flash(...)` + `c.Redirect(303, formPath)` on a validation
failure, and the GET form re-renders from the stored state.

**Cause.** Post/Redirect/Get is right for the success path only. On failure the
redirect discards the POST body: the page shows the previously saved config
(blank for a create form), so the user's input is lost. It also hides which
field was wrong because the error is a toast, not a field marker.

**Fix / check.** On validation failure re-render the same template with 400/422,
the submitted **non-secret** values and `FormErrors` mapped per field; never echo
credentials, passwords or API keys. Search a handler for `Redirect` in every
validation branch — that is the whole audit. Three corollaries from the TinyAPI
run:
- A visible required `*` must be derived from what the server actually rejects.
  Marking a field the server accepts (empty forgot-password email) and not
  marking a table the server rejects (dynamic model rows) both make the UI lie.
  HTML `required` alone is a convenience, not validation.
- An inline `<script>` inside a template's `content` block runs **before** the
  layout's `<script src="...bootstrap...">`: `new bootstrap.Modal(...)` there
  throws `ReferenceError` silently, and both "reopen the modal after 422" and
  "show the one-time key on success" fail invisibly. Wrap it in
  `DOMContentLoaded`, or move the logic into the deferred app script.
- One-time tokens: call `valid(token)` and validate the submitted data, and only
  `consume(token)` after everything passes. `consume` first turns one password
  typo into a permanently dead reset link.

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
