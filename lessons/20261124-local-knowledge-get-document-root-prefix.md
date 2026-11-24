# `no indexed document at WLB:projects/…` when passing a search hit verbatim to get_document

Date: 2026-11-24

## Signal

`local-knowledge` `search_documents` renders each hit as `ROOT:relative/path`
(`WLB:projects/023-shouce.org/README.md`). Pasted verbatim into
`get_document`, it fails:

```
Error: no indexed document at WLB:projects/023-shouce.org/README.md
```

The document is indexed — only the address form is wrong.

## Cause

The `ROOT:` prefix belongs to the search result's display format. `get_document`
takes either a **root-relative path** (the part after `ROOT:`) or an absolute
path under a root. The root name itself must not be in the path; there is no
`ROOT:` scheme in the lookup.

## Fix

Strip the prefix:

```
projects/023-shouce.org/README.md     # works
WLB:projects/023-shouce.org/README.md # fails
```

When a citation must name the root, keep `ROOT:path` in prose and convert to the
bare root-relative path for the tool call.

## Check next time

If `get_document` reports `no indexed document` while `search_documents` just
returned that exact string, suspect the prefix before concluding the file is
missing — retry once with the prefix removed before reporting a miss.
