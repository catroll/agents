# A todo list nobody updates is a false progress report

**Signal.** The owner asks why the task panel still says "1 进行中，6 待处理"
after the turn that created it finished, tested and committed everything. The
entries were all real; only the panel was stale, because `todo_write` was called
once at the start of the turn and never again.

**Why it matters more than it looks.** The panel is the only progress signal the
owner sees while the turn runs. A list frozen at its opening snapshot claims work
is unstarted that has already shipped, and it sends them looking for a stuck job
that does not exist — in this case the first hypothesis was a wedged app queue
(no Redis listener, no such counter in the console: it was the agent's own list).

**Check.** Treat `todo_write` as paired calls: one to open the plan, and one final
call before the closing reply in which **nothing** is `in_progress` or `pending`.
If the turn used a plan at all, the last state must describe the turn as it
actually ended. Flip each item to `completed` when its work lands, not in one
batch at the end, so the panel stays true while it is being watched.

**Distinguish it from a real queue before investigating.** Asked about "进行中"
counts, confirm whose counter it is: an app-side job queue has a listener, a
table or a log behind it, and the number can be reproduced from one of them; a
stale plan has neither, and its counts match the number of items the agent wrote
down. One `grep` for the exact label and one `ss -ltn` settle which is which
before any debugging starts.
