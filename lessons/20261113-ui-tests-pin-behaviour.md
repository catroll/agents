# A black-box UI suite that pins widget shape, copy or status codes breaks on legitimate UI evolution

**Signal.** After a UI change the acceptance suite fails with messages such as
`models textarea = "", want "gpt-test"`, `expected to find "already exists"`,
`status = 422, want 303`, `expected to find "absolute URL"`. Every assertion
names a *how* (which control, which sentence, which status), and every one of
them is about a form that still works for a real user.

Concrete case: `tinyapi_test/cases` (TinyAPI) — 9 failures after the Console
channel form moved models from a `textarea` to repeated table-row inputs and
validation failures switched from `303 + flash` to `422 + re-render`. The
product was correct; the tests were over-pinned.

**Check before editing anything.** Read the rendered page and the response:

```bash
# what controls does the page actually render?
curl -s -b jar http://host/admin/channels/1/edit | grep -oE 'name="[^"]+"'
# what does a rejected submit actually answer?
curl -s -o /tmp/out.html -w '%{http_code}\n' -b jar -X POST ... --data-urlencode ...
```

Then decide: does the *user-visible outcome* still hold — the submission is
rejected, the error is visible, no config/data changed, the service is healthy?
If yes, the test is wrong, not the product. If the rejection silently
succeeds (or a success silently fails), that is a product regression; keep the
test red.

**Fix pattern (do not just match the new strings).**

1. Discover controls from the rendered page; do not assume an earlier widget.
   Repeated rows need a multi-value reader (TinyAPI harness:
   `FormValuesAll`; Go: `url.Values` with repeated `Add`).
2. Accept equivalent presentations of validation: `4xx` re-render **or**
   `303 + flash`. Pin the invariant instead: error visible **and** no side
   effect. Never accept "the request completed" as proof of validation.
3. Match message *fragments* case-insensitively (`already in use`,
   `already exists`, `duplicate`), not full sentences. Exact copy is only a
   contract where the documentation literally promises it.
4. Keep success paths at `2xx/303`, and keep every behavioural assertion:
   persistence, idempotency, live apply, no secret leakage.
5. Record the policy in the suite (TinyAPI: `TESTPLAN.md` §3.1) so the next
   author does not re-pin copy.

**Negative result.** A blanket "accept any 4xx" is worse than the original
failure: a handler that returns 422 with an empty body, or 4xx after already
writing the config, passes it. The test must still assert visible error text
**and** byte-unchanged state (config file, row counts, `/v1/models`).

**Generalisable bit.** An acceptance test asserts what a user can observe and
rely on. Widget type, exact wording and a particular redirect are implementation
choices; when they change, update the test — but only after confirming the
observable outcome is unchanged, and keep the outcome assertions intact.
