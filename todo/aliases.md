# StdEnv aliases — TODO

> Project: ~/Projects/StdEnv/aliases
> Prefix: AL
> Next ID: AL-050
> Updated: 2026-11-21

## Theme: review follow-up (2026-11-21)

Source: repo review in this session; commit `0e081f1` already landed the
credential-free P0 hardening (ssh host-key policy, removed v2inst/getgo/webinit,
docker cache). Credential bodies, key backups and history rewrite are
deliberately out of scope for now.

### Batch B20261121-p1 — fix confirmed P1 defects (target 2026-11-22, done)

- [x] **AL-001** [P1][B20261121-p1] common.sh: killjobs brace range + empty xargs -> done 2026-11-21 (commit 3369184)
  - Done when: `for` loop uses arithmetic and no jobs exits cleanly
  - Ev: bash -c with 0/2 jobs
- [x] **AL-002** [P1][B20261121-p1] common.sh: retry usage returns, runs argv safely -> done 2026-11-21 (commit 3369184)
  - Done when: no-arg call returns 1; quoted args survive
  - Ev: `retry 1 printf '%s\n' "a b"` prints one line
- [x] **AL-003** [P1][B20261121-p1] common.sh: clean removes non-empty __pycache__ -> done 2026-11-21 (commit 3369184)
  - Done when: a populated `__pycache__` is gone, rc=0
  - Ev: temp tree test
- [x] **AL-004** [P1][B20261121-p1] common.sh: dirtar/gitrepo guard cd/mkdir -> done 2026-11-21 (commit 3369184)
  - Done when: bad path returns 1 without touching cwd
  - Ev: subshell tests
- [x] **AL-005** [P1][B20261121-p1] common.sh: mod644 stops chmod on *.key; safe copyqclear/fmvsc/parents -> done 2026-11-21 (commit 3369184)
  - Done when: `.key` files keep their mode; no fixed /tmp list
  - Ev: temp tree + mktemp usage
- [x] **AL-006** [P1][B20261121-p1] common.sh: sshconfig-gen writes atomically -> done 2026-11-21 (commit 3369184)
  - Done when: import failure leaves the old config intact
  - Ev: stub python failing
- [x] **AL-007** [P1][B20261121-p1] script.sh: log filename, TTY, exit, printf, startnewlog -> done 2026-11-21 (commit d50388f)
  - Done when: filename has date+pid+tty; ending recording keeps the shell; `-v` gone
  - Ev: source in subshell
- [x] **AL-008** [P1][B20261121-p1] work.sh: confirm_result + iptables_clear actually flush -> done 2026-11-21 (commit 8e7e6c0)
  - Done when: y flushes, n does not; prompt not captured
  - Ev: stubbed sudo
- [x] **AL-009** [P1][B20261121-p1] work.sh: ipforward arg checks and VPN_IP handling -> done 2026-11-21 (commit 8e7e6c0)
  - Done when: empty $1/$2 no longer flushes; CIDR stripped; tun0 down returns
  - Ev: stub command log
- [x] **AL-010** [P1][B20261121-p1] work.sh: current_ip, SVN_AUTH_PATH, duplicate local -> done 2026-11-21 (commit 8e7e6c0)
  - Done when: tty grep expands; svn path under $HOME; one mailUsersFile
  - Ev: grep/line check
- [x] **AL-011** [P1][B20261121-p1] work.sh: dbsync/domainchk locking -> done 2026-11-21 (commit 8e7e6c0)
  - Done when: lock created and removed; dbsync does not re-source from wrong dir
  - Ev: temp dir run
- [x] **AL-012** [P1][B20261121-p1] work.sh: findip semantics; drop dead confirm_action -> done 2026-11-21 (commit 8e7e6c0)
  - Done when: 1-arg is keyword, 2-arg project+keyword; zsh-safe
  - Ev: usage checks
- [x] **AL-013** [P1][B20261121-p1] git.sh: myclone depth override -> done 2026-11-21 (commit 656306f)
  - Done when: `myclone <repo> <depth>` uses depth
  - Ev: parse check / local repo
- [x] **AL-014** [P1][B20261121-p1] git.sh: ggg commits only the named path -> done 2026-11-21 (commit 656306f)
  - Done when: pre-staged files do not ride along; failed add returns 1
  - Ev: temp repo
- [x] **AL-015** [P1][B20261121-p1] git.sh: has_changes covers staged/untracked; fast_merge checks steps -> done 2026-11-21 (commit 656306f)
  - Done when: staged-only and untracked-only are "dirty"
  - Ev: temp repo
- [x] **AL-016** [P1][B20261121-p1] git.sh: create_local_branch IFS scoped, no git br dependency -> done 2026-11-21 (commit 656306f)
  - Done when: IFS unchanged after call; branches created with switch --track
  - Ev: subshell check
- [x] **AL-017** [P1][B20261121-p1] git.sh: `g` no longer shadows git; sourcetree/gi portable -> done 2026-11-21 (commit 656306f)
  - Done when: `g=git`; SourceTree only on Windows; gi uses live endpoint
  - Ev: alias/type checks
- [x] **AL-018** [P1][B20261121-p1] git.sh: gsmart2 keeps D/R; _git_path quoting; gsmart3 user path -> done 2026-11-21 (commit 656306f)
  - Done when: paths with quotes/spaces accepted; wsl mapping via wslpath
  - Ev: temp repo
- [x] **AL-019** [P1][B20261121-p1] dev.sh: newfile1m/sdir/djlocales -> done 2026-11-21 (commit 4675410)
  - Done when: 10M file is 10 MiB; no-match find does not block; no-arg djlocales refuses
  - Ev: temp dir
- [x] **AL-020** [P1][B20261121-p1] dev.sh: codesync2 push --all, mergeBr, find loops -> done 2026-11-21 (commit 4675410)
  - Done when: no automated push; branch param used; paths with spaces safe
  - Ev: static review + stub git
- [x] **AL-021** [P1][B20261121-p1] ffmpeg.sh: vcut exit status, arg count, extension -> done 2026-11-21 (commit 63f2d62)
  - Done when: failed ffmpeg returns non-zero; 5+ args refused; .mkv named correctly
  - Ev: stub ffmpeg
- [x] **AL-022** [P1][B20261121-p1] vagrant.sh: jq string+number, missing return, quoting -> done 2026-11-21 (commit 967acc8)
  - Done when: vgtsearch prints results; vgtadd refuses incomplete args
  - Ev: stub jq/vagrant
- [x] **AL-023** [P1][B20261121-p1] markjour.sh: MJPY works in bash and zsh -> done 2026-11-21 (commit 63bc0e2)
  - Done when: bash prints `uv run python`
  - Ev: bash/zsh expansion test
- [x] **AL-024** [P1][B20261121-p1] python.sh: WORKON_HOME, requirements typo, PATH guard -> done 2026-11-21 (commit 9eb2d0b)
  - Done when: $HOME path; requirements.txt; pyenv absent adds nothing
  - Ev: stub HOME
- [x] **AL-025** [P1][B20261121-p1] proxy.sh: export no_proxy, socks5h, rm -f, gsettings guard -> done 2026-11-21 (commit aea16be)
  - Done when: .proxyrc exports no_proxy/NO_PROXY; missing file tolerated
  - Ev: temp HOME
- [x] **AL-026** [P1][B20261121-p1] main.sh: shell detection, LOG order, quotes, idempotence, debug switch -> done 2026-11-21 (commit 7c3b340)
  - Done when: no /proc error, double source guarded, `_ALIASES_DEBUG` gates timing
  - Ev: zsh/bash source twice
- [x] **AL-027** [P1][B20261121-p1] hardware.sh: free/top/uptime parsing, `::`, single samples -> done 2026-11-21 (commit e091e42)
  - Done when: zh_CN locale yields numbers; stubs are no-ops
  - Ev: live run
- [x] **AL-028** [P1][B20261121-p1] email-ipv6: MX split, SRV lookup, exception handling -> done 2026-11-21 (commit c027637)
  - Done when: each MX host checked; SRV target used; timeouts caught
  - Ev: gmail.com run
- [x] **AL-029** [P1][B20261121-p1] tmux.sh: tmate.conn copies without xargs -> done 2026-11-21 (commit 7e40f87)
  - Done when: content with quotes/apostrophes intact; pbcopy fallback
  - Ev: fake file
- [x] **AL-030** [P1][B20261121-p1] java.sh/nodejs.sh: JAVA_HOME guard, single nvm load -> done 2026-11-21 (commit f740c27)
  - Done when: absent paths leave env untouched; nvm sourced once
  - Ev: stub HOME
- [x] **AL-031** [P1][B20261121-p1] network.sh: netpps/netspeed cleanup -> done 2026-11-21 (commit 0cba330)
  - Done when: unused IF gone, arithmetic builtin, usage names function
  - Ev: bash -n + static

### Batch B20261121-p2 — engineering guard rails (target 2026-11-23, done)

- [x] **AL-032** [P1][B20261121-p2] Makefile with help/check/lint/test -> done 2026-11-21 (commit 1da489d)
  - Done when: `make`, `make help`, `make check`, `make test` pass from a clean checkout
  - Ev: command output
- [x] **AL-033** [P1][B20261121-p2] install path: guarded rc block + idempotent script -> done 2026-11-21 (commit 1da489d)
  - Done when: running install twice leaves one source line
  - Ev: temp HOME
- [x] **AL-034** [P1][B20261121-p2] README rewrite + docs/operations.md (deps, platforms, load order) -> done 2026-11-21 (commit 49b443a)
  - Done when: README says what it is, install, deps, docs link; operations holds internals
  - Ev: files present, links resolve
- [x] **AL-035** [P2][B20261121-p2] lint/CI config (shellcheck error level, pre-commit) -> done 2026-11-21 (commit 615705a)
  - Done when: `make lint` runs shellcheck when installed; config committed
  - Ev: make lint
- [x] **AL-036** [P2][B20261121-p2] .gitignore + pyproject scope note + file modes -> done 2026-11-21 (commit 9844b95)
  - Done when: `__pycache__/`, `*.pyc` ignored; pyproject says formatter-only
  - Ev: git status after python -c import

### Batch B20261121-p3 — cleanup and dedupe (target 2026-11-30, done)

- [x] **AL-037** [P2][B20261121-p3] remove dead/unloaded files; mark FLOZz scripts run-only -> done 2026-11-21 (commit 9ac0e8f)
  - Done when: c.sh/color.sh/pref.sh/go.sh/zoxide_* gone or justified; no dangling load entries
  - Ev: main.sh load list + grep
- [x] **AL-038** [P2][B20261121-p3] dedupe hist.top10..100 -> done 2026-11-21 (commit a47eb91)
  - Done when: one awk program, same output for the five names
  - Ev: alias dump
- [x] **AL-039** [P3][B20261121-p3] remove duplicated color helpers -> done 2026-11-21 (commit 9ac0e8f)
  - Done when: one implementation remains
  - Ev: grep
- [x] **AL-040** [P2][B20261121-p3] collapse 48 db helper functions into a dispatcher -> done 2026-11-21 (commit fda3ce1 6b01290)
  - Done when: stub-based before/after output is identical
  - Ev: diff of generated commands
- [x] **AL-041** [P3][B20261121-p3] single email-ipv6 implementation -> done 2026-11-21 (commit 13a7c28 79aaa33)
  - Done when: shell version delegates or is removed; dependency documented
  - Ev: run both
- [x] **AL-042** [P3][B20261121-p3] repo split proposal (portable vs work/private) -> done 2026-11-21 (commit 4c55da9)
  - Done when: written plan with paths and migration order
  - Ev: docs file

### Batch B20261121-followup — owner feedback (2026-11-21, done)

- [x] **AL-044** [P2][B20261121-followup] Restore c.sh/color.sh and load them -> done 2026-11-21 (commit 2ccc18f)
  - Done when: both files are tracked, sourced from main.sh, and fastrun.c returns compiler/program status
  - Ev: `fastrun.c ok.c` / `bad.c` in zsh and bash; `make test`
- [x] **AL-045** [P2][B20261121-followup] Remove sync.sh (private-key backup) -> done 2026-11-21 (commit 2ccc18f)
  - Done when: sync.sh is gone, not in the loader, and docs no longer reference it
  - Ev: grep for sync.sh/backup.ssh2; make check

### Batch B20261121-layout — local category directories (2026-11-21, done)

- [x] **AL-046** [P2][B20261121-layout] Split tracked helpers into lib/ and profiles/ -> done 2026-11-21 (commit a45bf32)
  - Done when: portable files live in lib/, host/employer files in profiles/, and the explicit load order still works
  - Ev: alias/function snapshot identical before/after in zsh and bash; `make check`/`make test`; clean archive without extras passes
- [x] **AL-047** [P2][B20261121-layout] Load machine-local overrides from $ALIASES_EXTRA -> done 2026-11-21 (commit a45bf32)
  - Done when: extras/*.sh is sourced last, missing dir is a no-op, and personal.sh moved there
  - Ev: temp override dir; personal.sh byte-identical to the old sync file

- [x] **AL-048** [P2][B20261121-layout] Put extras at ~/Documents/Mine/Sync/aliases-extras -> done 2026-11-21 (commit 01ad342)
  - Done when: ALIASES_EXTRA defaults to the sync directory, personal.sh lives there, and no extras/ is tracked
  - Ev: `git ls-files extras` is empty; clear archive `make check`/`make test`; `$ALIASES_EXTRA` prints the sync path

- [x] **AL-049** [P3][B20261121-layout] Move standalone tools into tools/ -> done 2026-11-21 (commit 6580ca4)
  - Done when: email-ipv6.* and the two colour demos live in tools/, root keeps main.sh/nodejs.sh, and references are updated
  - Ev: `make check` scans tools/; `tools/email-ipv6.sh example.com` runs; clean archive passes

### Batch B-backlog — unplanned (done)

- [x] **AL-043** [P2][B-backlog] credentials out of the repo and history rewrite [user] -> dropped 2026-11-21 (owner: resources deleted, remaining values are stale placeholders; no rewrite)
  - Done when: user rotates secrets and decides on public visibility; then move to personal.sh
  - Ev: user action
