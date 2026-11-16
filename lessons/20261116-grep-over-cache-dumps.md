# `grep -rn` over the repo dumps a megabyte-long match line

Symptom: a repo-wide `grep -rn ... .` prints one enormous line (a minified JSON
or base64 blob stored under `.cache/`), truncates the result, and the pipe to
`head` ends with `grep: 写入错误: 断开的管道` (broken pipe).

Cause: the search root included `.cache/` (31 MB in this repo),
`services/coder/.venv/` (135 MB), `__pycache__/`, and `node_modules/`.
Filtering matches afterwards (`| grep -v .cache`) still makes grep read and
print the blob — the filter runs after the read.

Check: exclude generated/runtime trees in the search command itself, and filter
by file type:

    grep -rn --include='*.py' --include='*.md' --include='*.sh' \
      --exclude-dir=.cache --exclude-dir=.venv --exclude-dir=__pycache__ \
      --exclude-dir=node_modules --exclude-dir=.git \
      'pattern' services scripts docs

Or use the harness `grep` tool with `include` and a narrow `path`; it never
enters those trees. If the search really must be whole-repo, use `rg` with
`--glob '!.cache' --glob '!.venv' ...`.

Negative result: a later `grep -v` does not save the read; the huge line is
still produced and the pipe can break. `head` closing the pipe turns it into
`grep: 写入错误: 断开的管道` rather than a clean stop.
