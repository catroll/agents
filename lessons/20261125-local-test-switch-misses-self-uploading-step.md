# A "local test" switch that only redirects the last step still writes production

## Trigger

- You ran a pipeline with its documented test/override flag (`PUBLISH_TARGET`,
  `--dry-run`, `DEST=`, a staging config) and a step inside it still wrote to
  the live host — a log line, an uploaded file, an email, a webhook.
- The flag is documented as "overrides the destination", but the pipeline has
  more than one place that writes.

## What happened (2026-11-25, markjour publish)

`tools/publish.sh` advertises `PUBLISH_TARGET=/tmp/...` for local testing: the
final `rsync build/` goes to that path. But one stage, `main.py sitemap`, does
its own `rsync sitemap.*` to a hardcoded
`woodyhosted01.hosts.d3v.cn:/opt/www.markjour.com/`. A test run with
`PUBLISH_TARGET=/tmp/staticize-publish-test/` therefore still uploaded
`sitemap.html` and `sitemap.xml` to the live site:

```
19:52:38 INFO [markjour.scripts.sitemap:rsync_sitemap#238] rsync sitemap:
  rsync -avzP --no-owner --no-group --chmod=D755,F644 .../sitemap.html \
  .../sitemap.xml .../sitemap.xsl woodyhosted01.hosts.d3v.cn:/opt/www.markjour.com/
```

No page was deployed by that run, so the live sitemap briefly described pages
that only went live on the next cron tick. The test looked clean because the
final rsync summary pointed at `/tmp`.

## Before calling any run "local", find every writer

```bash
grep -nE "rsync|scp|ssh|curl|Popen|subprocess|requests\.(post|put)" tools/publish.sh markjour/scripts/*.py
```

Then, for each writer, ask *which variable decides its target*. A constant, a
config default or a second environment variable is a hole in the switch. The
`PUBLISH_TARGET` fix was: let `sitemap.py` read `SITEMAP_RSYNC_TARGET` (default
unchanged) and make `publish.sh` export it from its own `TARGET`.

## Prove the redirect, don't assume it

- Unit level: point the variable at a temp dir and assert the argv destination
  (`tests/test_sitemap_target.py`) plus the exported value in the script
  (`tests/test_publish_script.py`).
- End to end: run the stage with the override and check the files land locally
  and the log line names the temp path:

  ```bash
  SITEMAP_RSYNC_TARGET=/tmp/sitemap-probe/ .venv/bin/python main.py sitemap
  ls -l /tmp/sitemap-probe
  ```

## Harm check after the fact

If a "local" run did reach production, check whether the content differed
(`rsync --stats` "Number of regular files transferred"), and whether any other
step was supposed to make it consistent. Here only the two sitemap files moved
and the next cron tick deployed the pages they listed.

## Negative results

- `--no-search` did not make the run local; it only skips Algolia. Two
  independent switches made the mistake easy to miss.
- The exit status was 0 and the log ended with `== publish done`, so nothing
  flagged the production write; only reading the whole log did.
