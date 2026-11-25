# Staticize (staticize) — TODO

> Project: ~/Projects/Mine/staticize
> Docs: docs/roadmap.md, admin/README.md
> Prefix: ST
> Next ID: ST-006
> Updated: 2026-11-25

## Theme: admin operations

### Batch B20261118-admin-restart — restart without leaving the page (done 2026-11-18)

- [x] **ST-001** [P1][B20261118-admin-restart] Replace the stale-code command
  hint with a highlighted one-click restart
  - Done when: the banner has a button that restarts the supervisor unit and the
    page waits for the new pid; failure shows the reason.
  - Ev: `POST /restart` + `/healthz` (admin/restart.py), 10 tests, headless
    Firefox click, live restart to pid 3226919 -> done 2026-11-18
  (admin/restart.py, admin/web/templates/base.html, tests/test_admin_restart.py)

### Batch B20261118-favicons — rounded site icon and framed admin icon (done 2026-11-18)

- [x] **ST-002** [P2][B20261118-favicons] Rounded markjour favicon + dark-red
  bordered admin favicon
  - Done when: the site icon has rounded transparent corners at 16/32/48 and
    the admin icon is the same artwork inside a dark-red rounded frame.
  - Ev: `make favicons` from `static/icon/ma.png`; 4 tests; live
    https://www.markjour.com/favicon.ico sha256 matches the generated file
    -> done 2026-11-18
  (tools/make_favicons.py, favicon.ico, admin/web/static/favicon.ico)

## Theme: site identity

### Batch B20261118-header-logo — logo beside the page header title (done 2026-11-18)

- [x] **ST-003** [P2][B20261118-header-logo] Show a large logo left of the page
  header title
  - Done when: every generated page's top-left shows the site icon left of the
    title, the icon is the same artwork as the favicon, and small screens do not
    overflow.
  - Ev: `make favicons` now also writes `static/logo/markjour-logo.png`
    (192x192, rounded alpha corners) from `static/icon/ma.png`; template
    `mj-site-brand` + CSS 96px / 64px mobile; 241 tests; headless Firefox on the
    live build measured 96x96 at x=12 with the title at x=124 (64px at 390px
    wide), naturalWidth 192, no horizontal overflow, light and dark both
    render; `tools/publish.sh --no-search` deployed and the live
    `/static/logo/markjour-logo.png` sha256
    188e92db17ea63c698112244ae9a66ffbd5a771f8d7d899391eff6d38c4e009c matches
    the repo file -> done 2026-11-18
  (templates/tpl.base.html, static/css/common.css, tools/make_favicons.py,
  tests/test_header_logo.py, tests/test_favicons.py,
  static/logo/markjour-logo.png; commit abd2f23f7)

## Theme: maintenance

### Batch B20261124-imgcheck-ci — image check and a CI gate (done 2026-11-24)

- [x] **ST-004** [P1][B20261124-imgcheck-ci] Fix `articles imgcheck` after the
  image links moved to `/media/images/...` and add a Gitee Go gate so a script
  regression fails CI
  - Done when: `make articles-imgcheck` reports only genuinely missing files,
    the resolver has a test per reference form, and the Gitee pipeline runs the
    checks and a cold build.
  - Ev: `markjour/scripts/articles.py` normalizes canonical/legacy/bare forms,
    fails on unknown local paths, skips fenced examples; 15 tests in
    `tests/test_articles_imgcheck.py`; `make check` green (264 tests); `make
    generate` 8730 pages; `bash tools/ci.sh` exit 0; `.workflow/*.yml` run it on
    Python 3.12 -> done 2026-11-24
  (Makefile, tools/ci.sh, .workflow/, docs/build.md, tests/test_articles_imgcheck.py)

### Batch B20261125-publish-env — panel publishes when the daemon has no HOME (done 2026-11-25)

- [x] **ST-005** [P1][B20261125-publish-env] Panel publish died with `HOME:
  unbound variable` before doing any work
  - Done when: `tools/publish.sh` runs with no HOME in the caller's
    environment, the admin process exports HOME, and a regression test pins it.
  - Ev: job c8ba26d27957 exit 1 at line 49; reproduced with
    `env -u HOME bash tools/publish.sh --no-search`; full run under the daemon
    env (no HOME) with `PUBLISH_TARGET=/tmp/staticize-publish-test/` exit 0
    (8,950 pages, 21,310 files, 7.2 s); `supervisorctl reread` + `update`
    restarted admin to pid 479396 with `HOME=/home/catroll`;
    `tests/test_publish_script.py` 4 tests, `tests/test_sitemap_target.py` 4
    tests; PUBLISH_TARGET now also redirects the sitemap upload -> done
    2026-11-25
  (tools/publish.sh, admin/supervisor.conf, markjour/scripts/sitemap.py,
  tests/test_publish_script.py, tests/test_sitemap_target.py, docs/build.md)
