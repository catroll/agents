# TOTP Authenticator (totp) — TODO

> Project: tools/totp
> Prefix: TOTP
> Next ID: TOTP-004
> Updated: 2026-11-20

## Theme: YAML-driven TOTP page behind the existing tinyauth gate

### Batch B20261120-totp — first version (target 2026-11-20, wip)

- [x] **TOTP-001** [P1][B20261120-totp] Add the one-Go-file TOTP service and single HTML page
  - Done when: `bin/totp -config ...` serves `/`, `/api/totp`, `/healthz`; RFC 6238 vectors pass
  - Ev: `make check`; 18 RFC vectors; real HTTP; headless Firefox -> done 2026-11-20
- [x] **TOTP-002** [P1][B20261120-totp] Add the tinyauth Caddy route and homepage entry
  - Done when: rendered Caddyfile adapts; unauthenticated request 302s to the portal
  - Ev: `caddy adapt`; temporary Caddy + real tinyauth -> done 2026-11-20
- [ ] **TOTP-003** [P1][B20261120-totp][user] Install the Caddy block and run the service
  - Done when: `https://totp.eqr.hosts.d3v.cn/` 302s to the login page, then serves the page after login
  - Ev: `sudo scripts/install-caddy.sh install` in `tools/homepage`; start `bin/totp` under systemd/supervisor; checks in `tools/totp/docs/operations.md` §6.3
  - Progress 2026-11-20: Caddy block installed and 302 verified; `totp.service` transient started with the example config. Persistent unit and the real YAML remain.
