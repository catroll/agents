# Verifying generated HTML rows: a lazy `(.*?)</li>` stops at nested list markup

**Signal.** Checking that every monthly archive row rendered its explicit
Summary, extraction with

```python
re.findall(r'<li class="archive-item" id="article-([^"]+)">(.*?)</li>', html, re.S)
```

reported 14–15 "missing summary block" problems while the page clearly had
them. The summaries contain their own `<ul><li>…</li></ul>` (e.g. 2018-05
`SMTP 认证`'s list of auth methods), so the lazy group ended at the *inner*
`</li>` and the `<div class="archive-summary">` that follows `archive-meta` was
outside the captured body. A second false alarm came from
`<div class="archive-summary">(.*?)</div>` on a summary containing a raw
`<div style=…>`; same cause.

**Fix.** Split on the item boundary instead of matching the closing tag, then
compare the expected HTML verbatim (the template inserts it unchanged):

```python
for chunk in html.split('<li class="archive-item"')[1:]:
    name = re.match(r'\s+id="article-([^"]+)"', chunk).group(1)
    expected = summary_without_images(article_info(source_path(name)))
    assert (expected in chunk) if expected else ('class="archive-summary"' not in chunk)
```

Result after the fix: 1,420 items, 411 with the summary embedded verbatim,
1,009 without, zero problems. Use an HTML parser when the real structure
matters; use exact-string containment when the generator inserts a known
fragment. Do not conclude from a regex extractor that generated output is
missing content until a nesting-safe check agrees.
