# `grep: 无效的定序字符` — a CJK bracket range silently measures nothing

**Symptom.** A language mix-up audit ran

```sh
grep -c $'[\u4e00-\u9fff]' docs/*.md
```

and printed `grep: 无效的定序字符` once per file with **no count on stdout**.
Exit status was 2. The loop kept going, so the table simply showed empty
values next to each filename — a reader (or the next command) could take that
as "0 CJK characters, all English".

**Cause.** GNU grep in a UTF-8 locale rejects a bracket-expression range whose
endpoints are multi-byte characters: glibc cannot build a collation range over
`一`–`鿿`. The diagnostic goes to stderr only; `-c` still prints nothing and
exits 2, so a pipeline that discards stderr (`2>/dev/null`, `| sort`) loses the
failure entirely.

**What works.**

```sh
grep -cP '[\x{4e00}-\x{9fff}]' file   # PCRE: counts matching lines, exit 0/1
python3 -c "import re,sys;print(len(re.findall(r'[\u4e00-\u9fff]',open(sys.argv[1]).read())))" file
```

`LC_ALL=C` makes the range "work" by comparing bytes, so it can match a stray
UTF-8 lead byte without the character being there — do not use it for this.

**The check.** A measurement command that prints nothing and exits non-zero is
a failed measurement, not a zero. Before reporting a count from a loop, print
`exit=$?` (or `set -e`) per iteration, and prefer a tool whose failure is
visible in stdout — Python `re` here, not `grep -c`.

**Related.** Repo-wide greps that walk `node_modules/`, `.venv/` and `build/`
also produced dozens of irrelevant hits and `grep: 写入错误: 断开的管道` in the
same session — `lessons/20261116-grep-over-cache-dumps.md`.
