# A pipeline's exit code is the last command's, not the failing test's

**Signal.** `go test ./... -count=1 2>&1 | tail -6; echo "exit=$?"` printed a
package line `FAIL` and then `exit=0`. The shell status came from `tail`, which
succeeded, not from `go test`.

**Why it matters.** It is a false green: a script that only checks `$?` will
report a passing suite while a package failed. The output still contained
`FAIL`, but nothing enforces reading it.

**Check.** Either run the test without a pipe and inspect `$?`, or add
`set -o pipefail` (bash) so the pipeline fails when any stage fails, or write
the output to a file and grep it for `^FAIL` / `--- FAIL` and treat a hit as
failure. The same trap applies to `go vet | head`, `npm test | tail`, and any
`cmd | formatter` chain.

**Related.** Truncating output with `tail`/`head` also hides earlier failures;
when a suite is long, keep the full log in a file and print only the summary
lines that decide pass/fail.
