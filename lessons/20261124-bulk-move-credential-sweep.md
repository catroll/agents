# A docs move moves the secrets with it

## Trigger

Moving `02.email/12.operation/` (internal ops notes) into `email/industry/` as
industry knowledge. An audit afterwards found two plaintext logins in the moved
pages: a Validity account and an RWL signup, both written as `user / password`
near the top of small notes.

## Why it happens

Ops notes record logins so the next person can use the service, and they are
written to be read by colleagues, not published. A directory move reads as a
path change, so nobody re-reads the content. The new home can also look more
shareable ("industry knowledge"), which raises the blast radius.

## Check after any directory move or export

1. Grep the moved tree for account/password pairs:
   `grep -rniE '@[a-z0-9.-]+[[:space:]]*/[[:space:]]*[^ ]{6,}' <dir>`
   and for keywords: `grep -rniE 'password|密码|token|secret|api[_-]?key' <dir>`.
2. Check for `.env`, `.netrc`, kubeconfig, key files and other hidden state in
   the same tree, including ignored files.
3. Sanitize to a pointer ("见密码库") **before** committing the move, and in the
   source tree too, so a rollback cannot bring the value back.
4. Sweep the whole repo for the same strings. If they were ever pushed, treat
   them as burned: rotate the accounts, and say so in the report.

## Recovery

Replace the value with a pointer to the password store and commit that as its
own change. Rotation is the owner's call, but the report must say which
accounts and that git history still contains the old values.

## What I missed

The credential lines were plain `user / password` pairs near the top of two
small pages. The move was a batch `git mv` with no content read, and the first
audit only looked for "is this industry or internal", not "does this page
carry a login".
