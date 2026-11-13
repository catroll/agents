# WebDriver POSTs need `{}`, and native dialogs need a handler

**Signal 1.** `find element` works, but `element/click` or `element/clear`
returns HTTP 400:

```
{"value":{"error":"invalid argument","message":"Failed to decode request as JSON: ","stacktrace":"Syntax error at :1:0"}}
```

**Cause.** The W3C WebDriver POST endpoints expect a JSON body. A raw HTTP
client that sends `data=None` transmits no body, so geckodriver's JSON parser
fails. It is not an element or session problem.

**Fix.** Send `{}` for POST/PUT commands that carry no arguments.

**Signal 2.** A test clicks a button whose handler calls `window.confirm(...)`,
but `GET /session/{id}/alert/text` reports no dialog, the action never runs past
the prompt, and the page looks unchanged.

**Cause.** Firefox's default `unhandledPromptBehavior` is "dismiss and notify";
the prompt is auto-dismissed before the next command. This also makes a test
believe the flow executed when the user answered "no".

**Fix.** Set `"unhandledPromptBehavior": "ignore"` in the session capabilities,
then use `GET /session/{id}/alert/text` (the endpoint is GET, not POST) and
`POST /session/{id}/alert/accept`. A button click that opens the prompt returns
success; the prompt stays open until accepted.

**Screenshot trap.** AdminLTE headers and footers transition background colour
for 0.3 s. A screenshot taken immediately after switching light/dark catches a
half-transitioned grey header and looks like a broken theme. Wait for
`transitionend` or ~0.5 s, or read `getComputedStyle(...).backgroundColor` —
which reports the final value as soon as the class is applied.


