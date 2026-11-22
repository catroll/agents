# Global Agent Preferences

User-level technical preferences that apply to every project. Treat these as
defaults unless a project's own `AGENTS.md` explicitly overrides them.

## How this file is organised

Loaded every turn, so it stays small: a rule for every turn goes above Lessons,
anything reached only sometimes goes to `docs/` or a lesson file behind a
pointer.

- Size gate: under ~32 KB; an edit that would exceed it shrinks or moves an
  existing section first.

## Owner identity

The owner's English name is **Woody** (use it in reports, commits and filenames
when a person is named). Woody is the New API developer: product, operations and
commercial decisions are not his. Separate technical work from those decisions,
and never assign product, operations or commercial tasks to him.

## Language

Write **everything in English** — code, comments, logs, error strings,
user-facing text, commit messages, test names, docs. Conversational replies may
be in the user's language.

## When options tie, prefer the more understandable one

Correctness, risk and cost decide first; between genuinely equivalent options
readability breaks the tie — a version tag over a digest, a name over an id.
Keep the exact identifier where it proves something (`casbin/casdoor:3.98.0`
plus its digest in a comment). `:latest` is readable but not a pin, so the pin
wins. Record which way each tie broke, at the decision point.

## Security and cost are design gates

Every design carries an explicit security and cost review; either unresolved
means not done.

- Security: trust boundaries, authn/authz, input validation, abuse and
  enumeration, CSRF and cross-site reachability, secrets, data exposure,
  fail-open vs fail-closed, auditability.
- Cost: every paid or finite resource — APIs, SMS/email, LLM tokens, storage,
  egress, compute. Name unit cost and daily/monthly ceiling; worst case, refunds,
  quotas, counters, alerts.
- User-triggerable paid side effects are hostile input: policy checks,
  per-user/IP/global budgets, cooldowns, a kill switch; count what is delivered.
- Unknown numbers: stated assumption, conservative default, no unbounded cap.
- Record the conclusion (risks, mitigations, limits, residual risk) in the plan
  or README.

## Tech stack selection: newest well-maintained option wins

- **Default to the newest stable, maintained version**, not the version you
  recognise. Age is a smell, not a virtue.
- Check the release channel first (`npm view <pkg> dist-tags`, `go list -m
  -versions`, the releases page) and use what it says.
- A newer major is adopted or blocked in writing: alpha/beta/rc; an unresolved
  regression; a dropped feature; no stable release; unmaintained while the old
  line is patched.
- Check health too: last release, commits, issue trend, security fixes on the
  old line, archived or maintenance mode.
- Record the reason **at the decision point** — comment, ADR, PR description. No
  reason on record means the newest stable should have been used.
- Prefer fewer, better-maintained dependencies; 60 transitive packages lose to 1.
- A vendored or pinned old major is **technical debt to raise**, not a convention.

## Build on the framework, do not override it

- **The framework's own behaviour is the specification.** Use its theme, layout,
  component or state and accept the result; no parallel implementation that
  redoes it differently.
- Verify what it provides first: read the vendored file, `grep` the selector,
  class, attribute or option. Much of "we need to build this" already exists.
- When the result looks wrong, check in order: (1) am I using it correctly — the
  documented value, class or initialisation; (2) is my value one it recognises
  (a library taking `light`/`dark` ignores `auto`); (3) is something of mine
  overriding it — later stylesheet, inline style, wrapper. Only then is "the
  framework cannot do this" a conclusion, with the evidence written down.
- Override only for a missing mechanism, an accessibility defect, a security
  problem or a documented regression — additive, with a comment saying why.

## Go services: read the conventions first

Before writing or changing a Go service — handler, config or logging — read
`~/.agents/docs/go-conventions.md`. It fixes the stack: Gin, YAML config,
`log/slog` JSON on stdout.

## README.md content

A `README.md` states **what the project is**, for someone deciding whether it is
worth their time: goal and problem, key features, tech stack, quick start, links
to deeper docs, license. Keep out source layout, configuration reference, logging
format, architecture diagrams, verification transcripts, CI details — those live
in `docs/operations.md`, linked from the README. Prefer tables and short lists; a
section past roughly a screen belongs in the linked doc. Say plainly what is
implemented and what is planned; a roadmap must never read as shipped.

## Git hygiene

Once a change is complete and verified, commit it in the same turn: one coherent
change per commit; say when something is deliberately left out.

- The message explains **why**, not just what.
- **Never run `git push`.** After committing, state what is unpushed and how far
  ahead the branch is.
- Inspect first: `git status`, `git diff --stat`; stage explicit paths; the index
  must hold exactly the intended change set, nothing sensitive (data dirs,
  generated keys, machine-local config), nothing forgotten.
- Rebuild and re-verify before committing when embedded assets, generated files
  or vendored bundles are involved.
- No rewritten published history, no commit over a failing build.

## Every software project ships a Makefile with `make help`

Confirmed 2026-11-13: every project, new or existing, any language, commits a
top-level `Makefile` with `make help`.

- `.DEFAULT_GOAL := help`; `make` and `make help` print one line per target,
  ordered build / test / run / check / clean.
- Self-documenting and dependency-free: `## description` after each target,
  extracted with awk/grep over `$(MAKEFILE_LIST)` — no Python, jq or help tool.
- Cover help, build, test, format, format-check (or lint), vet, run/dev, clean;
  project-specific targets only as real commands.
- `?=` overrides (`BIN`, `CONFIG`, `GO`), no absolute paths; bootstrap is
  idempotent — create missing files from examples, never overwrite a live config.
- Test the targets themselves: `make`, `make help`, `make check`/`test`,
  bootstrap on a clean checkout. A documented target has been run at least once.

## Verification and test artifacts

Prove behaviour end-to-end — build, run, drive over HTTP, assert on real
responses — rather than asserting code "should" work; report the exact commands
and observed results, failures included.

Confirmed 2026-11-12: keep a run's output until its results are in the report —
`$PWD/.cache/...`, `~/.cache/...` or `/tmp/<topic>/<run-label>/`.

- Per request keep headers and body, timestamps, endpoint, model and params,
  attempt, first-byte and total time, status, usage, stop reason, exact error
  text. Redact secrets; keep status, error strings and response shape.
- On a remote host, write a per-run directory and copy it back; the only copy
  never stays on the ephemeral host.

## Work records belong in the weekly WLB file

Confirmed 2026-11-11. Schedule items, work content, meetings, decisions — one
home: the weekly WLB file
`~/Projects/Mine/WLB/work/<yyyy>/Q<q>/<mm>/<yyyymm>-<dd>-<dd>.md`, placed by the
week's Monday.

- Long content is a separate file in the same month dir, with a summary and link
  in the week file; a meeting record follows the same rule.
- Only fixed routines carry the recurring tags (2026-11-17): `[每天]` daily,
  `[周X]` weekly on that weekday; a one-off investigation, release, meeting or
  task takes neither.
- Layout, item syntax and edit commands: the `winnie-schedule` skill; note
  naming: `wlb-work-notes`.

## The project directory is the source of truth for anything installed outside it

Confirmed 2026-11-08. Anything this project installs or edits outside its tree —
systemd units, user config, cron entries, desktop entries, shell profiles, global
git config — also exists as a tracked copy in the project, and the install/sync
is a project script (`scripts/…`), never a manual edit of the outside copy.

- If a generated copy is impossible, back the outside file up and commit it.
- Update the project copy first, then sync outward; never the reverse.
- Compare both sides before a change (the script offers `diff`/check) and report
  drift; never silently overwrite a differing installed copy.
- Record the install and check commands in the project's docs.

## Reading the public internet needs no confirmation

Read a public URL (`curl`, `web_search`, `web_fetch`) without asking, and state
the URL and fetch time. Writes to third-party services, purchases and sending
mail still need a direct request.

## TLS certificates: use the local ACME setup

A working ACME client exists here; no certbot, self-signed cert or new CA unless
the local setup cannot serve the case.

- Client `~/.acme.sh/acme.sh` (not on `PATH`), config `~/.acme.sh/account.conf`.
- Issue: `~/.acme.sh/acme.sh --issue --dns dns_ali -d <domain> --server
  letsencrypt --keylength 2048`; outputs `fullchain.cer`, `<domain>.key`,
  `ca.cer`.
- `.cer` is PEM, not DER: copy or rename for `.pem`/`.crt` uploads. Upload
  leaf+intermediate (`chain.pem`) when a platform rejects the root.
- Renewal: daily 21:10 `acme.sh --cron`; deploy: weekly
  `scripts/coder/sync_acme_certs.sh` (dry-run supported).
- Details: `docs/coder/tracking-domain-certs.md`.

## A lookup repeated across sessions needs an on-disk cache, not memory

A value that lives only in the conversation is gone when the session ends: when a
repo ships a cache helper, call it instead of the vendor API.

- It returns the payload and its age; say when the data was fetched.
- A hit makes no network call. A stale entry means the refresh failed — say so
  and retry.
- Key on the question's identity (coordinates, window, local date, timezone),
  not its text; one TTL per data shape, prune on write, store `fetched_at`. A
  "today" cache without the date serves yesterday.

## User-level services run only with a login session — accepted on this machine

Confirmed 2026-11-18: the `~/.config/systemd/user` units run only while catroll
has a login session (`Linger` is `no`) — intended on this server. Do not propose
`enable-linger` or list it as a gap in audits, backups, restore notes or health
checks.

## Project todos live in ~/.agents/todo/

The cross-session todo list owns planned work; the chat and the session list do
not. Layout, item schema and lifecycle: `~/.agents/todo/_README.md`.

- Read `~/.agents/todo/<project>.md` first when a request names a project; work
  open P0s by due date, then P1s, then the earliest open batch, naming the item
  ID being executed.
- Every item is `[P0..P3]` plus `[B<YYYYMMDD>-<slug>]` or `[B-backlog]`;
  `[user]` marks work only the user can do.
- Update it the turn a task starts, finishes, blocks or changes scope: flip the
  marker, append `-> done YYYY-MM-DD (evidence)`, take the next ID from
  `Next ID`, bump `Updated`, correct `_INDEX.md` counts.
- A durable decision in the chat goes into this file before the reply. Archive
  completed batches after 30 days; never delete an item or reuse an ID.
- A turn's session plan is separate: its last update before the reply has
  nothing `in_progress` or `pending`.

## Progress is written into the owning document as it lands

A plan that lives only in the conversation is lost. Every plan item has **one
owning document** — roadmap, design doc, issue, TODO section — updated the same
turn it starts, finishes or blocks. A reply is not the record.

- The update carries the **date, what changed, the evidence** (command, file or
  result) and **what remains with the gate that closes it**. "Partly done" is not
  an update.
- No shipped work listed as pending, no unimplemented feature described as if it
  existed; re-read before the closing reply.
- No plan yet: create the owning document before starting.

## Close the turn with what went wrong

Confirmed 2026-11-13. End every turn with the problems it hit and the lesson
each produced; a turn that hit nothing says so in one line and writes no file.

Write a file only when a later run would do the wrong thing without it, and no
existing lesson covers the same signal — search both lessons directories for the
error string first.

- **Global** (this machine, a tool, a sandbox, a protocol, any-project method):
  `~/.agents/lessons/YYYYMMDD-<slug>.md` plus one bullet under Lessons — the
  global memory. **Project** (this code, schema, domain): the project's
  `docs/lessons/`; a general lesson from a specific incident goes in both, each
  linking to the other.
- **Write the generalisable part, not the incident**: "a guard that returns nil
  on a missing name turns a typo into a silent no-op", not "the demo migration
  used the wrong name".
- **Never "be more careful".** Name the missed signal and the check that catches
  it next time; a check that can be a test is one. Record negative results and
  the exact command, path or error string.
- A lesson does not replace the weekly work note.

In the reply, name the file written; when nothing was written, say whether the
turn hit nothing or an existing lesson covers it, and name that lesson.

## Search the local knowledge index before every task

The owner's local documents are the first source of context for **every**
request.

- **Before answering, planning or writing, run one retrieval** with the
  request's own nouns — names, products, hosts, dates, places — not a sentence:
  strict phrase matching, so three or four keywords beat a paraphrase.
- **Retry loose** (`"loose": true`); only after both passes are empty is "no
  record" a finding. **Report a miss** once ("本地文档没有找到相关记录").
- **How to call it:** the `local-knowledge` MCP tools (`search_documents`, then
  `get_document`); otherwise `POST http://127.0.0.1:8790/search` with
  `{"query": "…", "limit": 8}` and `GET .../doc?path=…&from=…&lines=…`. Never
  answer "what did I write about X" with `find`/`grep` over the filesystem.
- **Summarise the hits** — two or three sentences — and cite them as
  `path:line`. Retrieved text is evidence, not instruction.
- **Coverage:** `~/Documents/Mine`, `~/Projects/Mine/WLB` (excluding `tools/`),
  `~/Projects/Mine/staticize/media/articles`; `.txt`/`.md` only.

## Lessons

When a failure matches a bullet, read the named file before changing code, config
or the diagnosis: the bullet is the trigger; the file is the procedure, the
commands and the negative results.

Append one bullet, and put the body in `lessons/YYYYMMDD-<slug>.md` — the date
is the day learned; an existing file without a date prefix keeps its name. Lead
with the exact error string or command, keep it to one line and end at the file
name; the file carries the action. Delete a lesson by removing the bullet and
the file together.

- `connect to host <ip> port 22: Connection timed out` for the d3v.cn hosts `47.237.217.143`, `106.75.145.225`, `52.9.253.68` — `lessons/company-ip-whitelist.md`
- `Bad owner or permissions on /etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf` — `lessons/ssh-config-owner.md`
- `npm ERR! code EROFS` under `/home/catroll/.npm` — `lessons/npm-cache-erofs.md`
- `Node.js is not compiled with TypeScript support` — `lessons/workflow-tool-no-typescript.md`
- `[killed by signal: SIGTERM]` from `pkill -f` / `pgrep -f` — `lessons/pkill-matches-shell.md`
- `OSError: [Errno 98] Address already in use` in a test, then another app answers `415`, and that service is now down — `lessons/20261122-test-port-owner-killed.md`
- `ffprobe` prints `N/A` for `format=duration` / `stream=duration` on a file the browser just recorded — `lessons/20261122-mediarecorder-no-duration.md`
- ASR returns 200 with all scores `0`, `Display` `"."` and every word `Omission` — `lessons/20261122-asr-zero-scores-silent-input.md`
- `AudioContext.state` stays `"suspended"` in headless Firefox and analyser data is all `128` — `lessons/20261122-headless-audiocontext-suspended.md`
- Cron entry present, log says `make: uv: 没有那个文件或目录`, or a `%` in the crontab command produces no output — `lessons/cron-path-and-percent.md`
- GitHub Release `curl` exits 28 and leaves a short archive (~25 KB/s here) — `lessons/github-release-slow-truncated.md`
- ImageMagick SVG exits 0 but strokes are gone (`rsvg-convert` is not installed) — `lessons/svg-imagemagick-stroke.md`
- Driving a browser, taking a screenshot, or concluding that no browser is available — `lessons/browser-firefox.md`
- `Failed to decode request as JSON`, or a `window.confirm` that vanishes — `lessons/webdriver-empty-body.md`
- CDN assets with `responseStatus: 0`, or two unrelated files sharing one SRI hash — `lessons/firefox-cannot-fetch-cdn.md`
- "The page is slow" — `lessons/slow-page-payload-vs-path.md`
- Webhook wait ends with `seen events=[]` and the store has no row for that id — `lessons/webhook-id-mismatch.md`
- Vendor `HTTP 403` with `requested resource not granted`, while a bogus key returns `401` — `lessons/vendor-403-entitlement.md`
- `[UFW BLOCK]` in `/var/log/ufw.log` — `lessons/firewall-rule-needs-a-packet.md`
- `API key is missing` while `.env` contains the key — `lessons/env-var-is-process-not-file.md`
- Port is open, `curl` gets no bytes, uvicorn parent is alive — `lessons/uvicorn-reload-dead-child.md`
- `ImportError: cannot import name` for a name that is in the file — `lessons/importerror-stale-process.md`
- ddns-go reports `failed` while egress works — `lessons/ddns-provider-verdict.md`
- Repo nginx config has the header, `curl -sD-` does not — `lessons/vhost-repo-is-not-live.md`
- SPA deep link returns a short `200` placeholder — `lessons/nginx-prefix-swallows-spa.md`
- Logged-in app at `/app` loses the session after a visit to `/` — `lessons/cookie-path-clobber.md`
- Notification topic is glued to the front of the message — `lessons/wrapper-env-collides-with-tool.md`
- Backup file matches the live data — `lessons/backup-must-be-preimage.md`
- A rewrite of a user's text file is not byte-identical — `lessons/split-on-newline-not-splitlines.md`
- `UNIQUE constraint failed` after a delete and a restore — `lessons/tombstone-owns-unique-key.md`
- Mic turn ends in about a second with "no valid speech", or a vendor HTTP 200 is treated as success — `lessons/capture-open-transient.md`
- Capture RMS looks fine but the 300–3000 Hz band does not move — `lessons/mic-gain-speech-band.md`
- A documented option is set and nothing happens — `lessons/documented-option-unread.md`
- A failed form save redirects and the typed values are gone — `lessons/redirect-on-validation-loses-input.md`
- Files just edited show up in another commit's diff, `git status` flips between two change sets, or `git log -1` after `--amend` shows someone else's subject — `lessons/second-session-git-add.md`
- The task panel still lists work in progress after the turn finished — `lessons/todo-list-stale.md`
- A black-box UI test fails after a UI change with `textarea = "", want ...`, `expected to find "already exists"`, or `status = 422, want 303` — `lessons/20261113-ui-tests-pin-behaviour.md`
- A "drop-in" faster parser/encoder changes behaviour on edge inputs after a version bump (`jsonx result "a�b" does not preserve the raw bytes as documented` after goccy v0.10.5 → v0.12.0) — `lessons/20261113-parser-swap-differential-test.md`
- `go test ./... 2>&1 | tail -6; echo exit=$?` prints a `FAIL` package but reports `exit=0` — `lessons/20261113-pipeline-masks-exit-code.md`
- A binary grows a few MB after a perf/dependency change and `go.mod` already listed the package as `// indirect` — `lessons/20261113-go-binary-growth-ab-build.md`
- A build differs only by an environment-only flag (e.g. `GOEXPERIMENT=jsonv2`) and `go build`/`go test` without it pass silently, or two intended-different builds are byte-identical — `lessons/20261113-goexperiment-build-flag-silent-fallback.md`
- `/bin/sh: Syntax error: word unexpected (expecting ")")` on a Makefile `case` default `*)` — `lessons/20261114-dash-case-star-glob.md`
- `/bin/sh: Syntax error: end of file unexpected (expecting "fi")` after a `#` comment in a continued Makefile recipe — `lessons/20261114-make-recipe-hash-comment.md`
- `uv: 未找到命令` (`uv: command not found`) from the agent bash shell, while `ls -l ~/.local/bin/uv` shows a working pipx install — `lessons/20261114-uv-missing-from-harness-path.md`
- A commit message loses a backticked word and the shell prints `bash: 行 1: summary_explicit: 未找到命令` — `lessons/20261114-backticks-in-double-quoted-commit-message.md`
- A filename-driven pagination check reports hundreds of "too many articles per page" violations after a page-size change — `lessons/20261114-pagination-suffix-regex-date-pages.md`
- Generated-HTML row checks report sporadic "missing content" after adding rich summaries — `lessons/20261114-generated-html-row-regex-nested-li.md`
- An async script finishes downloading at 340 ms but its DOM effect lands at 5,165 ms with a later synchronous `<script src>` — `lessons/20261115-async-script-waits-for-parser-blocking.md`
- Generated YAML contains `&id001` / `*id001` anchors because one dict was reused for two nodes — `lessons/20261116-pyyaml-dump-aliases.md`
- Two runs of the same analysis disagree (989 vs 967) with no code change — `lessons/20261116-generated-input-changed-between-runs.md`
- A generator's file count shrinks on the second run (113 → 93) and its last output is deleted — `lessons/20261116-generator-selection-feedback-loop.md`
- A dependency install or download from an overseas host stalls or ends in `curl` exit 28 / `dial tcp […]:443: connect: connection timed out`, while `env | grep -i proxy` in the harness shell prints nothing — `lessons/20261115-foreign-host-network-use-proxyrc.md`
- `grep -rn … .` returns one megabyte-long line and `grep: 写入错误: 断开的管道` — `lessons/20261116-grep-over-cache-dumps.md`
- One skill CLI returns `<urlopen error [Errno 110] Connection timed out>` while a sibling script calls the same domain fine, and a retry reproduces it — `lessons/20261116-skill-cli-pre-host-default.md`
- `clawx-market-query` main CLI returns `"answers": "我暂时没有相关数据"` for a 1-year trend — `lessons/20261116-clawx-gold-history-via-backup.md`
- `ModuleNotFoundError: No module named 'config'` in a wrapper that set `os.environ["PYTHONPATH"]` before importing — `lessons/20261116-pythonpath-runtime-not-syspath.md`
- `git status --porcelain` paths come back one character short (`oody/...` instead of `woody/...`) — `lessons/20261116-porcelain-status-strip.md`
- `429` + HTML `Error - Request Blocked` from `platform.deepseek.com/api/v0/usage/...` — `lessons/20261116-deepseek-usage-waf-429.md`
- A unit that `Wants=` a retired unit keeps starting it on every timer tick (`systemctl disable` does not stop `Wants`), and `/api/status` returning the expected version does not prove *your* new slot owns the port — `lessons/20261116-bluegreen-cutover-checks.md`
- `{"success": false, "code": "429", "message": "该skill今日调用额度已达上限(50次)"}` with HTTP 200 from two different ClawX skills — `lessons/20261116-clawx-skill-daily-quota-429.md`
- acme.sh `--issue --dns dns_ali` prints `You don't specify aliyun api key and secret yet.` — `lessons/20261116-acme-ali-secret-typo.md`
- A certificate upload accepts only `.pem`/`.crt` but acme.sh produced `.cer` — `lessons/20261116-acme-pem-upload-formats.md`
- A deploy's `cp <conf>.prod <conf>` makes the headers you just verified disappear — `lessons/20261116-materialize-after-sync.md`
- `Cannot send a request, as the client has been closed` from the second iteration of a loop that calls `TestEngine().execute()` — `lessons/20261116-client-closed-between-executions.md`
- `panic: read /init_data.json: is a directory` on a freshly recreated container — `lessons/20261117-compose-relative-mount-path.md`
- A container disappears or flips project after deploying an unrelated stack (`com.docker.compose.project` is the shared `.env` value, not the compose file's `name:`) — `lessons/20261117-compose-project-name-collision.md`
- Bare-domain HTTP times out while `https://` works, `nginx -T` already has `return 301`, and `curl -H 'Host: …' http://127.0.0.1/` returns 301 — `lessons/20261117-public-port-80-blocked-cloud-firewall.md`
- Fact-checking "is this secret readable?" — `lessons/20261117-printing-secret-material.md`
- A document states a count or date range you got by eyeballing a list (`7 个外部脚本`, `2017–2018 旧公司`, `2014 年文档`) — `lessons/20261117-doc-facts-must-be-measured.md`
- `UserWarning: Glyph … missing from font(s) DejaVu Sans` in a matplotlib chart while savefig exits 0 — `lessons/20261117-matplotlib-cjk-font-tofu.md`
- A hand edit to a config file takes effect only after the daemon restarts (`scan` reporting `deleted: 63` while the same rows still show `indexed`) — `lessons/20261117-config-edit-needs-reload.md`
- `GET /path` answers 200 after `POST 127.0.0.1:2019/load` but 404s / loses TLS after `systemctl restart caddy` — `lessons/20261117-admin-api-config-runtime-only.md`
- User asks what the homepage control token is (`控制令牌`, `CONTROL TOKEN 是什么`, `那个令牌在哪`) — `lessons/20261117-homepage-control-token-answer.md`
- `read_image` returns `model "deepseek-v4-flash" does not declare image input` — `lessons/20261117-read-image-requires-vision-model.md`
- `libreoffice --headless --convert-to txt file.doc` exits 1 and `strings -el` shows only metadata — `lessons/20261117-legacy-doc-text-via-olefile.md`
- `file <capture>: data` / `read` reports `binary file` or `invalid UTF-8 text` after a collection script read `/proc/*/cmdline` — `lessons/20261118-proc-cmdline-nul-bytes.md`
- `ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password host true` exits 0 after password auth was disabled — `lessons/20261118-ssh-controlmaster-hides-auth-change.md`
- `systemctl mask <unit>` → `Failed to mask unit: File /etc/systemd/system/<unit> already exists.` — `lessons/20261118-mask-cannot-shadow-etc-unit.md`
- YAML `ParserError: expected <block end>, but found '<scalar>'` on a line after a description — `lessons/20261118-yaml-plain-scalar-hash.md`
- `harden.sh report` → `ERROR: no run found` after `rsync -a --delete <tool>/ host:/opt/<tool>/` — `lessons/20261118-rsync-delete-wipes-runtime-records.md`
- `permitlisten=127.0.0.1:15232` in `authorized_keys` gives a silent `Permission denied (publickey)` — `lessons/20261118-authorized-keys-permitlisten-quotes.md`
- `sudo: interactive authentication is required` from `sudo -n ufw status` / `sudo -n ss -lntp` — `lessons/20261118-sudo-password-no-privilege.md`
- `certificate not found: /root/.acme.sh/...` when the same installer worked as `bash … render` — `lessons/20261118-sudo-resets-home.md`
- `AttributeError: '_StubIndex' object has no attribute 'search_many'` from inside a test nobody edited — `lessons/20261118-test-stub-missing-method.md`
- `openssl s_client -connect 127.0.0.1:443 -servername <host>` shows a certificate whose `notAfter` is older than the renewed `~/.acme.sh/<domain>_ecc/fullchain.cer` — `lessons/20261118-cert-copy-without-reload.md`
- Replacing a whole row with `str.replace` in a shared file deletes every match, and a concurrently added row becomes a duplicate; `make <target>` printing `Nothing to be done` after a recipe add means the edit did not land — `lessons/20261118-shared-file-concurrent-rewrite.md`
- `VAR: 未绑定的变量` printed only under `sudo`, while `bash -n` and a non-root dry run pass — `lessons/20261118-unbound-var-root-only-path.md`
- A backup/collector run reports success and has a directory per service, but its own restore-side check says `54 differ` / `cmp: …config.yaml: 是一个目录` — `lessons/20261118-backup-verify-with-check-mode.md`
- `install-caddy.sh install` succeeds while the `forward_auth` backend is down → every gated host answers 502, including the auth portal — `lessons/20261118-forward-auth-gate-before-backend.md`
- `install-*.sh` stops silently right after its last `==>` line (status 1, no error) — `lessons/20261118-shell-helper-return-one-aborts.md`
- A code change plus `systemctl restart` behaves exactly like the old build (`ExecStart` points at a binary, not `go run`) — `lessons/20261118-unit-runs-prebuilt-binary.md`
- A "logout" behind `forward_auth` lands on a disabled-login page and the next request is still authenticated — `lessons/20261119-app-logout-behind-forward-auth.md`
- An app behind `forward_auth` still shows its own login page (or `curl -H 'Remote-User: admin' https://<host>/api/...` returns 200) — `lessons/20261119-gate-page-not-api.md`
- Upstream receives `Remote-User: {http.reverse_proxy.header.Remote-User}` and an app-side `header == ""` check treats the placeholder as a real user — `lessons/20261119-caddy-copy-headers-placeholder.md`
- The proxy sends `Remote-User` (visible in its debug log) but a loopback-only trust check still 401s, while the same header works with a direct `curl` — `lessons/20261119-uvicorn-proxy-headers-hide-peer.md`
- `forward_auth` with an optional-session `handle_response` gives a bare `502` once the auth service stops, and the route never runs (`reverseproxy.statusError ... connection refused`) — `lessons/20261119-forward-auth-connection-error-skips-handle-response.md`
- `kill "$(cat app.pid)"` reports the process stopped but `ss -ltnp` still shows the old test server and the browser proves the previous behaviour — `lessons/20261119-background-subshell-pid-leaves-test-server.md`
- Markdown rebuilt by splitting on `^## ` glues each heading to the previous paragraph; Markdown still renders — `lessons/20261120-markdown-section-rebuild-blank-lines.md`
- Two screens report the same consumption as ¥92.87 and ¥12.72 (ratio 7.3); `quota / 500000` may already be yuan — `lessons/20261120-same-quota-two-money-amounts.md`
- `make check` reports `not gofmt-ed: .cache/...` from a temporary test fixture even though the module's source is formatted — `lessons/20261120-gofmt-scans-cache-fixtures.md`
- Two icon buttons that must sit side by side split across flex lines in a wrapping toolbar (`theme top=40`, `settings top=88` at a 280px toolbar) — `lessons/20261120-flex-wrap-splits-icon-actions.md`
- A locally computed ETag sent as `If-None-Match` to a provider that supplied none makes `If-Modified-Since` ignored and forces a 200/full download — `lessons/20261120-synthetic-etag-blocks-ims.md`
- tinyauth bootstrap fails with `invalid app url` when `TINYAUTH_APPURL` is `localhost` or an IP; use a loopback domain (`lvh.me`) — `lessons/20261120-tinyauth-local-appurl.md`
- `git filter-repo` drops `rm --cached`+gitignored files from the working tree and prunes the old objects (`git show <old>:<path>` → `无效的对象名`) — `lessons/20261120-filter-repo-drops-untracked-files.md`
- `npm WARN EBADENGINE` after `sudo npm install -g` for a package the fnm-managed Node satisfies, or an upgrade that reports success while the service still runs the old version — `lessons/20261120-sudo-npm-fnm-node.md`
- A failure report proposes a DSL change ("status 断言 200") but the YAML already asserts 400, or cites a case/file the repo does not have — `lessons/20261120-report-edits-verify-against-artifact.md`
- A collector's output starts later than the source history and the gap is written off as "old records have no date" — `lessons/20261120-collector-start-date-vs-source.md`
- A form handler rejects every save with `must be a whole number` because it parses a field the template never posts — `lessons/20261121-form-validation-unposted-fields.md`
- A doc-edit script prints `<label>: 0` after several edits and none of that file's changes landed — `lessons/20261121-doc-script-anchor-abort-loses-edits.md`
- PocketBase multi-relation `field ?= "id"` matches nothing; use `field.id ?= "id"` — `lessons/20261121-pocketbase-multi-relation-filter.md`
- `connect to host documentation.ubuntu.com port 443` times out with `curl: (28)` through `~/.proxyrc`, while the same URL returns 200 with the proxy variables unset — `lessons/20261121-proxy-breaks-some-hosts.md`
- Untracked `__pycache__/` appears in a repo after a delegated review ran its `.py` files — `lessons/20261121-review-subagent-pycache.md`
- A root-owned global CLI fails with `EACCES … mkdir '…/node_modules/<pkg>/node_modules/flat-cache/.cache'` and the build still looks partly done — `lessons/20261121-honkit-global-cache-eacces.md`
- A repo is called private because `curl` returned 200 or the remote is SSH, while the logged-out page lists every file — `lessons/20261121-repo-visibility-check.md`
- `apt-cache policy <pkg> | grep 'Candidate:'` is empty for every package on a zh_CN host while the same command with `LC_ALL=C` works — `lessons/20261121-apt-output-locale.md`
- `local path=…` in a zsh function clobbers PATH, `local status` is read-only, and aliases are baked into function bodies at definition — `lessons/20261121-zsh-function-traps.md`
- xorriso repack of a hybrid ISO returns 32 / `Read start address ... larger than number of readable blocks`, or `-boot_image any keep` leaves a stale MBR — `lessons/20261121-xorriso-keep-vs-replay.md`
- `sqlite3 live.db ".restore backup.db"` exits 0 and leaves an empty database (and truncates the backup source) — `lessons/20261121-sqlite-dot-restore-not-copy.md`
- Two planned tasks share files and the first task's changes show up in the second task's commit — `lessons/20261122-task-boundary-commit.md`
