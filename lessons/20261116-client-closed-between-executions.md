# "Cannot send a request, as the client has been closed" when looping one engine object

## Signal

A loop that calls `TestEngine().execute(...)` (or any SDK object that owns an
HTTP client) over N inputs succeeds on the first iteration and fails the rest:

    Step execution failed: Request execution failed: Cannot send a request, as the client has been closed.

The first candidate's result looks fine, so the failure only appears in the
batch count — 1 rejected + 26 errors was the first probe pass.

## Cause

`TestEngine.execute()` closes its HTTP client before returning. The engine is a
one-shot executor, not a reusable session.

## Check / fix

Construct a fresh engine inside the loop (or call the SDK's documented
`client = ...` reset). Do not hoist the engine above the loop because "it worked
for the first one".

    for cand in candidates:
        result = TestEngine().execute(script, platform=target)

Verify by looping at least two inputs and asserting every result has a
non-null status.

## Negative result

Reusing the engine and catching the exception gives a batch where every
candidate after the first reports an execution error, which looks like a
network problem and silently turns a 96% rejection rate into "mostly errors".
