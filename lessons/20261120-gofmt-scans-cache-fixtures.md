# `make check` fails on an unformatted temporary file under `.cache`

## Symptom

A project Makefile had:

```make
fmt-check:
	@out=$$(gofmt -l .); if [ -n "$$out" ]; then echo "not gofmt-ed:"; echo "$$out"; exit 1; fi
```

`make check` failed even though the only Go source was formatted:

```text
not gofmt-ed:
.cache/totp-test/rfc/main_test.go
make: *** [Makefile:32: fmt-check] Error 1
```

The file was a deliberately temporary test fixture under the project's
gitignored `.cache/`; `gofmt -l .` walks hidden directories too.

## Fix

Scope the check to files that belong to the module, not every `*.go` on disk:

```make
fmt-check:
	@out=$$(gofmt -l *.go); ...
```

For a project with nested packages, use `git ls-files '*.go'` or the directories
returned by `go list -f '{{.Dir}}' ./...`; never include `.cache`, `bin`,
`vendor` or other fixture roots.

## Check

Create an unformatted `*.go` under `.cache/` and run `make check`: it must still
pass. Remove the fixture afterwards.
