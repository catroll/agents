# TOTP Authenticator (totp) — TODO

> Project: tools/totp
> Prefix: TOTP
> Next ID: TOTP-017
> Updated: 2026-11-20

## Theme: FreeOTP JSON TOTP page behind the existing tinyauth gate

### Batch B20261120-totp — first version (target 2026-11-20, wip)

- [x] **TOTP-001** [P1][B20261120-totp] Add the one-Go-file TOTP service and single HTML page
  - Done when: `bin/totp -config ...` serves `/`, `/api/totp`, `/healthz`; RFC 6238 vectors pass
  - Ev: `make check`; 18 RFC vectors; real HTTP; headless Firefox -> done 2026-11-20
- [x] **TOTP-002** [P1][B20261120-totp] Add the tinyauth Caddy route and homepage entry
  - Done when: rendered Caddyfile adapts; unauthenticated request 302s to the portal
  - Ev: `caddy adapt`; temporary Caddy + real tinyauth -> done 2026-11-20
- [ ] **TOTP-003** [P1][B20261120-totp][user] Install the Caddy block and run the service
  - Done when: `https://totp.eqr.hosts.d3v.cn/` 302s to the login page, then serves the page after login
  - Ev: `sudo scripts/install-caddy.sh install` in `tools/homepage`; start `bin/totp` under systemd/supervisor; checks in `tools/totp/docs/operations.md` §6.4
  - Progress 2026-11-20: Caddy block installed and 302 verified; `totp.service` transient restarted with the JSON version; reference backup is active. Domain changed to otp; re-run the Caddy installer. Persistent unit remains.
- [x] **TOTP-004** [P1][B20261120-totp] Add search, URL filter, theme toggle and multi-config management
  - Done when: `?q=` filters the page, theme persists, config paths can be added/selected/edited/removed with the example locked
  - Ev: state API tests; headless Firefox; `make check` -> done 2026-11-20
- [x] **TOTP-005** [P2][B20261120-totp] Keep the theme and settings icons on one line
  - Done when: a constrained toolbar keeps both icons at the same top, with settings to the right
  - Ev: reproduced theme top=40 / settings top=88 at toolbar width 280px; `.actions` nowrap group keeps both at the same top for 100–300px -> done 2026-11-20
- [x] **TOTP-006** [P1][B20261120-totp] Read FreeOTP JSON backups and map issuer logos
  - Done when: the reference backup parses, optional fields work, and issuer logos resolve
  - Ev: 22 records / 21 logo URLs all 200; JSON error paths; headless Firefox 22 images loaded -> done 2026-11-20
- [x] **TOTP-007** [P2][B20261120-totp] Keep search and both icons on one responsive row
  - Done when: search, theme and settings share a top at 280–1200px with no overflow
  - Ev: 280/320/390/760/1200px measured; 280px search ~150px -> done 2026-11-20
- [x] **TOTP-008** [P2][B20261120-totp] Compact the page and credential cards
  - Done when: card height drops to about 100–106px and name/meta truncation keeps a tooltip
  - Ev: 327×106 at 1200px, 354×102 at 390px, 269×102 at 280px; no code-row overflow -> done 2026-11-20
- [x] **TOTP-009** [P2][B20261120-totp] Add a filtered OTP API
  - Done when: `GET /api/otp?issuer=&account=` returns matching entries with codes and no secrets
  - Ev: 22 all / 2 SendCloud / 1 Binance / 3 NINEDOORS / 1 Cloudflare+kwicoo / empty no-match -> done 2026-11-20
- [x] **TOTP-010** [P2][B20261120-totp] Four-column compact cards with click-to-copy
  - Done when: desktop shows four cards per row, cards are shorter, and no Copy button remains
  - Ev: 4 columns at 1024/1200; 244x89 card; click/Enter copies and shows toast -> done 2026-11-20
- [x] **TOTP-011** [P2][B20261120-totp] Preserve second-line spacing without an account
  - Done when: entries with no account keep the same title-to-code gap as entries with one
  - Ev: Bittrex/ucloud blank meta height 14px, title-to-code 20px, card 89px -> done 2026-11-20
- [x] **TOTP-012** [P1][B20261120-totp] Cache issuer icons locally with daily conditional sync
  - Done when: `/api/totp` returns local `/api/icons/...`, missing icons are fetched, and daily sync uses ETag/Last-Modified
  - Ev: 21 local icons, 42 files; local 200/304; restart sync 21 not_modified -> done 2026-11-20
- [x] **TOTP-013** [P1][B20261120-totp] Add a reusable Python OTP client with tinyauth cache
  - Done when: login/TOTP flow works, client.yaml is 0600 without a password, and later runs reuse it
  - Ev: temp tinyauth v5.2.0 password/TOTP tests; cross-subdomain cookie; import reuse -> done 2026-11-20
- [x] **TOTP-014** [P2][B20261120-totp] Rename the public host to otp.eqr.hosts.d3v.cn
  - Done when: template, nav, docs and Python defaults use otp, and the template adapts
  - Ev: domain grep clean; homepage validate; caddy adapt -> done 2026-11-20 (live install pending root)
- [x] **TOTP-015** [P1][B20261120-totp] Keep the FreeOTP password and exported secrets out of git
  - Done when: no commit on either remote branch contains `china532084` or the `otp_backup.*` exports, and the exports still exist on disk for the reference backup
  - Ev: `git filter-repo` rewrite of `scripts` master+dev force-pushed (bf1ecc5/00ba3cd); fresh clone `git grep` = 0; exports restored byte-identical from the pre-rewrite bundle; `make run` re-exported 22/22 identical -> done 2026-11-20
- [ ] **TOTP-016** [P1][B-backlog][user] Rotate the leaked FreeOTP master password and the panel account that reused it
  - Done when: the FreeOTP master (backup) password is changed before the next export, the `boys.tf` panel account password is changed (`ninedoors@126.com` is only its username), and provider tokens are rotated where the provider offers it
  - Ev: new export decrypts with the new password and the old one is rejected; no `china532084` left in any live config
