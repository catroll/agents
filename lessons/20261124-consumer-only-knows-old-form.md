# A consumer that enumerates the old URL/path forms degrades to "all broken" or "none found"

Date: 2026-11-24

## Signal

`make articles-imgcheck` in `~/Projects/Mine/staticize` printed ~2,000
`/media/images/...` paths as missing while the files existed, and exited 0.
The same shape appears with config keys, API fields and log formats: a
consumer keeps a `startswith`/`key in` list of the old spellings, the producer
moves to a new one, and the consumer reports every record as absent instead of
failing.

## Cause

The checker knew `../images/` and `images/`; the corpus had moved to
`/media/images/`. The unmatched path was joined with `os.path.join`, whose
absolute second argument discards the base directory, so the existence test
pointed at `/media/images/...` on the host root. Nothing tested the current
form, and the only outcome was "not found".

## Check next time

- When a convention changes, grep for the old literal (`../images/`,
  `old_field`, `v1/`) across *consumers*, not only producers, before calling
  the migration done.
- Normalize input in one function instead of branches at each call site, and
  raise on a site-local form the function does not know. A silent
  `return input` turns the next convention change into a false negative.
- Add one fixture per accepted form and one assertion that the real corpus
  still matches (a reference count, not just exit 0), so "the scanner found
  nothing" fails CI.
- A missing file and an unrecognized path form are different failures: report
  the first, fail on the second.

## Related

Project lesson: `~/Projects/Mine/staticize/docs/lessons/20261124-imgcheck-image-path-forms.md`.
