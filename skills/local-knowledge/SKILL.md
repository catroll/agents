---
name: local-knowledge
description: Search the owner's local notes and Markdown documents. Use when a
  question depends on what the owner wrote, decided or saved before ("我的笔记",
  "之前写的", "找一下那份文档", "where did I", "what did we decide about").
  Backed by an MCP server named local-knowledge and an HTTP API on
  127.0.0.1:8790; never search the filesystem for these
  documents.
whenToUse: The user asks about something they wrote, noted, decided, or saved
  locally, or asks you to find a document without naming a path.
---

# Local knowledge

An index of the owner's own `.md` and `.txt` files. Reach it through tool calls,
not by walking directories.

## Tools

- `search_documents(query, roots?, since?, limit?)` — ranked hits with path,
  heading, line range, mtime and score.
- `get_document(path, from_line?, lines?)` — the cited text, revalidated against
  the file before it is returned.
- `index_status()` — coverage, last sweep, failures.

## HTTP

When MCP is unavailable: `POST http://127.0.0.1:8790/search` with
`{"query": "...", "limit": 8}`.

## Rules

- Answer only from text returned by `get_document`; cite `path:line`.
- An empty result means the corpus has nothing. Say so instead of guessing.
- Results carry `mtime`; re-run the search after a file changes.
