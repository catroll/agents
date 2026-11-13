# A rejected form save that redirects is a data-loss bug

**Signal.** "I submitted, it said failure, and everything I typed was gone." The
save handler calls `flash(...)` + `c.Redirect(303, formPath)` on a validation
failure, and the GET form re-renders from the stored state.

**Cause.** Post/Redirect/Get is right for the success path only. On failure the
redirect discards the POST body: the page shows the previously saved config
(blank for a create form), so the user's input is lost. It also hides which
field was wrong because the error is a toast, not a field marker.

**Fix / check.** On validation failure re-render the same template with 400/422,
the submitted **non-secret** values and `FormErrors` mapped per field; never echo
credentials, passwords or API keys. Search a handler for `Redirect` in every
validation branch — that is the whole audit. Three corollaries from the TinyAPI
run:
- A visible required `*` must be derived from what the server actually rejects.
  Marking a field the server accepts (empty forgot-password email) and not
  marking a table the server rejects (dynamic model rows) both make the UI lie.
  HTML `required` alone is a convenience, not validation.
- An inline `<script>` inside a template's `content` block runs **before** the
  layout's `<script src="...bootstrap...">`: `new bootstrap.Modal(...)` there
  throws `ReferenceError` silently, and both "reopen the modal after 422" and
  "show the one-time key on success" fail invisibly. Wrap it in
  `DOMContentLoaded`, or move the logic into the deferred app script.
- One-time tokens: call `valid(token)` and validate the submitted data, and only
  `consume(token)` after everything passes. `consume` first turns one password
  typo into a permanently dead reset link.

