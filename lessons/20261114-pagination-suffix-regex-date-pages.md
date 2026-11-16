# Verifying generated pagination by filename — a generic `-<n>` suffix regex misreads date pages

Confirming "20 articles per page" by globbing generated output, I parsed names
with

```python
re.match(r'^(.*?)(?:-(\d+))?\.html$', base)
```

which splits a date page `build/date/2026-10-01.html` into key `2026-10` and
page number `1` (the day, not a page suffix). Every day after the first became
"page 2, 3, …" of a fake month group, and the check reported **146 false
violations** of the 20-item limit (e.g. `2026-10: {30: 2, 14: 1, 3: 1, ...}`).
The real output was correct: 1,214 date pages, none paginated.

Strip the `-<n>` suffix only after matching the full key shape:

```python
# date pages: key is YYYY-MM-DD, optional page suffix
r'^(\d{4}-\d{2}-\d{2})(?:-(\d+))?\.html$'
```

For tag pages the scheme is genuinely ambiguous (`Foo-2` is page 2 of `Foo`,
even if `Foo-2` could be a tag name — see `docs/build.md`, tag slug `/` → `~`),
so cross-check a known sample and the rendered footer (`PageSize: 20`, the
`本月 N 篇` note) before concluding that generated code is wrong.

Rule: when a filename-driven verification reports a large number of
violations, re-derive the filename grammar from the generator and test the
regex on one known file before "fixing" the generator.
