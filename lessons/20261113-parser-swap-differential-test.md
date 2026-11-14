# A faster parser swap needs a differential test that survives dependency bumps

**Signal.** After bumping `github.com/goccy/go-json` v0.10.5 -> v0.12.0 the
differential test in `tinyapi/internal/jsonx` failed with
`jsonx result "a�b" does not preserve the raw bytes as documented`. The older
release kept invalid UTF-8 bytes raw; v0.12.0 now replaces them with U+FFFD to
match `encoding/json`. The Go API (`json.Unmarshal`) was unchanged — "drop-in"
covered the signature, not the behaviour.

**Action.** When replacing a stdlib parser/encoder with a faster third-party
one, keep a differential test against the stdlib covering representative and
adversarial inputs (raw messages, duplicate keys, big numbers, malformed JSON,
invalid UTF-8), and **rerun it after every dependency bump** instead of trusting
the drop-in claim. Record any accepted difference at the seam (package comment +
test name), not at call sites.

**Note.** After the upgrade the difference disappeared (v0.12.0 aligned with
stdlib), so the fix was to update the assertion; the value was that the test
proved the alignment rather than assuming it.
