# A green test turns red because a hand-written double lacks a new method

Signal: `AttributeError: '_StubIndex' object has no attribute 'search_many'`
raised from production code *inside* a test, for a test file nobody edited.
Both failures were reported as assertion failures (`assert 'not evidence' in
"ERROR: AttributeError: ..."`), so the reason was one traceback away while the
test summary looked like a behaviour regression.

## What happened

`winnie-assistant`'s `_search_documents` was changed to call
`IndexClient.search_many` (several phrasings merged into one result). The
tests' `_StubIndex` in `apps/api/tests/test_assistant_recall.py` still only had
`search()`. `ToolBox.execute` catches every exception from a tool and returns
`"ERROR: ..."` to the model, so the stub's missing method surfaced as wrong
assertions instead of a crash:

    ERROR: AttributeError: '_StubIndex' object has no attribute 'search_many'

Nothing in the diff touched the test or the tool, so `git blame` leads nowhere:
the StubIndex already described an interface the production code had stopped
using.

## The check

When a client class gains a method, grep the tests for the doubles that
implement that class *by hand*:

    grep -rn "class _.*Stub\|class _.*Fake" apps/api/tests packages/*/tests

Mirror the real method's semantics in the double, not just the name. Here
`search_many` merges hits by `(path, start_line)` and caps the merge, which is
exactly what the two tests assert about; a stub returning `self.hits` unchanged
would have made them pass while testing nothing.

Prefer a shared fake over per-file stubs when the interface is more than one or
two methods: a single class is one place to update.

## Negative result

Do not "fix" this by making the tool tolerate the missing method — catching
`AttributeError` in `_search_documents` would hide a real broken index client
behind a soft error string. The double is wrong, not the caller.
