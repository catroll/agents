# `git status --porcelain` loses its first status column when the output is stripped

**Signal.** A wrapper lists dirty paths and reports the first one as
`oody/docs/coder/constraint-matrix.md` while every later path is
`woody/docs/...`. Nothing is actually missing from the repository.

**Cause.** The helper did:

```python
return proc.stdout.strip() if proc.returncode == 0 else ""
...
paths = [line[3:] for line in status.splitlines()]
```

`strip()` removes the **leading space of the first line**, whose format is
`XY PATH` (` M`, `??`, `A `, ...). Slicing `line[3:]` then drops the first
character of the path.

**Check / fix.** Keep porcelain stdout unstripped; split lines and slice the
three-character prefix (`line[3:]`). Strip only single-value commands such as
`rev-parse --short HEAD`. When a path looks one character short, print
`repr(lines[0])` before touching the slicing.

**Negative result.** `lstrip()` and `.strip()` are equally wrong: the leading
space is data in porcelain v1. `git status --short` has the same format.

**Generalisable.** Any fixed-width line format (porcelain, `ls -l`, columnar
output) breaks when a generic trim is applied before parsing; trim the scalar
value, not the structured block.
