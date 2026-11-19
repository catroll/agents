# A Markdown document rebuilt section by section glues every heading to the previous paragraph

## Signal

A file assembled from sections split with `re.split(r'(?m)^(## .+)$', text)` has
each heading on the line immediately after the previous section's last line:

    existing section first.
    ## Language

Markdown still renders and nothing errors, so the defect survives until someone
reads the file or diffs it.

## Why

The split pattern consumes the blank line that separated the heading from the
previous section, and the replacement section ended with one `\n` instead of the
`\n\n` the join needs. Rebuilding with `''.join(parts)` copies the consumed
separator into the result.

## Check

Run this on the generated file before installing it:

    python3 - <<'PY'
    import re
    t = open('AGENTS.md', encoding='utf-8').read()
    glued = re.findall(r'(?m)[^\n]\n## ', t)
    assert not glued, f'{len(glued)} headings glued to the previous paragraph'
    assert t.endswith('\n') and '\n\n\n' not in t
    PY

Then read `diff -u old new`; the byte count and a smoke test both pass on the
broken file, and the diff is what shows the missing line.

## Negative result

A size target chosen before the transformation was 3 KB optimistic. The
machine-generated section (93 one-line lesson bullets) has a floor of about
160 bytes per entry, so roughly 15 KB of that file cannot be compressed by
editing prose. Measure the fixed part before promising a number.
