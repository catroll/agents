# Rewriting a user's text file: split on `\n`, and prove it with a round trip

**Signal.** A parser written to preserve formatting still rewrote a file:
`"\n".join(text.splitlines()) + "\n" != text` for
`~/Projects/Mine/WLB/work/2024/Q4/12/202412-16-22.md`, which contains a literal
`\x0b` (vertical tab) inside a paragraph. `str.splitlines()` also breaks on
`\x0c`, `\x1c`-`\x1e`, `\x85`, `\u2028` and `\u2029`, so any of them silently
becomes a line boundary and the "unchanged" bytes are lost.

**Fix.** `lines = text.split("\n")`, pop the trailing `""` when the text ended
with a newline, and keep that fact for the write. Then assert the invariant
against the real corpus: every file must parse and render back to its exact
bytes (`week.render() == path.read_text()`), and add-then-delete must return the
file unchanged. That single test caught the `\x0b` file, and it is what makes a
line-splicing editor safe to point at files a human also edits.

**And a silent grammar failure: a `^\[` anchor after a consumed token.**
Parsing ``- [ ] `10/05` [周一] [09:30~10:30] text`` with ``^`(\d+/\d+)` `` and
then `^\[([^\]]+)\]` matched nothing, because the date regex consumed the
backticks and left one space before the first `[`. Every tag became part of the
text and nothing raised: the listing "looked right" because it printed the line
verbatim. Strip whitespace between tokens (`^[ \t]*\[...`) and assert the
post-condition that matters, not the presence of a function — here,
`event.text` must not start with `[`, checked over all 10k events in the corpus.

