# A root-owned global CLI fails writing a cache inside its own package

## Signal

`honkit build` (honkit 6.2.5 installed globally under
`/usr/local/lib/node_modules`) ended with:

    Error: EACCES: permission denied, mkdir
    '/usr/local/lib/node_modules/honkit/node_modules/flat-cache/.cache'

A partial `_book/` was produced, and because the command was piped through
`tail`, `$?` reported `exit=0` — the pipeline mask, not the build result.

## Why it matters

The failure looks like a permissions problem in the project, but the package's
dependency (`flat-cache`) writes its cache next to its own module, so the cache
location follows the install prefix, not `$HOME` or the project. A partial book
that "looks built" is worse than no book: pages silently go missing.

## Procedure

- Pin the generator in the project as a local devDependency (`npm install
  honkit@6.2.5`) and run `node_modules/.bin/honkit build`; never rely on a
  root-owned global install for a build step.
- Do not trust `cmd | tail` for the exit status. Capture `rc=$?` of the command
  itself, and confirm success with the tool's own success line
  (`generation finished with success`) plus an output count (`_book/*.html`).
- When the generator has no `--cache-dir`, a local install is the only clean fix.

## Negative results

`grep -ril 'honkit\|flat-cache' ~/.agents/lessons` returned nothing; no existing
lesson covered a package-relative cache path.

Date learned: 2026-11-21.
