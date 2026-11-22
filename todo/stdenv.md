# StdEnv/stdenv (stdenv) — TODO

> Project: `~/Projects/StdEnv/stdenv` (public remote: `git@gitee.com:stdenv/stdenv`)
> Prefix: ST
> Next ID: ST-023
> Updated: 2026-11-21

## Theme: repo review remediation (2026-11-21)

Review outcome: the repo is now a reproducible book plus a documented set of
placeholder credentials and scripts. The 2026-11-21 remediation landed; what
remains is one clean-container package regression (ST-007), enabling the Gitee
Go pipeline (ST-014), and the recurring/user decisions (ST-017, ST-019).

### Batch B20261121-p0 — credentials cleanup (target 2026-11-21, done)

- [x] **ST-001** [P1][B20261121-p0] Remove the hardcoded Aliyun key from `scripts/cloud/003.acme.sh` -> done 2026-11-21 (commit 7a61f6c; `grep -R LTAI` on the tree is empty)
  - Done when: the script reads `Ali_Key`/`Ali_Secret` from the environment, no `LTAI…` value remains in the tree, and a comment records that the old key was revoked on 2026-11-21
  - Ev: `grep -R LTAI --exclude-dir=.git .`; commit hash
- [x] **ST-002** [P1][B20261121-p0] Mark example passwords as placeholders -> done 2026-11-21 (commit 94d11e6; values unchanged)
  - Done when: `001.install.md:9-10`, `stdenv.sh:8`, `007.mysql.md:3`, `cloud/002.mysql.sql:3` each carry an explicit "placeholder / example only" note; the values stay unchanged
  - Ev: grep for the note; diff shows values untouched
- [x] **ST-003** [P1][B20261121-p0] Align the git credential-helper guidance with this machine -> done 2026-11-21 (commit 029350a; global helper is empty)
  - Done when: `002.git.md` and `002.git.sh` no longer recommend `credential.helper store`; they record that this machine has no global helper and uses SSH remotes (libsecret only when HTTPS is needed)
  - Ev: `git config --global --get credential.helper` is empty; docs match
- [x] **ST-004** [P1][B20261121-p0] Add `SECURITY.md` and record the residual secret risk -> done 2026-11-21 (SECURITY.md; tree scan clean, history hit allowlisted by fingerprint)
  - Done when: the revoked key in history is documented, the placeholder policy is stated, and a tree/history scan result is recorded
  - Ev: `gitleaks detect --log-opts=--all` (expected: old key hits, documented); tree scan clean
- [-] **ST-005** dropped 2026-11-21 (reason: no history rewrite or force-push; key already revoked per user)

### Batch B20261128-fix — correct the content and make it build (target 2026-11-28, open)

- [x] **ST-006** [P1][B20261128-fix] Fix silently wrong shell snippets -> done 2026-11-21 (commits 25a6df9, ad1f22b; bash -n/shellcheck clean)
  - Done when: `003.ssh.md:50-54` (`echo > config <<EOF` writes nothing), `006.python.md:92-96` (`echo >> .bashrc <<EOF`), `005.shell.md:67-68` (`$INIT_COST_TIME`, `main.s`), `stdenv.sh:88` (missing `sudo`), `:14-19` (`confirm` recursion/inverted return), `001.install.md:206` (`apt remote`) are corrected and each command was run
  - Ev: commands executed in a container; output recorded in the PR/report
- [x] **ST-007** [P1][B20261128-fix] Refresh package names and versions for Ubuntu 24.04/26.04 -> done 2026-11-21 (commits 94d11e6, fa1b506, ad1f22b, 3dba39a; `apt-get -s install` resolved every refreshed package on 26.04; no clean-container run, registry pull blocked)
  - Done when: `001.install.md:66,104-112`, `stdenv.sh:110-120`, `201.input-method.md` install on a clean 26.04 container; dead mirrors/registries (`taobao`, `daocloud`, `docker-cn`, `azk8s`, `wps-community`, `mirrors.sohu`) replaced; Python 2 / MySQL 5.7 / Fedora 26 references removed or archived
  - Ev: `docker run ubuntu:26.04` transcript for each command block
  - Audit 2026-11-21: 167 unique apt names across the scripts, 90 installed, 77 missing (45 still installable on 26.04, 32 gone/renamed); 280 of 342 manual packages are absent from the scripts. Inventory and staged plan (P0 fixes / P1 installs / P1b machine-to-script / P2 non-apt / P3 dedupe) in `~/.cache/stdenv-audit/20261121/REPORT.md`; scope awaiting user confirmation.
- [x] **ST-008** [P1][B20261128-fix] Remove dangerous and policy-violating instructions -> done 2026-11-21 (commits 1875906, f9f8ca4)
  - Done when: KMSpico (`windows/basic.md:13`), `--skip-grant-tables` (`007.mysql.md:106`), `ufw allow mysql` (`:9`), `Amazon-linux`-style open grants (`cloud/002.mysql.sql:3`), `Host * User root` (`stdenv.sh:133`, `003.ssh.md:52`), `sudo rm /home/$USER` (`windows11/README.md:78`), `credential.helper store` (`002.git.md:105`, `002.git.sh:34`) are gone or replaced with safe guidance
  - Ev: `grep` for each pattern returns nothing
- [x] **ST-009** [P1][B20261128-fix] Rewrite README and complete SUMMARY -> done 2026-11-21 (fde3928, d537e8e; 47 pages, four missing pages render)
  - Done when: README states what/why/quick start/support matrix (24.04/26.04) instead of a raw apt list; `windows11/README.md`, `macos/README.md`, `windows/pycharm.md`, `windows/sublime.md` are in SUMMARY or deleted; `honkit build` renders every listed page
  - Ev: `_book/*.html` count matches SUMMARY; README reviewed against the project README rule
- [x] **ST-010** [P1][B20261128-fix] Add `Makefile` with `make help`, pinned Honkit, and checks -> done 2026-11-21 (f754c3d; Honkit 7.0.1, fresh clone check/book pass)
  - Done when: `make help` lists build/check/book/clean; `honkit@6.2.5` is a local devDependency (global install fails `EACCES` on `flat-cache/.cache`); `make check` runs markdownlint, shellcheck, link check, and a secret scan; `make book` builds clean on a fresh clone
  - Ev: fresh clone run of `make`, `make check`, `make book`
- [x] **ST-011** [P1][B20261128-fix] Harden the shell scripts -> done 2026-11-21 (5dc289a; shellcheck clean, executable bits set)
  - Done when: every `.sh` has a shebang, `set -euo pipefail`, a `--dry-run` for mutating actions, `chmod +x`, and no interactive infinite loop (`check_vcs_key.sh`); `001.install.sh:11-13` no longer stores ECDSA as `id_rsa` nor `chmod 0400` the public key
  - Ev: shellcheck clean; dry-run on this host
- [x] **ST-012** [P1][B20261128-fix] Repo hygiene -> done 2026-11-21 (bf7ee5d, de5bc83, 8b0eda4; status clean, covers removed, origin/old ref deleted)
  - Done when: the pending `002.git.md` and `100.others.md` edits are committed or reverted, `origin/old` (2018, merged) is deleted, unused `cover*.jpg` are removed or wired into `book.json`, and `git status` is clean
  - Ev: `git status`, branch list, `grep -r cover`

### Batch B20261212-structure — restructure and automate (target 2026-12-12, open)

- [x] **ST-013** [P2][B20261212-structure] Split docs from executable scripts -> done 2026-11-21 (fde3928; scripts/ split, book kept at root so Gitee renders README/SUMMARY)
  - Done when: `docs/` holds the book, `scripts/` holds runnable setup, legacy 18.04 content moves to `docs/archive/`, and root no longer mixes `NNN.md` with `.sh`
  - Ev: new tree; SUMMARY updated
- [!] **ST-014** [P2][B20261212-structure] Add CI on every push -> pipeline added 2026-11-21 (3fc9d65); why: needs Gitee Go enabled and one push-triggered run, which the user must do
  - Done when: Gitee Go (or a mirror) runs secret scan, markdownlint, shellcheck, `make check`, and `make book`; failures block merge
  - Ev: one green and one red pipeline run
- [x] **ST-015** [P2][B20261212-structure] Add `SECURITY.md`, `CONTRIBUTING.md`, and `docs/operations.md` -> done 2026-11-21 (fde3928, 03f2424)
  - Done when: secret-reporting path, commit convention, build/publish steps, and "last verified" policy are documented
  - Ev: files exist and are linked from README
- [x] **ST-016** [P2][B20261212-structure] Establish one source of truth -> done 2026-11-21 (3dba39a, 03f2424; matrix in docs/operations.md)
  - Done when: each duplicated block (README vs `001.install.md`, `011.vscode.md` vs `.sh`, `windows/ide.md` vs `pycharm.md`/`sublime.md`, `stdenv.sh` vs `cloud/001.init.sh`) has one owner and the others link to it
  - Ev: duplication matrix in `docs/operations.md`

### Batch B-backlog — unplanned (open)

- [ ] **ST-017** [P3][B-backlog] Quarterly link/mirror/version freshness pass
  - Done when: dead links and EOL versions are rechecked every quarter, with a "last verified YYYY-MM-DD" line per page
- [x] **ST-018** [P3][B-backlog] Fix stale prose and stub pages -> done 2026-11-21 (b3b8d07)
  - Done when: `windows/tips.md:13,17-18`, `windows/xshell.md:32-34`, `windows/basic.md:26,173-193`, `windows/example.md:40`, `204.ide.md:12`, `012.nfs.md:22`, `209.golang.md`, `windows/linux-wsl.md`, `windows/group-policy.md` are completed or removed
- [ ] **ST-019** [P3][B-backlog][user] Decide public personal data and language policy
  - Done when: real name, emails, hostnames, Windows username, and internal hostnames are either accepted as public or sanitized; content language (Chinese) vs code/comments (English) is recorded
- [x] **ST-020** [P3][B-backlog] Adopt a commit message convention -> done 2026-11-21 (CONTRIBUTING.md; commits since 7a61f6c explain why)
  - Done when: new commits explain why (not `Update <file>`), and the convention is in CONTRIBUTING
- [-] **ST-021** [P2][B20261212-structure] Record the non-apt toolchain in the repo -> deferred 2026-11-21 (reason: audit scope not confirmed; versions are machine-specific, see ~/.cache/stdenv-audit/20261121/REPORT.md)
  - Done when: `013.tools.md` + `013.tools.sh` list the pipx/go/npm/snap/standalone tools and pinned versions from the 2026-11-21 inventory; `check-tools.sh` verifies each command and version on a fresh host
  - Ev: run `013.tools.sh` on a clean 26.04 container; `check-tools.sh` reports 0 missing
- [-] **ST-022** [P2][B-backlog] Remove duplicate and broken PATH tool entries -> deferred 2026-11-21 (reason: machine-level PATH cleanup belongs to the aliases repo, not this documentation repo)
  - Done when: `uv`/`ruff`/`govulncheck` resolve to one version per shell, `~/.python/bin/pytest` is fixed or removed, and `command -v` checks for both bash and zsh pass
  - Ev: `bash -lc` and `zsh -ic` version table; `pytest --version` works in both
