# Binary grew after a perf/dependency change: attribute with an A/B rebuild

**Signal.** A release or dev binary grows by a few MB after a feature or
performance commit. `go.mod` already listed the suspect package before (as
`// indirect`), the feature diff looks small, or you are about to attribute the
growth to "more code".

**Check (about five minutes).**

1. Build the previous known-good commit in a temporary worktree with the exact
   same flags and compare bytes and sections (`.text`, `.gopclntab`, `.rodata`,
   debug sections).
2. A/B the candidate itself: in a scratch copy of the current tree, swap the new
   import back to the previous implementation, rebuild with identical flags,
   and diff the bytes. This separates the dependency cost from feature growth.
3. Confirm linkage, not presence: `go version -m <bin>`,
   `go tool nm -size <bin> | grep <module>`, and count functions. An
   `// indirect` line in `go.mod` is not evidence that the package is in the
   binary; Go drops packages nobody imports.
4. Only then attribute. Real case (TinyAPI, 2026-11-13): release
   +2,387,968 B; the A/B rebuild with `internal/jsonx` switched back to
   `encoding/json` put goccy/go-json's cost at +2,367,488 B (99.1%) and all
   feature code at +20,480 B. The dev build grew 1.11 MB more because DWARF and
   symbols are emitted for the same 1,606 new functions.

**Rule.** Binary size attribution is an A/B rebuild, not a code-review guess.
For Go a package is linked whole, so a hot-path dependency drags in its entire
encoder/decoder; dev/pprof builds pay extra DWARF for it. Keep the measurement
in the project's binary-size document together with the decision it justified
(here: +45% throughput on 1 MiB responses for +2.37 MB).

**Negative result recorded.** Counting new Go lines (+720) suggested "feature
code grew", which was wrong by two orders of magnitude. Line count is not code
size, and `go.mod` digest changes are not linkage.
