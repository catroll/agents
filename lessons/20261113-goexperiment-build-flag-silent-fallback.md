# An environment-only build flag falls back silently

**Signal.** A build depends on a setting that lives only in the environment
(`GOEXPERIMENT=jsonv2`, `CGO_ENABLED`, tags selected by an env var) and not in
`go.mod`. Plain `go build` / `go test` compile and pass, yet the produced binary
is not the one you think: two builds that should differ are byte-identical, or a
Makefile recipe prints the variable empty (`GOEXPERIMENT= go build ...`).

**Check.**

1. Ask make what it will actually run: `make -n build | grep GOEXPERIMENT`.
   A `?=` definition that was "added" by an edit that silently did not match the
   file leaves `$(GOEXPERIMENT)` empty and every recipe looks plausible.
2. Build unstripped binaries with and without the flag and compare package
   presence: `go tool nm /tmp/x | grep -c encoding/json/v2` (477 vs 0 in the
   real case). A stripped binary has no symbols, so this check needs the debug
   build.
3. Compare size and a benchmark between the two builds; a real flag changes both.

**Rule.** An environment-only build flag must be defined once, threaded through
every build/test/vet/run path, and asserted mechanically (symbol presence or a
size/benchmark delta). CI must fail when it is missing, and the test gate must
run under the same environment as the release build; `go.mod` cannot carry a
build flag, so a plain `go build` can silently ship the slow path.

**Negative result recorded.** In this incident the flag definition was missing
from the Makefile because a targeted string replacement did not match (the file
had gained a VERSION block in between) and nothing failed: release and dev
builds were byte-identical with the experiment on and off. The identical sizes
were the clue; the fix was adding `GOEXPERIMENT ?= jsonv2` and re-checking
`make -n` plus the symbol count.
