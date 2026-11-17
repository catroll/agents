# Fact-checking a secret must never print the matching line

**Signal.** Verifying "is this credential readable?" I printed the matching
row/line to show the evidence. That put a live 42-byte GitHub PAT and later a
whole DKIM RSA private key into the tool output and the session transcript —
the key was stored as one cell of a Markdown table, so `ln.strip()` returned
the entire PEM block.

**Rule.** Never emit a line, cell, JSON field or search snippet from a document
that may contain a secret, not even truncated "for context". Prove readability
programmatically instead:

```python
# does the server return the secret? compare hashes, print a boolean
src = pathlib.Path(f).read_text(encoding="utf-8-sig").strip()
returned = response_json["text"].strip()
print("equals_file:", hashlib.sha256(returned.encode()).hexdigest()
      == hashlib.sha256(src.encode()).hexdigest())
print("chars:", len(returned), "prefix:", returned[:3] + "***")
```

For regex triage, print the pattern name, the file, and a count — never
`m.group(0)`. If the match itself must be shown, show only `m.group(0)[:4] +
"…"` and the length.

**Why the usual "first 80 chars" guard fails.** A Markdown table row or a
one-line JSON field can hold an entire PEM key; any prefix/suffix slice of that
line still leaks most of it. Line-based redaction assumes the secret is on its
own line, which is exactly false in tables, JSON dumps and chat logs.

**A leak is not ephemeral.** The transcript is persisted in the session log
(`~/.dsh/sessions/...`), so a printed secret now has a second home outside the
indexed file. Treat printed credentials as compromised: rotate them, then fix
the query.

**Negative result worth keeping.** `grep`/`sed`/`head` on "the line containing
the token" is the same trap; use `grep -c` or `python` with the comparison
above. The same check applies before printing a search-hit snippet, a diff, or
a database row.