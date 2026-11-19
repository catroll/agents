# Winnie (winnie) — TODO

> Project: ~/Projects/Mine/winnie
> Prefix: WN
> Next ID: WN-010
> Updated: 2026-11-19

## Theme: authentication (docs/decisions.md, WLB tools/homepage/docs/auth.md §6.6)

### Batch B20261118-auth-service — console consumes the tinyauth identity (open)

- [x] **WN-009** [P1][B20261118-auth-service] Open the console without its own login page
  - 2026-11-19: `/api` was ungated, so the console's token-less `/auth/me` probe
    never saw `Remote-User` and the login page stayed; the same path let a forged
    `Remote-User: admin` authenticate (verified HTTP 200). Fixed the Caddy
    template (gate `/api`, bypass for machine credentials, strip `Remote-*` on
    every upstream route), added `auth.proxy_user_map` (`catroll -> admin`), and
    made the console probe the edge identity before a stored token. 5 proxy
    tests + 11 auth tests pass; Firefox through a local Caddy with the real dist
    loads `Dashboard` with no login form (details in auth.md §6.6).
  - 2026-11-19 01:00 hot-loaded the candidate config; the user ran the installer
    at 01:03 (`--check` reports in sync). At 01:09 a second layer was fixed:
    uvicorn's default proxy headers rewrote `request.client` to the browser's
    `X-Forwarded-For`, so the loopback trust check still rejected Caddy's
    `Remote-User`. `serve-api.py` now disables `proxy_headers`, and
    `winnie_api.proxy.TransportAwareProxyHeaders` keeps the transport peer in
    `scope["winnie.transport_client"]`; the trust check reads it. A direct API
    call with a public `X-Forwarded-For` went 401 -> 200, and a headless browser
    through a local Caddy with a non-loopback forwarded address loads
    `Dashboard` and its `/api/v1/meetings` call returns 200. Remaining: the user
    refreshes once for final confirmation (their tinyauth cookie cannot be
    reused). 2026-11-19 01:23: the user refreshed and landed in the console;
    the API logged `/api/v1/auth/me` 200 for the same browser address -> done
    2026-11-19.
  - Done when: live `https://eqr.hosts.d3v.cn/` opens the console with no local
    login page, and a forged `Remote-User` on `/api` is rejected.

## Theme: schedule/calendar sync (docs/schedule-calendar-sync.md)

### Batch B20261118-calendar-clients — close the two-client acceptance (open)

- [ ] **WN-001** [P1][B20261118-calendar-clients][user] Add the DAVx⁵ account on the phone
  - Done when: the phone shows the dedicated `WLB 计划` calendar (and optionally
    `个人通讯录`), a new `[日程]` item appears within one DAVx⁵ interval, and an
    edit made on the phone reaches the week file.
  - Ev: phone screenshot of the account and a synced event; bridge action log.

- [ ] **WN-002** [P1][B20261118-calendar-clients][user] Add the CalDAV account to
  GNOME Online Accounts (or Evolution) on Ubuntu
  - Done when: GNOME Calendar shows `WLB 计划`, GNOME Contacts shows
    `个人通讯录` if enabled, a create/retitle/move round-trips through the week
    file, and Files is disabled in GOA.
  - Ev: GNOME Calendar screenshot and one bridge JSON log line.

- [ ] **WN-003** [P2][B20261118-calendar-clients] Run the two-client conflict scenario
  - Done when: an edit on the phone and a different edit in Markdown during the
    same cycle produce a merge for disjoint fields and a conflict record for the
    same field, with no lost text.
  - Ev: `data/schedule-sync/conflicts/<date>.jsonl` and the final week line.

- [x] **WN-008** [P2][B20261118-calendar-clients] Expose CardDAV on the same relay
  - Done when: `/.well-known/carddav` redirects, the `个人通讯录` address book
    exists, and a vCard can be created, read and deleted through the public
    URL.
  - Ev: 301 well-known, `MKCOL` 201, vCard `PUT` 201 / `GET` / `DELETE` 200;
    staticize commit `11b69190a` plus the winnie installer change -> done 2026-11-18

### Batch B-backlog — operations (open)

- [ ] **WN-004** [P2][B-backlog] Enable linger for the calendar user units
  - Why: the timer and tunnel currently start at login, not at boot.
  - Done when: `loginctl show-user catroll -p Linger` says `yes` after
    `sudo loginctl enable-linger catroll`, and a reboot leaves the timer and
    tunnel active.
  - Ev: `systemctl --user is-active winnie-schedule-sync.timer winnie-cal-tunnel.service`.

- [ ] **WN-005** [P2][B-backlog] Back up and restore the calendar stores
  - Done when: a backup of `~/.local/state/winnie/radicale` and
    `data/schedule-sync` is restored on a scratch path, `calendar-service.sh
    status` is healthy, and one event round-trips.
  - Ev: backup path, restore command, bridge log.

- [ ] **WN-006** [P2][B-backlog] Surface the public relay in status and alerts
  - Done when: `make calendar-status` or the status command reports the public
    `https://www.markjour.com/winnie-cal/` response and a tunnel outage creates a
    visible alert through the existing push path.
  - Ev: status output and one induced tunnel outage.

- [ ] **WN-007** [P3][B-backlog] Decide on tombstone suppression for stale clients
  - Why: v1 has no tombstones; a stale client can recreate a deleted event.
  - Done when: either the tombstone table and its tests exist, or the limitation
    is recorded as accepted in docs/schedule-calendar-sync.md.
