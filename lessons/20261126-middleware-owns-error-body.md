# A framework middleware that writes its own response breaks your error contract

**Signal.** A service documents one error shape ("every failure returns
`{"error":{"code":…}}`") and a status code list, and a review of the docs finds
a code in the list whose producer you never wrote. In this case: `request_timeout`
was in the README, but chi's `middleware.Timeout` was the producer, and it
writes `w.WriteHeader(504)` with **no body**.

**Cause.** A middleware that owns the failure status also owns the body. chi's
`Timeout` and its default 405 handler both do this. Wrapping a router in such a
middleware silently creates a response path that your envelope, your
`Content-Type` and your error-code list do not cover. Nothing fails loudly: the
tests pass because they test the handlers, and the docs are wrong only on the
one path nobody exercises.

**The check.** For every behaviour the docs claim, name the code that produces
it. If a third-party middleware produces it, read that middleware's source (in
the module cache: `$(go env GOMODCACHE)/<mod>@<ver>/…`) and confirm it writes
what you claim. Then write a test that asserts the *contract*, not the status:

```go
rec := httptest.NewRecorder()
h.ServeHTTP(rec, httptest.NewRequest(...))
json.Unmarshal(rec.Body.Bytes(), &envelope) // fails on an empty body
```

A test asserting only `rec.Code == 504` passes against the broken version.
Confirm the test is real by reverting the fix and watching it fail — here it
reported `status = 200, want 504`, proving the middleware path was never even
reached with an envelope.

**Fix shape.** Re-implement the middleware around the same semantics rather than
patching the output: keep the context cancellation, write the status and body
only when the handler returned without writing (`WrapResponseWriter.Status() == 0`),
so an answer that already went out is never corrupted. Say in a comment which
upstream middleware it replaces and why, or the next reader will "simplify" it
back.

**Related trap — a timeout does not bound a slow client.** `request_timeout`
cancels the request context; that does **not** unblock an `io.ReadAll(r.Body)`
on a client that never sends the body (verified on Go 1.26). Stalled clients are
cut off by `http.Server.ReadTimeout`, which closes the connection and yields a
decodable 400. Credit the right knob in cost/DoS notes, and verify with a raw
socket that sends headers and no body: with `read_timeout: 2s` the reply arrived
at 2.0s.
