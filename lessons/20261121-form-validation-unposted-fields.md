# Validate a form field only if the form posts it

**Error shape.** After adding `parseIntStrict(c.PostForm("timeoutSeconds"))` to the
jobs schedule handler, every save from the list failed with "The timeout must be a
whole number of seconds" — the template posts only `cron`.

**Cause.** The handler assumed every policy field was present. An absent
`PostForm` value is `""`, which is not a number, so the validation rejected the
one request the form actually sends. The contract's own divergence note already
said the console form posts only `cron`; that note was read after the handler.

**Fix.** Treat an absent field as "keep the stored value": start from
`rec.GetInt(...)`, parse only when the raw string is non-empty, then validate the
resulting policy. The same rule applies to any inline form that edits one column
of a larger row.

**Check.** List what the template posts (`grep -n 'name="' <template>`) and compare
it with the handler's `c.PostForm(...)` calls. A handler test that supplies every
field cannot catch this; the end-to-end form can.
